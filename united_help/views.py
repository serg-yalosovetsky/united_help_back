import datetime
from contextlib import suppress
from datetime import datetime as dt

from django.http import Http404
from rest_framework import permissions, viewsets, status
from rest_framework.generics import UpdateAPIView, GenericAPIView, get_object_or_404, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from united_help.helpers import str_to_bool, index_in_list, DATETIME_FORMAT
from united_help.permissions import IsOrganizerOrReadOnly, IsOwnerOrCreateOnly, IsAdminOrReadOnly, \
    IsAuthenticatedOrCreateOnly, IsAdmin, IsVolunteer, IsAdminOrOwnerOrCreateOnly, IsOrganizer
from united_help.serializers import *
from united_help.models import *


class EventsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
    serializer_class = EventSerializer

    def event_filters(self, queryset):
        enabled = self.request.query_params.get('enabled')
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

        if (bool_enabled := str_to_bool(enabled)) is not None:
            queryset = queryset.filter(enabled=bool_enabled)
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
            serializer.save()
        else:
            raise Http404('you are no organizer')

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

        if volunteers_only is not None and refugees_only is not None:
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

    def get_queryset(self,):
        event_id = self.kwargs.get('pk')
        print(f'{event_id=}')
        event = get_object_or_404(Event.objects.all(), pk=event_id)
        return Comment.objects.filter(event=event)


class UserCommentsEventView(ListAPIView):
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

    def get_queryset(self,):
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
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        if event.participants.all().count() < event.required_members:
            profiles = Profile.objects.filter(active=True, user=request.user)
            user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
            if user_volunteer_profile.exists():
                event.participants.add(user_volunteer_profile.first())
                message = f'You subscribed to event {event}'
                status_code = 200
            else:
                message = f'You are not a volunteer'
                status_code = 403
        else:
            message = f'There are no more job for you on this event {event}'
            status_code = 404
        return Response(message, status=status_code)


class EventUnsubscribeView(EventSubscribeView):
    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
        if user_volunteer_profile.exists():
            if event.participants.filter(id=user_volunteer_profile.first().id).exists():
                event.participants.remove(user_volunteer_profile.first())
                message = f'You unsubscribed to event {event}'
                status_code = 204
            else:
                message = f'You has not subscription to event {event}'
                status_code = 404
        else:
            message = f'You are not a volunteer'
            status_code = 403
        return Response(message, status=status_code)


class FinishEventView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]
    serializer_class = FinishEventSerializer

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if not event.enabled:
                message = f'You are already finished {event}'
                status_code = 404
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
                    event.enabled = False
                    event.save()
                message = f'You are finished {event} with {eventlog} in {eventlog.log_date}'
                status_code = 200
        else:
            message = f'You are not a organizer owner'
            status_code = 403
        return Response(message, status=status_code)


class CancelEventView(EventSubscribeView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def post(self, request, *args, **kwargs):
        event_id = kwargs.pop('pk')
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if not event.enabled:
                message = f'You are already canceled {event}'
                status_code = 404

            else:
                volunteers_attended = []
                eventlog = EventLog(event=event,
                                    happened=True)
                eventlog.save()
                eventlog.volunteers_attended.add(*volunteers_attended)
                eventlog.volunteers_subscribed.add(*event.participants.all())
                event.enabled = False
                event.save()
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
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        profiles = Profile.objects.filter(active=True, user=request.user)
        owner_profile = profiles.filter(role=Profile.Roles.organizer)
        if owner_profile.exists() and event.owner == owner_profile.first():
            if event.enabled:
                message = f'You are already activated {event}'
                status_code = 404
            else:
                event.enabled = True
                event.save()
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

    def get(self, request, *args, **kwargs):
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


class MeUserProfileView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
    queryset = Profile.objects.all()

    def retrieve(self, request, *args, **kwargs):
        profile_type = kwargs.get('pk')
        user = self.request.user
        profile = Profile.objects.filter(user=user, role=profile_type).first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    def get_queryset(self):
        profiles = self.queryset.filter(active=True, user=self.request.user)
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
    
    def update(self, request, *args, **kwargs):
        super(ProfileView, self).update()


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
            # TODO ???????????????? ?????????????????? ?????????????? ?????? ????????????????
            # TODO ?? ?????? ???????????? ???????? ???????????? ?????????? ???????? ???? ?????????? ?????????????? ????????????????????????, ?? ????????????????
        profile.rating = profile.scores / profile.users_voted
        return profile


class CityView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = CitySerializer
    queryset = City.objects.all()


class CommentView(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class SkillView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
