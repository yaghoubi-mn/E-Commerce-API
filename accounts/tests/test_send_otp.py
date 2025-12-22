import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches
from django.conf import settings
from unittest.mock import patch
from datetime import timedelta, datetime

from utils import error_messages

auth_cache = caches['auth']




@pytest.fixture(scope="module")
def send_otp_url():
    return reverse('send_otp')


@pytest.fixture
def valid_phone_number():
    return '09123456789'


@pytest.fixture(autouse=True)
def setup_send_otp_tests_env():
    """
    Ensure settings are configured for tests and clear cache before each test.
    This fixture runs automatically for all tests in this module.
    """
    settings.PHONE_NUMBER_RESEND_OTP_MINUTES = 2
    auth_cache.clear()


@pytest.mark.django_db
def test_send_otp_success_new_request(api_client, send_otp_url, valid_phone_number):
    """
    Test that sending OTP to a valid phone number for the first time is successful.
    """
    data = {'phone_number': valid_phone_number}
    response = api_client.post(send_otp_url, data)

    assert response.status_code == status.HTTP_200_OK
    assert 'otp' in response.data
    assert 'temp_token' in response.data
    # Verify OTP is stored in cache
    cached_data = auth_cache.get(valid_phone_number)
    assert cached_data is not None
    assert 'otp' in cached_data
    assert 'temp_token' in cached_data
    assert 'created_at' in cached_data


@pytest.mark.django_db
def test_send_otp_rate_limit(api_client, send_otp_url, valid_phone_number):
    """
    Test that sending OTP again within the rate limit returns a 400 Bad Request
    and the appropriate error message.
    """
    # First request - should be successful
    data = {'phone_number': valid_phone_number}
    api_client.post(send_otp_url, data)

    # Attempt to send again within the rate limit
    response = api_client.post(send_otp_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'phone_number' in response.data
    assert response.data['phone_number'][0] == error_messages.ERR_OTP_RATE_LIMIT


@pytest.mark.django_db
def test_send_otp_invalid_phone_number_format(api_client, send_otp_url):
    """
    Test that sending OTP with an invalid phone number format returns a
    400 Bad Request and the appropriate error message.
    """
    data = {'phone_number': 'invalid-phone'}
    response = api_client.post(send_otp_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'phone_number' in response.data
    assert error_messages.ERR_INVALID_PHONE_NUMBER_FORMAT in response.data['phone_number'][0]


@pytest.mark.django_db
@patch('random.randint', return_value=123456)
def test_send_otp_with_different_phone_number_after_first_succeeds(mock_randint, api_client, send_otp_url, valid_phone_number):
    """
    Test that sending OTP to a different valid phone number is successful
    even if another OTP was recently sent.
    """
    phone_number_1 = valid_phone_number
    phone_number_2 = '09112223344'

    # Send OTP to the first phone number
    data_1 = {'phone_number': phone_number_1}
    response_1 = api_client.post(send_otp_url, data_1)
    assert response_1.status_code == status.HTTP_200_OK

    # Send OTP to the second phone number immediately
    data_2 = {'phone_number': phone_number_2}
    response_2 = api_client.post(send_otp_url, data_2)
    assert response_2.status_code == status.HTTP_200_OK
    assert 'otp' in response_2.data
    assert 'temp_token' in response_2.data
    assert auth_cache.get(phone_number_2) is not None


@pytest.mark.django_db
def test_send_otp_missing_phone_number(api_client, send_otp_url):
    """
    Test that sending OTP without a phone number returns a 400 Bad Request
    and the appropriate error message.
    """
    data = {}  # Missing phone_number
    response = api_client.post(send_otp_url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'phone_number' in response.data
    assert error_messages.ERR_REQUIRED_FIELD in response.data['phone_number'][0]


@pytest.mark.django_db
@patch('django.utils.timezone.now')
def test_send_otp_after_rate_limit_expires(mock_now, api_client, send_otp_url, valid_phone_number):
    """
    Test that sending OTP is successful after the rate limit duration has passed.
    """
    initial_time = datetime(2023, 1, 1, 10, 0, 0)
    mock_now.return_value = initial_time

    data = {'phone_number': valid_phone_number}

    # First request
    api_client.post(send_otp_url, data)

    # Advance time beyond the rate limit
    mock_now.return_value = initial_time + timedelta(minutes=settings.PHONE_NUMBER_RESEND_OTP_MINUTES + 1)

    # Second request should now pass
    response = api_client.post(send_otp_url, data)
    assert response.status_code == status.HTTP_200_OK
    assert 'otp' in response.data
    assert 'temp_token' in response.data
    assert auth_cache.get(valid_phone_number) is not None