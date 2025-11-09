import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role


@pytest.mark.django_db
class TestChangePassword:
    def setup_method(self):
        self.client = APIClient()
        self.change_password_url = reverse("change_password")
        self.role, _ = Role.objects.get_or_create(
            id=1,
            defaults={
                "name": "customer",
                "display_name": "customer",
                "description": "test",
                "permissions": "{}",
            },
        )
        self.user = User.objects.create_user(
            phone_number="09123456789",
            password="old_password",
            role=self.role,
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh_token.access_token}")

    def test_change_password_success(self):
        data = {
            "old_password": "old_password",
            "new_password": "new_password",
        }
        response = self.client.put(self.change_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.check_password("new_password")

    def test_change_password_wrong_old_password(self):
        data = {
            "old_password": "wrong_password",
            "new_password": "new_password",
        }
        response = self.client.put(self.change_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthorized(self):
        self.client.credentials()  # Clear authentication
        data = {
            "old_password": "old_password",
            "new_password": "new_password",
        }
        response = self.client.put(self.change_password_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED