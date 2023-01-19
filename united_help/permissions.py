from rest_framework import permissions
from united_help.models import User, Profile


class IsReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class IsCreateOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.method == 'POST'


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.admin).exists()


class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.organizer).exists()


class IsVolunteer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.volunteer).exists()


class IsRefugee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.refugee).exists()


class IsOwnerOrReadOnly(IsReadOnly, IsOwner):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsOwner).has_object_permission(request, view, obj))


class IsCreateOrReadOnly(IsReadOnly, IsCreateOnly):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsCreateOnly).has_object_permission(request, view, obj))


class IsOwnerOrCreateOnly(IsCreateOnly, IsOwner):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new.
    """
    def has_object_permission(self, request, view, obj):
        return (super(IsCreateOnly).has_object_permission(request, view, obj) or
                super(IsOwner).has_object_permission(request, view, obj))


class IsAdminOrOwnerOrCreateOnly(IsOwnerOrCreateOnly, IsAdmin):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new.
    """
    def has_object_permission(self, request, view, obj):
        return (super(IsOwnerOrCreateOnly).has_object_permission(request, view, obj) or
                super(IsAdmin).has_object_permission(request, view, obj))


class IsAuthenticatedOrCreateOnly(IsCreateOrReadOnly):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new and authenticated to view.
    """
    def has_object_permission(self, request, view, obj):
        if super(IsCreateOrReadOnly).has_object_permission(request, view, obj):
            return True
        return obj.owner == request.user


class IsAdminOrReadOnly(IsAdmin, IsReadOnly):
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsAdmin).has_object_permission(request, view, obj))


class IsOrganizerOrReadOnly(IsOrganizer, IsReadOnly):
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsOrganizer).has_object_permission(request, view, obj))


class IsVolunteerOrReadOnly(IsVolunteer, IsReadOnly):
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsVolunteer).has_object_permission(request, view, obj))


class IsVolunteerOrRefugee(IsVolunteer, IsRefugee):
    def has_object_permission(self, request, view, obj):
        return (super(IsVolunteer).has_object_permission(request, view, obj) or
                super(IsRefugee).has_object_permission(request, view, obj))


class IsRefugeeOrReadOnly(IsRefugee, IsReadOnly):
    def has_object_permission(self, request, view, obj):
        return (super(IsReadOnly).has_object_permission(request, view, obj) or
                super(IsRefugee).has_object_permission(request, view, obj))
