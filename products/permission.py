from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        if request.user.role.name == "Admin":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        print("fuck", request.user.role.name)
        if request.user.role.name == "Admin":
            return True

        return False
