import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role
from utils import error_messages


@pytest.mark.django_db
class TestEditProfile:

    profile_url = reverse("profile")

    def test_edit_profile_success(self, authenticated_client, user):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        response = authenticated_client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()

        assert user.first_name == data["first_name"]
        assert user.last_name == data["last_name"]
        assert user.email == data["email"]

    def test_edit_profile_unauthorized(self, api_client):
        data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
        }
        response = api_client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert error_messages.ERR_AUTHENTICATION_FAILED in response.data["detail"]

    def test_edit_profile_read_only_phone_number(self, authenticated_client, user):
        original_phone_number = user.phone_number
        data = {"phone_number": "09876543210"}
        response = authenticated_client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_200_OK

        user.refresh_from_db()
        assert user.phone_number == original_phone_number

    @pytest.mark.parametrize(
        "data, error_field, error_message",
        [
            ({"first_name": ""}, "first_name", error_messages.ERR_BLANK_FIELD),
            ({"first_name": "a" * 31}, "first_name", error_messages.ERR_INVALID_FIRST_NAME),
            ({"last_name": ""}, "last_name", error_messages.ERR_BLANK_FIELD),
            ({"last_name": "a" * 31}, "last_name", error_messages.ERR_INVALID_LAST_NAME),
            ({"email": "invalid-email"}, "email", error_messages.ERR_INVALID_EMAIL),
            ({"email": ""}, "email", error_messages.ERR_INVALID_EMAIL),
        ],
    )
    def test_edit_profile_invalid_data(self, authenticated_client, data, error_field, error_message):
        response = authenticated_client.put(self.profile_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert error_message in response.data[error_field]