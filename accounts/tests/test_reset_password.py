import uuid
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches

from accounts.models import User, Role

auth_cache = caches['auth']


@pytest.mark.django_db
class TestResetPassword:
    def setup_method(self):
        self.client = APIClient()
        self.reset_password_url = reverse("reset_password")
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

    def test_reset_password_success(self):
        # Manually create a verified OTP token in the cache
        temp_token = str(uuid.uuid4())
        auth_cache.set(f'verified_{self.user.phone_number}', {'temp_token': temp_token})

        data = {
            "phone_number": self.user.phone_number,
            "temp_token": temp_token,
            "new_password": "new_password",
        }
        response = self.client.post(self.reset_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.check_password("new_password")

    def test_reset_password_no_verified_otp(self):
        data = {
            "phone_number": self.user.phone_number,
            "temp_token": "some-invalid-token",
            "new_password": "new_password",
        }
        response = self.client.post(self.reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reset_password_user_not_found(self):
        temp_token = "some-verified-temp-token"
        phone_number = "09876543210"
        auth_cache.set(f'verified_{phone_number}', {'temp_token': temp_token})
        data = {
            "phone_number": phone_number,
            "temp_token": temp_token,
            "new_password": "new_password",
        }
        response = self.client.post(self.reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST