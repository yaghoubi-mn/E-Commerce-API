from rest_framework.permissions import BasePermission

class HavePermission(BasePermission):
    """
    Custom permission to check if the user has the required permission in their role.
    """
    def has_permission(self, request, view):
        required_permission = 'edit_addresses'
        user = request.user
        if not user or not user.is_authenticated:
            return False
        
        # Check if the user has a role and if the role has the required permission
        if user.role and hasattr(user.role, 'permissions'):
            if isinstance(user.role.permissions, dict):
                return user.role.permissions.get(required_permission, False)
        return False