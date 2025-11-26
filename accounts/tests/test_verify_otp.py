import pytest
import uuid
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches

from accounts.models import Role
from utils import error_messages

@pytest.fixture
def customer_role():
    return Role.objects.create(id=1, name="customer", display_name="customer", description="test", permissions={})

auth_cache = caches['auth']

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def verify_otp_url():
    return reverse('verify_otp')

@pytest.fixture
def phone_number():
    return '09123456789'

@pytest.fixture
def otp():
    return 123456

@pytest.fixture
def temp_token():
    return uuid.uuid4()

@pytest.fixture
def setup_otp_in_cache(phone_number, otp, temp_token):
    auth_cache.set(phone_number, {'otp': otp, 'temp_token': str(temp_token)})
    yield
    auth_cache.clear()

@pytest.mark.django_db
class TestVerifyOTPView:

    def test_verify_otp_success(self, api_client, verify_otp_url, phone_number, otp, temp_token, setup_otp_in_cache):
        data = {
            'phone_number': phone_number,
            'otp': otp,
            'temp_token': str(temp_token),
        }
        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert auth_cache.get(f'verified_{phone_number}') is not None
        assert response.data['detail'] == error_messages.OTP_VERIFIED_SUCCESSFULLY

    def test_verify_otp_invalid_otp(self, api_client, verify_otp_url, phone_number, temp_token, setup_otp_in_cache):
        data = {
            'phone_number': phone_number,
            'otp': 999999,  # Wrong OTP
            'temp_token': str(temp_token),
        }
        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['otp'][0] == error_messages.ERR_INVALID_OTP

    def test_verify_otp_expired_otp(self, api_client, verify_otp_url, phone_number, otp, temp_token):
        data = {
            'phone_number': phone_number,
            'otp': otp,
            'temp_token': str(temp_token),
        }
        # Do not set OTP in cache to simulate expiration
        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['phone_number'][0] == error_messages.ERR_OTP_EXPIRED

    def test_verify_otp_invalid_temp_token(self, api_client, verify_otp_url, phone_number, otp, setup_otp_in_cache):
        data = {
            'phone_number': phone_number,
            'otp': otp,
            'temp_token': str(uuid.uuid4()),  # Wrong temp token
        }
        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['temp_token'][0] == error_messages.ERR_INVALID_TEMP_TOKEN

    def test_verify_otp_already_verified_user(self, api_client, verify_otp_url, phone_number, otp, temp_token, customer_role):

        data = {
            'phone_number': phone_number,
            'otp': otp,
            'temp_token': str(temp_token),
        }

        # set verfied flag in cache
        auth_cache.set(f'verified_{phone_number}', {'otp': 1234})

        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['phone_number'][0] == error_messages.ERR_USER_ALREADY_VERIFIED

    def test_verify_otp_phone_not_found(self, api_client, verify_otp_url, phone_number, otp, temp_token, setup_otp_in_cache):
        # Do not create a user, just use the phone_number in cache
        data = {
            'phone_number': '09999999999',  # A phone number that not exists in database
            'otp': otp,
            'temp_token': str(temp_token),
        }
        response = api_client.post(verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['phone_number'][0] == error_messages.ERR_OTP_EXPIRED