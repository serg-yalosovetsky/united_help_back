from rest_framework import permissions
from united_help.models import User, Profile


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


class IsAdminOrOwnerOrCreateOnly(IsOwnerOrCreateOnly):
    """
    Custom permission to only allow owners of an object to edit it and everyone creates new.
    """
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        if user.profile_set.filter(role=Profile.Roles.admin).exists():
            return True
        return super().has_object_permission(request, view, obj)


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


class IsAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.admin).exists()


class IsAdminOrReadOnly(IsAdmin):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


class IsOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.organizer).exists()


class IsOrganizerOrReadOnly(IsOrganizer):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


class IsVolunteer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.volunteer).exists()


class IsVolunteerOrReadOnly(IsVolunteer):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)


class IsRefugee(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = User.objects.get(id=request.user.id)
        return user.profile_set.filter(role=Profile.Roles.refugee).exists()


class IsRefugeeOrReadOnly(IsRefugee):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_object_permission(request, view, obj)

