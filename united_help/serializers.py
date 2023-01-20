import datetime

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from united_help.models import Event, User, City, Skill, Profile, Comment, EventLog, Voting
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions


class ProfileSerializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField()

    def get_is_subscribe(self, obj):
        if request := self.context.get('request'):
            user = User.objects.get(id=request.user.id)
            if user.following.filter(id=obj.id).exists():
                return True
            else:
                return False
        return None

    def validate_role(self, value):
        """
        Check only admin can create admins.
        """
        if request := self.context.get('request'):
            user = User.objects.get(id=request.user.id)

            if self.context.get('request').method.lower() == 'post' and user.profile_set.filter(role=value).exists():
                raise serializers.ValidationError(f"You already have role {Profile.Roles.choices[value][1]}")
            if value == Profile.Roles.admin:
                if not user.profile_set.filter(role=Profile.Roles.admin).exists():
                    raise serializers.ValidationError("You does not have permission to create admin or organizers")

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'rating', 'active', 'is_subscribe',
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
    is_online = serializers.SerializerMethodField()

    def get_is_online(self, obj):
        datetime_diff = datetime.datetime.now() - obj.last_login.replace(tzinfo=None)
        is_online = datetime_diff.seconds < 5 * 60
        return is_online

    class Meta:
        model = User
        fields = ('id', 'active', 'username', 'phone',
                  'nickname', 'telegram_phone', 'viber_phone',
                  'email', 'last_login', 'is_online',
                  )
        read_only_fields = ('id', 'reg_date', 'last_login', 'active', 'is_online',)


class ContactGetSerializer(serializers.ModelSerializer):
    user = UserGetSerializer()

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'active', 'image',)
        read_only_fields = ('id', 'user', 'role', 'active', 'image',)


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
    image = Base64ImageField()
    is_subscribe = serializers.SerializerMethodField()

    def get_is_subscribe(self, obj):
        if request := self.context.get('request'):
            user = User.objects.get(id=request.user.id)
            participant = Profile.objects.filter(user=user, role=obj.to)
            is_participant = participant.exists() and participant.first() in obj.participants.all()
            if is_participant:
                return True
            else:
                return False
        return None


    class Meta:
        model = Event
        fields = ('id', 'active', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills', 'to',
                  'required_members', 'is_subscribe',
                  )
        read_only_fields = ('id', 'owner', 'reg_date')


class EventSubscribeSerializer(serializers.ModelSerializer):
    subscribed_members = serializers.SerializerMethodField()

    def get_subscribed_members(self, obj):
        return obj.participants.count()

    class Meta:
        model = Event
        read_only_fields = ('id', 'active', 'name', 'description', 'reg_date',
                            'start_time', 'end_time', 'image', 'city', 'location',
                            'employment', 'owner', 'participants', 'skills',
                            'subscribed_members', 'required_members', 'to',)
        fields = ('id', 'active', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills',
                  'subscribed_members', 'required_members', 'to',)


class EventFinishedSerializer(serializers.ModelSerializer):
    subscribed_members = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_subscribed_members(self, obj):
        return obj.participants.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_rating(self, obj):
        profile = obj.owner
        votes: list[Voting] = Voting.objects.filter(applicant=profile)
        votes_sum = 0
        for vote in votes:
            votes_sum += vote.score
        if votes.count() == 0:
            return 0
        else:
            return votes_sum / votes.count()

    class Meta:
        model = Event
        read_only_fields = ('id', 'active', 'name', 'description', 'reg_date',
                            'start_time', 'end_time', 'image', 'city', 'location',
                            'employment', 'owner', 'participants', 'skills',
                            'subscribed_members', 'required_members', 'to',
                            'comments_count', 'rating',
                            )
        fields = ('id', 'active', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills',
                  'subscribed_members', 'required_members', 'to',
                  'comments_count', 'rating',
                  )


class FinishEventSerializer(serializers.ModelSerializer):
    volunteers_attended = serializers.ListSerializer(child=serializers.IntegerField(), write_only=True)
    message = serializers.CharField()

    def update(self, validated_data, instance):
        updated_fields = []
        many_to_many_fields = ['volunteers_attended', ]
        # instance = EventLog._default_manager.create(**validated_data)
        print(0)
        for field in validated_data.keys():
            print(1)
            value = validated_data[field]
            print(2)
            if field in many_to_many_fields:
                print(3)
                if value == -1:
                    print(4)
                    getattr(instance, field).set(*instance.volunteers_subscribed.all())
                else:
                    print(5)
                    volunteers = Profile.objects.filter(pk__in=value)
                    getattr(instance, field).set(volunteers)
            else:
                print(6)
                setattr(instance, field, value)
                updated_fields.append(field)

        print(7)
        instance.save(update_fields=updated_fields)
        return instance

    def create(self, validated_data):
        updated_fields = []
        many_to_many_fields = ['volunteers_attended', ]
        print(0)
        instance = EventLog._default_manager.create(**validated_data)
        print(0)
        for field in validated_data.keys():
            print(1)
            value = validated_data[field]
            print(2)
            if field in many_to_many_fields:
                print(3)
                if value == -1:
                    print(4)
                    getattr(instance, field).set(*instance.volunteers_subscribed.all())
                else:
                    print(5)
                    volunteers = Profile.objects.filter(pk__in=value)
                    getattr(instance, field).set(volunteers)
            else:
                print(6)
                setattr(instance, field, value)
                updated_fields.append(field)

        print(7)
        instance.save(update_fields=updated_fields)
        return instance

    class Meta:
        model = Event
        read_only_fields = ('id', 'active', 'name', 'description', 'reg_date',
                            'start_time', 'end_time', 'image', 'city', 'location',
                            'employment', 'owner', 'participants', 'skills', 'to',
                            'required_members',)
        fields = ('id', 'active', 'name', 'description', 'reg_date',
                  'start_time', 'end_time', 'image', 'city', 'location',
                  'employment', 'owner', 'participants', 'skills', 'to',
                  'required_members', 'volunteers_attended')


class VotingSerializer(serializers.ModelSerializer):

    def validate(self, data):
        voter = self.context['request'].user

        event = Event.objects.filter(id=data['event'])
        if not event.exists():
            raise serializers.ValidationError(f'You are not a {event.to.name}!')
        event: Event = event.first()

        participant = Profile.objects.filter(user=voter, role=event.to)
        owner = Profile.objects.filter(user=voter, role=Profile.Roles.organizer)
        is_owner = owner.exists() and owner.first().id == event.owner.id
        is_participant = participant.exists() and participant.first() in event.participants.all()
        if not is_participant or is_owner:
            raise serializers.ValidationError(f'You are not a owner or participant of {event.name}!')

        applicant: Profile = Profile.objects.filter(id=data['applicant']).first()
        vote = Voting.objects.filter(voter=voter, applicant=applicant, event=event)

        if vote.exists():
            raise serializers.ValidationError(f'You are already rate {applicant.user.username} in event {event.name}!')

        return data

    class Meta:
        model = Voting
        fields = ('id', 'voter', 'applicant', 'event', 'score',)
        read_only_fields = ('id', 'voter',)


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
        if value > 5 or value < 0.5:
            raise serializers.ValidationError("You rate with invalid scores")
        return value

    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'scores', 'rating',
                  )
        read_only_fields = ('id', 'user', 'role', 'rating',)


class CommentSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = Comment
        fields = ('id', 'event', 'user', 'parent', 'text', 'score',)
        read_only_fields = ('id', 'user',)


class ProfileSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'role', 'rating', 'active',
                  'image', 'skills', 'description', 'url', 'organization',
                  )
        read_only_fields = ('id', 'user', 'rating', 'active',)


class UserAddFirebaseTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class CancelEventSerializer(serializers.Serializer):
    message = serializers.CharField()


class UserCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    image = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        user: User = obj.user
        profiles: list[Profile] = user.profile_set
        profile = profiles.filter(role=obj.event.to)
        if profile.exists():
            return request.build_absolute_uri(profile.first().image.url)
        images = []
        for role in [Profile.Roles.volunteer, Profile.Roles.refugee,
                     Profile.Roles.organizer, Profile.Roles.admin]:
            if profiles.filter(role=role).exists():
                images.append(profiles.filter(role=role).first().image)
        return request.build_absolute_uri(images[0].url) if images else None

    def get_rating(self, obj):
        profile = obj.event.owner
        votes = Voting.objects.filter(applicant=profile, voting=obj.user)
        return votes.first().scores if votes.exists() else None

    class Meta:

        model = Comment
        fields = ('id', 'event', 'user', 'parent', 'text', 'image', 'rating',)
        read_only_fields = ('id', 'user')
