import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role
from utils import error_messages

URL = reverse("profile")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_role():
    role, _ = Role.objects.get_or_create(
        id=1,
        defaults={
            "name": "customer",
            "display_name": "customer",
            "description": "test",
            "permissions": {},
        },
    )
    return role


@pytest.fixture
def active_user(user_role):
    return User.objects.create_user(
        phone_number="09123456789",
        password="testpassword",
        role=user_role,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
    )


@pytest.fixture
def inactive_user(user_role):
    user = User.objects.create_user(
        phone_number="09123456788",
        password="testpassword",
        role=user_role,
        first_name="John",
        last_name="Doe",
        email="john.doe.inactive@example.com",
    )
    user.is_active = False
    user.save()
    return user


@pytest.fixture
def authenticated_api_client(api_client, active_user):
    refresh = RefreshToken.for_user(active_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.mark.django_db
class TestGetProfile:
    def test_get_profile_success(self, authenticated_api_client, active_user):
        response = authenticated_api_client.get(URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone_number"] == active_user.phone_number
        assert response.data["first_name"] == active_user.first_name
        assert response.data["last_name"] == active_user.last_name
        assert response.data["email"] == active_user.email

    def test_get_profile_unauthorized(self, api_client):
        response = api_client.get(URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authentication credentials were not provided." in response.data["detail"]

    def test_get_profile_inactive_user(self, api_client, inactive_user):
      
        refresh = RefreshToken.for_user(inactive_user)
        access_token = str(refresh.access_token)
        
        # Manually set credentials for the API client
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        
        response = api_client.get(URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == error_messages.ERR_USER_IS_NOT_ACTIVE