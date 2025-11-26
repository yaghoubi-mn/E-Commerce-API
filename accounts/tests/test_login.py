import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User, Role
from utils import error_messages


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def login_url():
    return reverse('login')


@pytest.fixture
def customer_role():
    return Role.objects.create(id=1, name="customer", display_name="customer", description="test", permissions={})

@pytest.fixture
def user(db, customer_role):
    user = User.objects.create_user(
        phone_number='09123456789',
        password='testpassword',
        role=customer_role
    )
    user.is_active = True
    user.save()
    return user


@pytest.mark.django_db
class TestLogin:

    def test_login_success(self, api_client, login_url, user):
        data = {
            'phone_number': user.phone_number,
            'password': 'testpassword'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, api_client, login_url, user):
        data = {
            'phone_number': user.phone_number,
            'password': 'wrongpassword'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == error_messages.ERR_INVALID_PHONE_OR_PASSWORD

    def test_login_nonexistent_user(self, api_client, login_url):
        data = {
            'phone_number': '09876543210',
            'password': 'testpassword'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == error_messages.ERR_INVALID_PHONE_OR_PASSWORD

    def test_login_inactive_user(self, api_client, login_url, user):
        user.is_active = False
        user.save()
        data = {
            'phone_number': user.phone_number,
            'password': 'testpassword'
        }
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['detail'] == error_messages.ERR_USER_IS_NOT_ACTIVE

    @pytest.mark.parametrize(
        'data, error_field',
        [
            ({'password': '12345678'}, 'phone_number'),
            ({'phone_number': '09123456789'}, 'password'),
        ]
    )
    def test_login_missing_fields(self, api_client, login_url, data, error_field):
        
        response = api_client.post(login_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert error_messages.ERR_REQUIRED_FIELD in response.data[error_field][0]