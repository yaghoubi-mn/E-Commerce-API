import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Role
from utils import error_messages


change_password_url = reverse("change_password")


@pytest.mark.django_db
def test_change_password_success(authenticated_client, user, user_password):
    data = {"old_password": user_password, "new_password": "new_password"}
    response = authenticated_client.put(change_password_url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["detail"] == error_messages.PASSWORD_SUCCESSFULLY_CHANGED
    user.refresh_from_db()
    assert user.check_password("new_password")


@pytest.mark.django_db
def test_change_password_wrong_old_password(authenticated_client):
    data = {
        "old_password": "wrong_password",
        "new_password": "new_password",
    }
    response = authenticated_client.put(change_password_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["old_password"][0] == error_messages.ERR_WRONG_PASSWORD


@pytest.mark.django_db
def test_change_password_unauthorized(api_client):
    data = {"old_password": "old_password", "new_password": "new_password"}
    response = api_client.put(change_password_url, data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_change_password_invalid_password(authenticated_client):
    data = {
        "old_password": "old_password",
        "new_password": "123",
    }
    response = authenticated_client.put(change_password_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["new_password"][0] == error_messages.ERR_SHORT_PASSWORD