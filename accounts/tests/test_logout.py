import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role
from utils.error_messages import USER_LOGGEDOUT_SUCCESSFULLY

@pytest.mark.django_db
class TestLogout:
    def setup_method(self):
        self.client = APIClient()
        self.logout_url = reverse("logout")
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
            phone_number="09123456789", password="testpassword", role=self.role
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh_token.access_token}")

    def test_logout_success(self):
        data = {"refresh": str(self.refresh_token)}
        response = self.client.post(self.logout_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == USER_LOGGEDOUT_SUCCESSFULLY

    def test_logout_no_refresh_token(self):
        response = self.client.post(self.logout_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_unauthorized(self):
        self.client.credentials()  # Clear authentication
        data = {"refresh": str(self.refresh_token)}
        response = self.client.post(self.logout_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED