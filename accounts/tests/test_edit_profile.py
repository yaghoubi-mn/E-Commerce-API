import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role


@pytest.mark.django_db
class TestEditProfile:
    def setup_method(self):
        self.client = APIClient()
        self.profile_url = reverse("profile")
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
            password="testpassword",
            role=self.role,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
        )
        self.refresh_token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh_token.access_token}")

    def test_edit_profile_success(self):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        response = self.client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.first_name == data["first_name"]
        assert self.user.last_name == data["last_name"]
        assert self.user.email == data["email"]

    def test_edit_profile_unauthorized(self):
        self.client.credentials()  # Clear authentication
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        response = self.client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_edit_profile_read_only_phone_number(self):
        data = {
            "phone_number": "09876543210",
        }
        response = self.client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.phone_number == "09123456789"