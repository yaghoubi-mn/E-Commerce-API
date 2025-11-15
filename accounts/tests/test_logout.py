import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from accounts.models import User, Role
from utils import error_messages

INVALID_REFRESH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYyNzQzNjU5OSwianRpIjoiM2JkM2VkYjRjZDk3NGU5MmEwY2Q1Y2Q5Y2Q5Y2Q5Y2QiLCJ1c2VyX2lkIjoxfQ.5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z5Z"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def logout_url():
    return reverse("logout")


@pytest.fixture
def role():
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
def user(role):
    return User.objects.create_user(
        phone_number="09123456789", password="testpassword", role=role
    )


@pytest.fixture
def refresh_token(user):
    return RefreshToken.for_user(user)


@pytest.mark.django_db
class TestLogout:
    def test_logout_success(self, api_client, logout_url, user, refresh_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_token.access_token}")
        data = {"refresh": str(refresh_token)}
        
        response = api_client.post(logout_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == error_messages.USER_LOGGEDOUT_SUCCESSFULLY
        assert BlacklistedToken.objects.filter(token__token=str(refresh_token)).exists()

    def test_logout_no_refresh_token(self, api_client, logout_url, refresh_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_token.access_token}")
        
        response = api_client.post(logout_url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["refresh"][0] == error_messages.ERR_REQUIRED_FIELD

    def test_logout_invalid_refresh_token(self, api_client, logout_url, refresh_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_token.access_token}")
        data = {"refresh": INVALID_REFRESH_TOKEN}
        
        response = api_client.post(logout_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["refresh"][0] == error_messages.ERR_INVALID_REFRESH_TOKEN

    def test_logout_unauthorized(self, api_client, logout_url, refresh_token):
        data = {"refresh": str(refresh_token)}
        
        response = api_client.post(logout_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == error_messages.ERR_USER_NOT_AUTHENTICATED

    def test_logout_already_logged_out(self, api_client, logout_url, user, refresh_token):
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh_token.access_token}")
        data = {"refresh": str(refresh_token)}
        api_client.post(logout_url, data)
        
        response = api_client.post(logout_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["refresh"][0] == error_messages.ERR_REFRESH_TOKEN_BLACKLISTED
