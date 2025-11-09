import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import uuid
from utils.error_messages import OTP_RATE_LIMIT, INVALID_PHONE_NUMBER_FORMAT
from utils.error_messages import OTP_RATE_LIMIT

auth_cache = caches['auth']

@pytest.mark.django_db
class TestSendOTPView:

    def setup_method(self):
        self.client = APIClient()
        self.send_otp_url = reverse('send_otp')
        self.phone_number = '09123456789'
        # Ensure settings are configured for tests
        settings.PHONE_NUMBER_RESEND_OTP_MINUTES = 2

    def test_send_otp_success(self):
        data = {'phone_number': self.phone_number}
        response = self.client.post(self.send_otp_url, data)

        assert response.status_code == status.HTTP_200_OK
        assert 'otp' in response.data
        assert 'temp_token' in response.data
        assert auth_cache.get(self.phone_number) is not None

    def test_send_otp_rate_limit(self):
        # First request
        data = {'phone_number': self.phone_number}
        self.client.post(self.send_otp_url, data)

        # Attempt to send again within the rate limit
        response = self.client.post(self.send_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert OTP_RATE_LIMIT in response.data['phone_number'][0]

    def test_send_otp_invalid_phone_number(self):
        data = {'phone_number': 'invalid-phone'}
        response = self.client.post(self.send_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert INVALID_PHONE_NUMBER_FORMAT in response.data['phone_number'][0]