import uuid
import pytest
from django.core.cache import caches
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Role, User
from utils import error_messages

auth_cache = caches["auth"]


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture(scope="session")
def register_url():
    return reverse("register")


@pytest.fixture
def setup_roles():
    Role.objects.get_or_create(
        id=1,
        defaults={
            "name": "customer",
            "display_name": "customer",
            "description": "test",
            "permissions": {},
        },
    )


@pytest.fixture
def valid_data():
    phone_number = "09123456789"
    temp_token = str(uuid.uuid4())
    auth_cache.set(f"verified_{phone_number}", {"temp_token": temp_token})
    return {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": phone_number,
        "password": "password123",
        "temp_token": temp_token,
    }


@pytest.mark.django_db
class TestRegisterView:
    def test_register_success(self, api_client, setup_roles, register_url, valid_data):
        response = api_client.post(register_url, valid_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["detail"] == error_messages.USER_REGISTERED_SUCCESSFULLY
        assert User.objects.filter(phone_number=valid_data["phone_number"]).exists()

    def test_register_phone_number_already_exists(
        self, api_client, setup_roles, register_url, valid_data
    ):
        customer_role = Role.objects.get(id=1)
        User.objects.create_user(
            phone_number=valid_data["phone_number"],
            password=valid_data["password"],
            role=customer_role,
        )

        response = api_client.post(register_url, valid_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["phone_number"][0] == error_messages.ERR_PHONE_NUMBER_ALREADY_EXISTS

    def test_register_invalid_temp_token(
        self, api_client, setup_roles, register_url, valid_data
    ):
        data = valid_data.copy()
        data["temp_token"] = str(uuid.uuid4())

        response = api_client.post(register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["temp_token"][0] == error_messages.ERR_INVALID_TOKEN

    def test_register_missing_fields(
        self, api_client, setup_roles, register_url, valid_data
    ):
        required_fields = list(valid_data.keys())
        for field in required_fields:
            data = valid_data.copy()
            del data[field]

            response = api_client.post(register_url, data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert field in response.data

    def test_register_invalid_email(
        self, api_client, setup_roles, register_url, valid_data
    ):
        data = valid_data.copy()
        data["email"] = "invalid-email"

        response = api_client.post(register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_short_password(
        self, api_client, setup_roles, register_url, valid_data
    ):
        data = valid_data.copy()
        data["password"] = "123"

        response = api_client.post(register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['password'][0] == error_messages.ERR_SHORT_PASSWORD

    @pytest.mark.parametrize(
        "phone_number",
        [
            '1234',
            '122445',
            '+19123445666',
            '+98123456789',
            '091234567890',
            '0912345678',
            '+989123456789',
        ],
    )
    def test_register_invalid_phone_number_format(
        self, api_client, setup_roles, register_url, valid_data, phone_number
    ):
        data = valid_data.copy()
        data["phone_number"] = phone_number  # Invalid phone number format

        response = api_client.post(register_url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['phone_number'][0] == error_messages.ERR_INVALID_PHONE_NUMBER_FORMAT