from rest_framework import serializers

from united_help.models import Event, User, City, Skill, Profile, Comment
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions


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

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )
        return attrs

    def create(self, validated_data):
        user = super().create(validated_data)

        return user

    class Meta:
        model = User
        fields = ('id', 'active', 'username', 'description', 'phone',
                  'nickname', 'telegram_phone', 'viber_phone',
                  'email', 'password', 'reg_date',
                  'last_login', 'image', 'skills',
                  )
        read_only_fields = ('id', 'reg_date', 'last_login', 'active',)
        write_only_fields = ('password',)


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
        fields = ('id', 'user', 'role', 'scores', 'rating',
                  )
        read_only_fields = ('id', 'rating',)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'event', 'user', 'parent', 'text'
                  )
        read_only_fields = ('id',)

