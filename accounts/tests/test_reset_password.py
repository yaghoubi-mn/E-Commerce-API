import uuid
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches

from accounts.models import User, Role
from utils import error_messages

auth_cache = caches['auth']


@pytest.fixture
def reset_password_url():
    return reverse("reset_password")


@pytest.fixture
def create_verified_otp(user):
    temp_token = str(uuid.uuid4())
    auth_cache.set(f'verified_{user.phone_number}', {'temp_token': temp_token})
    return temp_token


@pytest.mark.django_db
class TestResetPassword:
    def test_successful_password_reset(
        self, api_client, reset_password_url, user, create_verified_otp
    ):
        data = {
            "phone_number": user.phone_number,
            "temp_token": create_verified_otp,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password("new_password")
        assert response.data["detail"] == error_messages.PASSWORD_RESET_SUCCESSFULLY

    def test_reset_password_with_invalid_temp_token(
        self, api_client, reset_password_url, user
    ):
        data = {
            "phone_number": user.phone_number,
            "temp_token": "some-invalid-token",
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["temp_token"][0] == error_messages.ERR_INVALID_TEMP_TOKEN

    def test_reset_password_for_nonexistent_user(self, api_client, reset_password_url):
        phone_number = "09876543210"
        temp_token = str(uuid.uuid4())
        auth_cache.set(f'verified_{phone_number}', {'temp_token': temp_token})
        data = {
            "phone_number": phone_number,
            "temp_token": temp_token,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data
        assert response.data["phone_number"][0] == error_messages.ERR_USER_NOT_FOUND

    def test_reset_password_without_phone_number(
        self, api_client, reset_password_url, create_verified_otp
    ):
        data = {
            "temp_token": create_verified_otp,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert error_messages.ERR_REQUIRED_FIELD in response.data["phone_number"][0]

    def test_reset_password_without_temp_token(
        self, api_client, reset_password_url, user
    ):
        data = {
            "phone_number": user.phone_number,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "temp_token" in response.data
        assert error_messages.ERR_REQUIRED_FIELD in response.data["temp_token"][0]

    def test_reset_password_without_new_password(
        self, api_client, reset_password_url, user, create_verified_otp
    ):
        data = {
            "phone_number": user.phone_number,
            "temp_token": create_verified_otp,
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        assert error_messages.ERR_REQUIRED_FIELD in response.data["new_password"][0]

    def test_reset_password_with_empty_phone_number(
        self, api_client, reset_password_url, create_verified_otp
    ):
        data = {
            "phone_number": "",
            "temp_token": create_verified_otp,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data
        assert error_messages.ERR_BLANK_FIELD in response.data["phone_number"][0]

    def test_reset_password_with_empty_temp_token(
        self, api_client, reset_password_url, user
    ):
        data = {
            "phone_number": user.phone_number,
            "new_password": "new_password",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "temp_token" in response.data
        assert error_messages.ERR_REQUIRED_FIELD in response.data["temp_token"][0]

    def test_reset_password_with_empty_new_password(
        self, api_client, reset_password_url, user, create_verified_otp
    ):
        data = {
            "phone_number": user.phone_number,
            "temp_token": create_verified_otp,
            "new_password": "",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        assert error_messages.ERR_BLANK_FIELD in response.data["new_password"][0]

    def test_reset_password_with_short_new_password(
        self, api_client, reset_password_url, user, create_verified_otp
    ):
        data = {
            "phone_number": user.phone_number,
            "temp_token": create_verified_otp,
            "new_password": "short",
        }
        response = api_client.post(reset_password_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data
        assert error_messages.ERR_SHORT_PASSWORD in response.data["new_password"][0]