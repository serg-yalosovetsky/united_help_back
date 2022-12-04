from rest_framework import serializers

from united_help.models import Event, User, City, Skill, Profile, Comment
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions


class ProfileSerializer(serializers.ModelSerializer):

    def validate_role(self, value):
        """
        Check only admin can create admins.
        """
        if request := self.context.get('request'):
            user = User.objects.get(id=request.user.id)
            if user.profile_set.filter(role=value).exists():
                raise serializers.ValidationError(f"You already have role {Profile.Roles.choices[value][1]}")
            if value == Profile.Roles.admin:
                if not user.profile_set.filter(role=Profile.Roles.admin).exists():
                    raise serializers.ValidationError("You does not have permission to create admin or organizers")

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'rating', 'active',
                  'image', 'skills', 'description', 'url', 'organization',
                  )
        read_only_fields = ('id', 'user', 'rating', 'active',)


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
        fields = ('id', 'active', 'username', 'phone',
                  'nickname', 'telegram_phone', 'viber_phone',
                  'email', 'password', 'reg_date',
                  'last_login',
                  )
        read_only_fields = ('id', 'reg_date', 'last_login', 'active',)
        write_only_fields = ('password',)


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'active', 'username', 'phone',
                  'nickname', 'telegram_phone', 'viber_phone',
                  'email', 'reg_date',
                  'last_login',
                  )
        read_only_fields = ('id', 'reg_date', 'last_login', 'active',)


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'rating', 'active',
                  'image', 'skills', 'description', 'url', 'organization',
                  )
        read_only_fields = ('id', 'user', 'rating', 'active',)


class ActivateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating', 'active',
                  )
        read_only_fields = ('id', 'user', 'role', 'rating', 'scores',)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills', 'to',
                  'required_members',
                  )
        read_only_fields = ('id',)


class EventSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        read_only_fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                            'start_time', 'end_time', 'image', 'city', 'location',
                            'employment', 'owner', 'participants', 'skills',
                            'required_members', 'to',)
        fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills',
                  'required_members', 'to',)


class FinishEventSerializer(serializers.ModelSerializer):
    volunteers_attended = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True)

    def update(self, instance, validated_data):
        updated_fields = []
        many_to_many_fields = ['volunteers_attended', ]
        for field in validated_data.keys():
            value = validated_data[field]
            if field in many_to_many_fields:
                if value == -1:
                    getattr(instance, field).set(*instance.volunteers_subscribed.all())
                else:
                    volunteers = Profile.objects.filter(pk__in=value)
                    getattr(instance, field).set(volunteers)
            else:
                setattr(instance, field, value)
                updated_fields.append(field)

        instance.save(update_fields=updated_fields)
        return instance
    class Meta:
        model = Event
        read_only_fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                            'start_time', 'end_time', 'image', 'city', 'location',
                            'employment', 'owner', 'participants', 'skills', 'to',
                            'required_members',)
        fields = ('id', 'enabled', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills', 'to',
                  'required_members', 'volunteers_attended')



class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'city', 'alias',
                  )
        read_only_fields = ('id',)


class SkillSerializer(serializers.ModelSerializer):

    def is_self_parent(self, instance_orig, inst, stack: list):
        print(f'{instance_orig=} {inst=} {stack=}')
        if instance_orig.id == inst.id:
            return True
        if inst.id in stack:
            return True
        stack.append(inst.id)
        if not inst.parents:
            return False
        else:
            for parent in inst.parents.all():
                return self.is_self_parent(instance_orig, parent, stack)

    def update(self, instance, validated_data: dict):
        # TODO разобраться с тупой хуйней, когда при проверке зацикливания родителей какого-то
        #  хуя объект при назначении родителя становится родителем сам для своего родителя
        # self_parents = []
        # if isinstance(parents := validated_data.get('parents'), list):
        #     for parent in parents:
        #         self_parent = self.is_self_parent(instance, parent, [instance.id])
        #         if self_parent:
        #             validated_data.pop('parents')
        #             break
        return super().update(instance, validated_data)

    class Meta:
        model = Skill
        fields = ('id', 'name', 'parents',)
        read_only_fields = ('id',)


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
