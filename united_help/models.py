from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User as DjangoUser


class User(DjangoUser):
    # name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    phone = PhoneNumberField(null=True, blank=True, unique=False)
    nickname = models.CharField(max_length=255, null=True, blank=True,)
    telegram_phone = PhoneNumberField(null=True, blank=True, unique=False)
    viber_phone = PhoneNumberField(null=True, blank=True, unique=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    firebase_tokens = models.TextField(default='')
    following = models.ManyToManyField('Profile', related_name='following', blank=True)

    def __repr__(self):
        return f'User_{self.pk} {self.username}'

    def __str__(self):
        return repr(self)


class Profile(models.Model):

    class Roles(models.IntegerChoices):
        admin = 0
        volunteer = 1
        organizer = 2
        refugee = 30

    user = models.ForeignKey('User', verbose_name='User', on_delete=models.CASCADE)
    role = models.IntegerField(choices=Roles.choices)
    rating = models.FloatField(default=0)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True,)
    skills = models.ManyToManyField('Skill', related_name='user_skills', blank=True)
    description = models.TextField(null=True, blank=True,)
    url = models.TextField(null=True, blank=True,)
    organization = models.TextField(null=True, blank=True,)

    def __repr__(self):
        return f'<Profile: {self.user} {self.role}>'

    def __str__(self):
        return repr(self)


class City(models.Model):
    city = models.CharField(max_length=255)
    alias = models.TextField()

    def __repr__(self):
        return f'City {self.city}'

    def __str__(self):
        return repr(self)


class Event(models.Model):

    class Employments(models.IntegerChoices):
        full = 0
        part = 1
        one_time = 2

    class Roles(models.IntegerChoices):
        volunteer = 1
        refugee = 3

    enabled = models.BooleanField(default=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    reg_date = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True,)
    city = models.ForeignKey('City', verbose_name='City', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    employment = models.IntegerField(choices=Employments.choices)
    owner = models.ForeignKey('Profile', verbose_name='Owner', on_delete=models.CASCADE)
    to = models.IntegerField(choices=Roles.choices, default=Roles.volunteer)
    participants = models.ManyToManyField('Profile', related_name='user_profiles', blank=True)
    skills = models.ManyToManyField('Skill', related_name='required_skills', blank=True)
    required_members = models.IntegerField()
    # TODO user can subscribe to organizer profile

    def __repr__(self):
        return f'Event_{self.id} {self.name}'

    def __str__(self):
        return repr(self)


class Voting(models.Model):
    voter = models.ForeignKey('User', verbose_name='User', on_delete=models.CASCADE)
    applicant = models.ForeignKey('Profile', verbose_name='Profile', on_delete=models.CASCADE)
    event = models.ForeignKey('Event', verbose_name='Event', on_delete=models.CASCADE,)
    score = models.IntegerField(default=0)

    def __repr__(self):
        return f'<Vote: {self.voter} to {self.applicant} in {self.event} {self.score}>'

    def __str__(self):
        return repr(self)



class Skill(models.Model):
    name = models.CharField(max_length=255)
    # description = models.TextField()
    parents = models.ManyToManyField('self', blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True,)

    def __repr__(self):
        return f'Skill {self.name}'

    def __str__(self):
        return repr(self)



class EventLog(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    volunteers_subscribed = models.ManyToManyField('Profile', related_name='profiles_subscribed', blank=True)
    volunteers_attended = models.ManyToManyField('Profile', related_name='profiles_attended', blank=True)
    happened = models.BooleanField(default=True)
    log_date = models.DateTimeField(auto_now_add=True)

    def __repr__(self):
        return f'EventLog_{self.id} {self.event}'

    def __str__(self):
        return repr(self)


class Comment(models.Model):
    event = models.ForeignKey('Event', verbose_name='Event', on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name='User', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()

    def __repr__(self):
        return f'Comment{self.id} {self.text} on {self.event}'

    def __str__(self):
        return repr(self)