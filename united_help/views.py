from rest_framework import permissions, viewsets
from rest_framework.generics import UpdateAPIView, GenericAPIView

from united_help.permissions import IsOrganizerOrReadOnly, IsOwnerOrCreateOnly, IsAdminOrReadOnly, \
    IsAuthenticatedOrCreateOnly, IsAdmin
from united_help.serializers import *
from united_help.models import *


class EventsView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def update(self, request, *args, **kwargs):
        print('update')
        return super().update(request, *args, **kwargs)


class EventSubscribeView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerOrReadOnly]
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def update(self, request, *args, **kwargs):
        print('update')
        return super().update(request, *args, **kwargs)


class UserView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrCreateOnly]
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ProfileView(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'head', 'options', 'trace']
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrCreateOnly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


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
    