import datetime
from contextlib import suppress
from datetime import datetime as dt

from rest_framework import permissions, viewsets, status
from rest_framework.generics import UpdateAPIView, GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q

from united_help.helpers import str_to_bool, index_in_list, DATETIME_FORMAT
from united_help.permissions import IsOrganizerOrReadOnly, IsOwnerOrCreateOnly, IsAdminOrReadOnly, \
    IsAuthenticatedOrCreateOnly, IsAdmin, IsVolunteer, IsAdminOrOwnerOrCreateOnly
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
                queryset = queryset.filter(skills_contain=skills)
            else:
                queryset = queryset.filter(skills_in=skills)
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


class EventSubscribeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsVolunteer]
    serializer_class = EventSubscribeSerializer
    queryset = Event.objects.all()

    def post(self, request, *args, **kwargs):
        event_id = int(kwargs.pop('pk'))
        event = get_object_or_404(Event.objects.filter(enabled=True), pk=event_id)
        if event.volunteers.all().count() < event.required_members:
            profiles = Profile.objects.filter(active=True, user=request.user)
            user_volunteer_profile = profiles.filter(role=Profile.Roles.volunteer)
            if user_volunteer_profile.exists():
                event.volunteers.add(user_volunteer_profile.first())
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
            if event.volunteers.filter(id=user_volunteer_profile.first().id).exists():
                event.volunteers.remove(user_volunteer_profile.first())
                message = f'You unsubscribed to event {event}'
                status_code = 204
            else:
                message = f'You has not subscription to event {event}'
                status_code = 404
        else:
            message = f'You are not a volunteer'
            status_code = 403
        return Response(message, status=status_code)


class UserView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrCreateOnly]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ProfileView(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']
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

# TODO добавить юзерам подписку на евент


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
