import json
from contextlib import suppress
from datetime import datetime as dt

from django.http import Http404, HttpResponseBadRequest
from rest_framework import permissions, viewsets, status
from rest_framework.generics import UpdateAPIView, GenericAPIView, get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from united_help.helpers import str_to_bool, index_in_list, DATETIME_FORMAT
from united_help.permissions import IsOrganizerOrReadOnly, IsAdminOrReadOnly, \
    IsAuthenticatedOrCreateOnly, IsAdmin, IsVolunteer, IsAdminOrOwnerOrCreateOnly, IsOrganizer, IsVolunteerOrRefugee
from united_help.serializers import *
from united_help.models import *
from united_help.services import send_firebase_multiple_messages, get_fine_location


class EventsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        for event in queryset:
            if not event.location_lat or not event.location_lon:
                lat, lon, name = get_fine_location(event.location)
                event.location_lat = lat
                event.location_lon = lon
                event.location_display = name
                event.save()

        return super().list(request, *args, **kwargs)

    def event_filters(self, queryset):
        active = self.request.query_params.get('active')
        name = self.request.query_params.get('name')
        employment = self.request.query_params.get('employment')
        city = self.request.query_params.get('city')
        skills = [self.request.query_params.get(f'skill')]
        skills_inclusive = self.request.query_params.get(f'skills_inclusive')
        search_in_description = self.request.query_params.get(f'search_in_description')
        start_time = self.request.query_params.get(f'start_time')
        end_time = self.request.query_params.get(f'end_time')

        for i in range(10):
            skills.append(self.request.query_params.get(f'skill{i}'))
        skill_objs = []
        for skill in skills:
            if skill:
                if (skill_obj := Skill.objects.filter(name=skill)).exists():
                    skill_objs.append(skill_obj.first())

        if (bool_active := str_to_bool(active)) is not None:
            queryset = queryset.filter(active=bool_active)
        if name:
            if str_to_bool(search_in_description):
                queryset = queryset.filter(Q(name__contains=name) | Q(description__contains=name))
            else:
                queryset = queryset.filter(name__contains=name)
        if employment:
            employment_int = index_in_list(Event.Employments.names, employment)
            if employment_int > 0:
                queryset = queryset.filter(employment=employment_int)
        if city:
            queryset = queryset.filter(city__alias__contains=city)
        if skill_objs:
            if str_to_bool(skills_inclusive):
                queryset = queryset.filter(skills__contains=skills)
            else:
                queryset = queryset.filter(skills__in=skills)
        if start_time:
            with suppress(ValueError):
                start_time_dt = dt.strptime(start_time, DATETIME_FORMAT)
                queryset = queryset.filter(start_time__gte=start_time_dt)
        if end_time:
            with suppress(ValueError):
                end_time_dt = dt.strptime(end_time, DATETIME_FORMAT)
                queryset = queryset.filter(start_time__lte=end_time_dt)
        return queryset

    def get_queryset(self):
        queryset = Event.objects.all()
        return self.event_filters(queryset)

    def perform_create(self, serializer):
        print(f'{serializer.validated_data=}')
        profiles = Profile.objects.filter(active=True, user=self.request.user)
        user_organizer_profile = profiles.filter(role=Profile.Roles.organizer)
        if user_organizer_profile.exists():
            serializer.validated_data['owner'] = user_organizer_profile.first()
            if (not serializer.validated_data['location_lat'] or
                    not serializer.validated_data['location_lon']):
                lat, lon, name = get_fine_location(serializer.validated_data['location'])
                serializer.validated_data['location_lat'] = lat
                serializer.validated_data['location_lon'] = lon
                serializer.validated_data['location_display'] = name
            event = serializer.save()
            if event.owner_profile.following.exists():
                send_firebase_multiple_messages(
                    f'Organizer has created event {event.name}',
                    f'Organizer {event.owner.user.username} has created event {event.name}',
                    event.owner_profile.following.all(),
                    image=event.image,
                    notify_type='create',
                    to_profile=event.to.name,
                    event_id=event.id,
                    event_to=Profile.Roles.labels[event.to].capitalize(),
                    event_name=event.name,
                    actor_name=event.owner.user.username,
                    actor_profile_id=event.owner.id,
                )
        else:
            raise Http404('you are no organizer')

    def update(self, request, *args, **kwargs):
        is_same = True  # check if event is changed

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        initial_serializer = self.get_serializer(instance, data=request.data, partial=partial)
        initial_serializer.is_valid(raise_exception=True)
        data = initial_serializer.data
        event_id = self.kwargs.get('pk')
        event = Event.objects.get(id=event_id)
        instance_serializer = self.get_serializer(event)
        instance_data = instance_serializer.data

        if (data['location'] != instance_data['location']):
            lat, lon, name = get_fine_location(serializer.validated_data['location'])
            serializer.validated_data['location_lat'] = lat
            serializer.validated_data['location_lon'] = lon
            serializer.validated_data['location_display'] = name

        update_items = {}
        # update_items_push = {}
        for k in data:
            if data[k] != instance_data[k]:
                is_same = False
                update_items[k] = data[k]
                # update_items_push[f'msgkey_{k}'] = data[k]

        if not is_same:
            send_firebase_multiple_messages(
                f'Organizer {event.owner.user.username} changed івент {event.name}.',
                f'{[f"{k} is {v}" for k, v in update_items.items()]}',
                [participant.user for participant in event.participants],
                notify_type='change',
                to_profile=event.to.name,
                event_id=event_id,
                image=request.build_absolute_uri(event.image.url),
                event_name=event.name,
                actor_name=event.owner.user.username,
                actor_profile_id=event.owner.id,
                # **update_items_push,
                _data=json.dumps(update_items),
            )

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class EventsSubscribedView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteer]
    serializer_class = EventSubscribeSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        profiles = Profile.objects.filter(active=True, user=self.request.user)
        user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
        if user_volunteer_profile.exists():
            events = self.queryset.filter(participants__in=user_volunteer_profile)

            return events
        return self.queryset.filter(id=-1)


class EventsAttendedView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteer]
    serializer_class = EventSubscribeSerializer
    queryset = EventLog.objects.all()

    def get_queryset(self):
        profiles = Profile.objects.filter(active=True, user=self.request.user)
        user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
        if user_volunteer_profile.exists():
            event_logs = self.queryset.filter(volunteers_attended__in=user_volunteer_profile, happened=True)
            event_ids = list(set(event_logs.values_list('event_id')))
            event_ids = [i[0] for i in event_ids]
            events = Event.objects.filter(pk__in=event_ids)
            return events
        return self.queryset.filter(id=-1)


class EventsCreatedView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = EventSubscribeSerializer
    queryset = Event.objects.all()

    def get_queryset(self):
        profiles = Profile.objects.filter(active=True, user=self.request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists():
            events = self.queryset.filter(owner=owner_profile.first())
            return events
        return self.queryset.filter(id=-1)


class EventsFinishedView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = EventFinishedSerializer
    queryset = EventLog.objects.all()

    def get_queryset(self):
        profiles = Profile.objects.filter(active=True, user=self.request.user)
        user_organizeer_profile = profiles.filter(role=Profile.Roles.organizer)
        if user_organizeer_profile.exists():
            event_logs = self.queryset.filter(event__owner=user_organizeer_profile.first(), happened=True)
            event_ids = list(set(event_logs.values_list('event_id')))
            event_ids = [i[0] for i in event_ids]
            events = Event.objects.filter(pk__in=event_ids)
            return events
        return self.queryset.filter(id=-1)


class ContactsView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = ContactGetSerializer
    queryset = Profile.objects.all()

    def get(self, request, *args, **kwargs):
        volunteers_only = self.request.query_params.get('volunteers')
        refugees_only = self.request.query_params.get('refugees')
        event_id: str = self.request.query_params.get('event_id')

        if event_id is not None and event_id and event_id.isdigit():
            event_id: int = int(event_id)
            event = get_object_or_404(Event, id=event_id)
            types = [event.to]
        elif volunteers_only is not None and refugees_only is not None:
            types = [Profile.Roles.volunteer, Profile.Roles.refugee]
        elif volunteers_only is not None:
            types = [Profile.Roles.volunteer]
        elif refugees_only is not None:
            types = [Profile.Roles.refugee]
        else:
            types = [Profile.Roles.volunteer, Profile.Roles.refugee]

        user_organizeer_profile = Profile.objects.filter(role=Profile.Roles.organizer)

        volunteers = set()
        refugees = set()
        if user_organizeer_profile.exists():
            if isinstance(event_id, int):
                if event.to == Profile.Roles.volunteer:
                    volunteers = set(list(event.participants.all()))
                else:
                    refugees = set(list(event.participants.all()))
            else:
                events = Event.objects.filter(owner=user_organizeer_profile.first())
                for event in events:
                    if event.to == Profile.Roles.volunteer and Profile.Roles.volunteer in types:
                        for participant in event.participants.all():
                            volunteers.add(participant)
                    if event.to == Profile.Roles.refugee and Profile.Roles.refugee in types:
                        for participant in event.participants.all():
                            refugees.add(participant)
        else:
            raise Http404

        contacts = {}
        if Profile.Roles.refugee in types:
            contacts['refugees'] = list(refugees)
        if Profile.Roles.volunteer in types:
            contacts['volunteers'] = list(volunteers)

        data = {}

        for type_, list_ in contacts.items():
            page = self.paginate_queryset(list_)

            if page is not None:
                serializer = self.get_serializer(page, many=True, context={"request": request})
            else:
                serializer = self.get_serializer(list_, many=True, context={"request": request})
            data[type_] = serializer.data
        return Response(data)


class CommentsEventView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = CommentSerializer
    lookup_field = 'pk'

    def get_queryset(self, ):
        event_id = self.kwargs.get('pk')
        print(f'{event_id=}')
        event = get_object_or_404(Event.objects.all(), pk=event_id)
        return Comment.objects.filter(event=event)


class UserAddFirebaseTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserAddFirebaseTokenSerializer

    def post(self, request):
        serializer: serializers.Serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        token = validated_data['token']

        if token:
            user = User.objects.get(id=request.user.id)
            firebase_tokens = user.firebase_tokens
            if firebase_tokens:
                firebase_tokens = set(user.firebase_tokens.split())
            else:
                firebase_tokens = set()
            firebase_tokens.add(token)
            new_tokens = ' '.join(list(firebase_tokens))
            print(f'{firebase_tokens=}')
            user.firebase_tokens = new_tokens
            print(f'{new_tokens=}')
            user.save()

            print(f'{user.firebase_tokens=}')

            message = f'You added new firebase token'
            status_code = 200
        else:
            message = f'This is invalid firebase token'
            status_code = 400
        return Response(message, status=status_code)


class UserCommentsEventView(ListAPIView):
    # return comments with user who created this comment
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserCommentSerializer
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    def get_queryset(self, ):
        event_id = self.kwargs.get('pk')
        print(f'{event_id=}')
        event = get_object_or_404(Event.objects.all(), pk=event_id)
        return Comment.objects.filter(event=event)


class EventSubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteer]
    serializer_class = EventSubscribeSerializer
    queryset = Event.objects.all()

    def post(self, request, *args, **kwargs):
        event_id = int(kwargs.pop('pk'))
        event = get_object_or_404(Event.objects.filter(active=True), pk=event_id)
        if event.participants.all().count() < event.required_members:
            profiles = Profile.objects.filter(active=True, user=request.user)
            user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
            if user_volunteer_profile.exists():
                event.participants.add(user_volunteer_profile.first())
                event_to: str = Profile.Roles.labels[event.to]

                send_firebase_multiple_messages(
                    f'{event_to.capitalize()} {user_volunteer_profile.first().user.username} приєднується до івента {event.name}.',
                    f'Набрано {event.participants.count()} з {event.required_members} {event_to}ів для допомоги в організації івента {event.name}.',
                    [event.owner.user, ],
                    notify_type='subscribe',
                    to_profile=Profile.Roles.organizer.name,
                    event_id=event_id,
                    event_to=event_to.capitalize(),
                    image=request.build_absolute_uri(user_volunteer_profile.first().image.url),
                    event_name=event.name,
                    actor_name=user_volunteer_profile.first().user.username,
                    actor_profile_id=user_volunteer_profile.first().id,
                    # participants=event.participants.count(),
                    # required=event.required_members,
                    _data=json.dumps({
                        'required': event.required_members,
                        'participants': event.participants.count(),
                    }),

                )
                message = f'You subscribed to event {event}'
                status_code = 200
            else:
                message = f'You are not a volunteer'
                status_code = 403
        else:
            message = f'There are no more job for you on this event {event}'
            status_code = 400
        return Response(message, status=status_code)


class EventUnsubscribeView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteer]

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(active=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
        if user_volunteer_profile.exists():
            if event.participants.filter(id=user_volunteer_profile.first().id).exists():
                event.participants.remove(user_volunteer_profile.first())
                send_firebase_multiple_messages(
                    f'You are lost one of volunteers in {event.name}',
                    f'Volunteer {user_volunteer_profile.first().user.username} unsubscribed to event {event.name}',
                    [event.owner.user, ],
                    image=user_volunteer_profile.first().image,
                    notify_type='subscribe',
                    to_profile=Profile.Roles.organizer.name,
                    event_id=event_id,
                    event_to=Profile.Roles.labels[event.to].capitalize(),
                    event_name=event.name,
                    actor_name=user_volunteer_profile.first().user.username,
                    actor_profile_id=user_volunteer_profile.first().id,
                )
                message = f'You unsubscribed to event {event}'
                status_code = 204
            else:
                message = f'You has not subscription to event {event}'
                status_code = 400
        else:
            message = f'You are not a volunteer'
            status_code = 403
        return Response(message, status=status_code)


class FinishEventView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = FinishEventSerializer

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(active=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if not event.active:
                message = f'You are already finished {event}'
                status_code = 400
            else:
                serializer: serializers.Serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                validated_data = serializer.validated_data
                volunteers_attended = validated_data['volunteers_attended']
                eventlog = EventLog(event=event,
                                    happened=True)
                eventlog.save()
                eventlog.volunteers_attended.add(*volunteers_attended)
                eventlog.volunteers_subscribed.add(*event.participants.all())
                if event.employment == Event.Employments.one_time:
                    event.active = False
                    event.save()
                users_to_send = (set([participant.user for participant in event.participants.all()]) |
                                 set(owner_profile.following.all()))
                send_firebase_multiple_messages(
                    f'Organizer has finished event {event.name}',
                    f'Organizer {event.owner.user.username} has finished event {event.name}',
                    list(users_to_send),
                    image=event.image,
                    notify_type='finish',
                    to_profile=event.to.name,
                    event_id=event_id,
                    event_to=Profile.Roles.labels[event.to].capitalize(),
                    event_name=event.name,
                    actor_name=event.owner.user.username,
                    actor_profile_id=event.owner.id,
                )
                message = f'You are finished {event} with {eventlog} in {eventlog.log_date}'
                status_code = 200
        else:
            message = f'You are not a organizer owner'
            status_code = 403
        return Response(message, status=status_code)


class CancelEventView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = CancelEventSerializer

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(active=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if not event.active:
                message = f'You are already canceled {event}'
                status_code = 400

            else:
                serializer: serializers.Serializer = self.serializer_class(data=request.data)
                serializer.is_valid(raise_exception=True)
                validated_data = serializer.validated_data

                volunteers_attended = []
                eventlog = EventLog(event=event,
                                    happened=True)
                eventlog.save()
                eventlog.volunteers_attended.add(*volunteers_attended)
                eventlog.volunteers_subscribed.add(*event.participants.all())
                event.active = False
                event.save()
                users_to_send = (set([participant.user for participant in event.participants.all()]) |
                                 set(owner_profile.following.all()))
                send_firebase_multiple_messages(
                    f'Organizer {event.owner.user.username} has canceled event {event.name}',
                    validated_data['message'],
                    list(users_to_send),
                    image=event.image,
                    notify_type='cancel',
                    to_profile=event.to.name,
                    event_id=event_id,
                    event_to=Profile.Roles.labels[event.to].capitalize(),
                    event_name=event.name,
                    actor_name=event.owner.user.username,
                    actor_profile_id=event.owner.id,
                )
                message = f'You are canceled {event} with {eventlog} in {eventlog.log_date}'
                status_code = 200

        else:
            message = f'You are not a organizer owner'
            status_code = 403
        return Response(message, status=status_code)


class ActivateEventView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.all(), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if event.active:
                message = f'You are already activated {event}'
                status_code = 400
            else:
                event.active = True
                event.save()
                users_to_send = (set([participant.user for participant in event.participants.all()]) |
                                 set(owner_profile.following.all()))
                set([i for i in range(1, 6)]) | set([i for i in range(3, 8)])
                send_firebase_multiple_messages(
                    f'Organizer has activated event {event.name}',
                    f'Organizer {event.owner.user.username} has activated event {event.name}',
                    list(users_to_send),
                    image=event.image,
                    notify_type='activate',
                    to_profile=event.to.name,
                    event_id=event_id,
                    event_to=Profile.Roles.labels[event.to].capitalize(),
                    event_name=event.name,
                    actor_name=event.owner.user.username,
                    actor_profile_id=event.owner.id,
                )
                message = f'You are activated {event}'
                status_code = 200
        else:
            message = f'You are not a organizer owner'
            status_code = 403
        return Response(message, status=status_code)


class UserView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrCreateOnly]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class MeUserView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserGetSerializer
    queryset = User.objects.all()

    def get(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)

    def get_queryset(self):
        return self.queryset.filter(id=self.request.user.id).first()


class MeProfilesView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_queryset(self):
        profiles = self.queryset.filter(active=True, user=self.request.user)
        return profiles


class UserProfileView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = Profile.objects.all()

    def retrieve(self, request, *args, **kwargs):
        profile_id = kwargs.get('pk')
        profile = Profile.objects.filter(id=profile_id).first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def get_queryset(self):
        profiles = self.queryset.filter(active=True)
        return profiles


class ProfileView(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options', 'trace']
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrCreateOnly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        Profile.objects.create(role=validated_data.get('role'), user=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProfileSubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteerOrRefugee]
    serializer_class = ProfileSubscribeSerializer
    queryset = Profile.objects.all()

    def post(self, request, **kwargs):
        profile_id = int(kwargs.pop('pk'))
        profile = get_object_or_404(Profile.objects.filter(active=True), pk=profile_id)
        user: User = User.objects.get(id=request.user.id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        user_volunteer_or_refugee_profile = profiles.filter(
            Q(role=Profile.Roles.refugee) | Q(role=Profile.Roles.volunteer))
        if user_volunteer_or_refugee_profile.exists():
            user.following.add(profile)
            message = f'You subscribed to organizer {profile.organization}'
            status_code = 200
        else:
            message = f'You are not a volunteer or refugee'
            status_code = 403
        return Response(message, status=status_code)


class ProfileUnsubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteerOrRefugee]
    serializer_class = ProfileSubscribeSerializer
    queryset = Profile.objects.all()

    def post(self, request, **kwargs):
        profile_id = int(kwargs.pop('pk'))
        profile = get_object_or_404(Profile.objects.filter(active=True), pk=profile_id)
        user: User = User.objects.get(id=request.user.id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        user_volunteer_or_refugee_profile = profiles.filter(
            Q(role=Profile.Roles.refugee) | Q(role=Profile.Roles.volunteer))
        if user_volunteer_or_refugee_profile.exists():
            user.following.remove(profile)
            message = f'You unsubscribed to organizer {profile.organization}'
            status_code = 204
        else:
            message = f'You are not a volunteer or refugee'
            status_code = 403
        return Response(message, status=status_code)


class ActivateProfileView(UpdateAPIView):
    http_method_names = ['post', ]
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = ActivateProfileSerializer
    queryset = Profile.objects.all()


class ChangeScoresView(GenericAPIView):
    http_method_names = ['post', ]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ActivateProfileSerializer
    queryset = Profile.objects.all()

    def update(self, validated_data):
        scores = validated_data.get('scores')
        profile_id = validated_data.get('id')
        profile = Profile.objects.get(id=profile_id)
        if scores != 0:
            profile.scores += scores
            # TODO добавить отдельную таблицу для рейтинга
            # TODO в ней должно быть записи какой юзер за какой профиль проголосовал, и значение
        profile.rating = profile.scores / profile.users_voted
        return profile


class CityView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = CitySerializer
    queryset = City.objects.all()


class SkillView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()


class CommentView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        serializer.save(user=self.request.user)
        print(f'{validated_data=}')

        event: Event = validated_data['event']
        event_to: str = Profile.Roles.labels[event.to]

        voter = self.request.user
        participant = Profile.objects.filter(user=voter, role=event.to)
        if participant.exists():
            participant = participant.first()
        is_participant = participant and participant in event.participants.all()
        if not is_participant:
            return HttpResponseBadRequest(f'You are not a owner or participant of {event.name}!')

        score: str = validated_data['score']
        if score:
            with suppress(ValueError):
                score = float(score)
        if isinstance(score, float):
            vote = Voting.objects.filter(voter=voter, applicant=event.owner, event=event)
            if vote.exists():
                return HttpResponseBadRequest(
                    f'You are already rate {event.owner.user.username} in event {event.name}!')
            Voting.objects.create(voter=voter, applicant=event.owner, event=event, score=score)

        send_firebase_multiple_messages(
            f'{event_to.capitalize()} {self.request.user.username} create a review to event {event.name}',
            validated_data['text'],
            [event.owner.user, ],
            image=participant.image,
            notify_type='review',
            to_profile=Profile.Roles.organizer.name,
            event_id=event.pk,
            event_to=Profile.Roles.labels[event.to].capitalize(),
            event_name=event.name,
            actor_name=self.request.user.username,
            actor_profile_id=participant.id,
            _data=json.dumps({'rating': validated_data['score']}),
        )


class VotingView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VotingSerializer
    queryset = Voting.objects.all()
