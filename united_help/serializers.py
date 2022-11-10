from rest_framework import serializers

from united_help.models import Event, User, City, Skill, Profile, Comment
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'volunteers', 'skills',
                  'required_members',
                  )
        read_only_fields = ('id',)


class EventSubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'volunteers', )
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

    def is_self_parent(self, instance_orig, inst, stack: list):
        if instance_orig.id == inst.id:
            return True
        if instance_orig.id in stack:
            return True
        stack.append(inst.id)
        if not inst.parents:
            return False
        else:
            for parent in inst.parents:
                return self.is_self_parent(instance_orig, parent, stack)

    def update(self, instance, validated_data: dict):
        print()
        self_parents = []
        if isinstance(parents := validated_data.get('parents'), list):
            for parent in parents:
                self_parents.append(self.is_self_parent(instance, parent, []))
            if any(self_parents):
                validated_data.pop('parents')
        return super().update(instance, validated_data)

    class Meta:
        model = Skill
        fields = ('id', 'name', 'parents',)
        read_only_fields = ('id',)


class ProfileSerializer(serializers.ModelSerializer):

    def validate_role(self, value):
        """
        Check only admin can create admins.
        """
        if request := self.context.get('request'):
            user = User.objects.get(id=request.user.id)
            if user.profile_set.filter(role=value).exists():
                raise serializers.ValidationError(f"You already have role {Profile.Roles.choices[value][1]}")
            if value == 0 or value == 2:
                if not user.profile_set.filter(role=0).exists():
                    raise serializers.ValidationError("You does not have permission to create admin or organizers")

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating', 'active',
                  )
        read_only_fields = ('id', 'rating', 'scores', 'active',)


class ActivateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating', 'active',
                  )
        read_only_fields = ('id', 'user', 'role', 'rating', 'scores',)


class ChangeScoresSerializer(serializers.ModelSerializer):
    def validate_scores(self, value):
        if value > 5 or value < -5:
            raise serializers.ValidationError("You rate with invalid scores")
        return value

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating',
                  )
        read_only_fields = ('id', 'user', 'role', 'rating',)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'event', 'user', 'parent', 'text'
                  )
        read_only_fields = ('id', 'user')

