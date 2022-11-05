from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User as DjangoUser

class User(DjangoUser):
    # name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True,)
    phone = PhoneNumberField(null=True, blank=True, unique=False)
    nickname = models.CharField(max_length=255, null=True, blank=True,)
    telegram_phone = PhoneNumberField(null=True, blank=True, unique=False)
    viber_phone = PhoneNumberField(null=True, blank=True, unique=False)
    reg_date = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True,)
    skills = models.ManyToManyField('Skill', related_name='user_skills', blank=True)


class Profile(models.Model):

    class Roles(models.IntegerChoices):
        admin = 0
        volunteer = 1
        organizer = 2
        refugee = 3

    user = models.ForeignKey('User', verbose_name='Manager', on_delete=models.CASCADE)
    role = models.IntegerField(choices=Roles.choices)
    scores = models.IntegerField()
    rating = models.FloatField()


class City(models.Model):
    city = models.CharField(max_length=255)
    alias = models.TextField()


class Skill(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)


class Event(models.Model):

    class Employments(models.IntegerChoices):
        full = 0
        part = 1
        one_time = 2

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
    manager = models.ForeignKey('Profile', verbose_name='Manager', on_delete=models.CASCADE)
    volunteers = models.ManyToManyField('Profile', related_name='user_profiles', blank=True)
    skills = models.ManyToManyField('Skill', related_name='required_skills', blank=True)
    required_members = models.IntegerField()


class Comment(models.Model):
    event = models.ForeignKey('Event', verbose_name='Event', on_delete=models.CASCADE)
    user = models.ForeignKey('User', verbose_name='User', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
