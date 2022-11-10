from django.contrib import admin
from .models import User, Profile, Event, Skill, City, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', "name", "enabled", 'city', 'owner')
    list_display_links = ('id', "name", "enabled",)
    search_fields = ["name", 'description', 'skills', ]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', "name", "parents",)
    list_display_links = ('id', "name",)
    search_fields = ["name", ]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('id', "city", "alias",)
    list_display_links = ('id', "city",)
    search_fields = ["city", "alias", ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', "event", "user",)
    list_display_links = ('id', "event",)



