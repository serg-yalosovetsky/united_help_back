from contextlib import suppress
from django.core.serializers import serialize
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.generics import ListCreateAPIView
from rest_framework import permissions, viewsets
from rest_framework_swagger.views import get_swagger_view

from united_help.serializers import *
from united_help.models import *


class EventsView(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    queryset = Event.objects.all()

    def get(self, request, *args, **kwargs):
        print('get')
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        print('\n\n')
        print(request.user)
        print('\n\n')
        return super().post(request, *args, **kwargs)
    

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    

class CityView(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    queryset = City.objects.all()
    

class CommentView(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    

class SkillView(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    queryset = Skill.objects.all()
    