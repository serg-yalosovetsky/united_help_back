from rest_framework import serializers

from united_help.models import Event, User, City, Skill, Profile, Comment


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'enabled', 'name', 'description', 'reg_date', 
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'manager', 'volunteers', 'skills',
                  'required_members',
                  )
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'active', 'name', 'description', 'phone',
                  'nickname', 'telegram_phone', 'viber_phone',
                  'email', 'password', 'reg_date', 
                  'last_time_online', 'image', 'skills',
                  )
        read_only_fields = ('id',)


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'city', 'alias',
                  )
        read_only_fields = ('id',)


class SkillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Skill
        fields = ('id', 'name', 'description', 'parent',
                  )
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating'
                  )
        read_only_fields = ('id',)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'event', 'user', 'parent', 'text'
                  )
        read_only_fields = ('id',)
        
        