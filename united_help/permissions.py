from rest_framework import permissions
from united_help.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsOwnerOrCreateOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        if hasattr(obj, 'owner'):
            return obj.owner.id == request.user.id
        if hasattr(obj, 'user'):
            return obj.user.id == request.user.id
        return True


class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new and authenticated to view.
    """
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        if bool(
            request.method in permissions.SAFE_METHODS or
            request.user and request.user.is_authenticated
        ):
            return True
        return obj.owner == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=0).exists()


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile_set.filter(role=0).exists()


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.profile_set.filter(role=2).exists()


class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile_set.filter(role=2).exists()


class IsVolunteerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.profile_set.filter(role=1).exists()


class IsVolunteer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile_set.filter(role=1).exists()


class IsRefugeeOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.profile_set.filter(role=3).exists()


class IsRefugee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.profile_set.filter(role=3).exists()
