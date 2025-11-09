import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role


@pytest.mark.django_db
class TestGetProfile:
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

    def test_get_profile_success(self):
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone_number'] == self.user.phone_number
        assert response.data['first_name'] == self.user.first_name
        assert response.data['last_name'] == self.user.last_name
        assert response.data['email'] == self.user.email

    def test_get_profile_unauthorized(self):
        self.client.credentials()  # Clear authentication
        response = self.client.get(self.profile_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED