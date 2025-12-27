from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # TODO: give permission to the admin by check request.user.role.permissions
        User = get_user_model()

        is_admin = User.objects.filter(pk=request.user.pk, role__name='Admin').exists()

        return is_admin


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff
