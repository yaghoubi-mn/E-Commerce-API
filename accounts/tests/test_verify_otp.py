import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches
import uuid
from utils.error_messages import OTP_EXPIRED, INVALID_TEMP_TOKEN, INVALID_OTP, OTP_VERIFIED_SUCCESSFULLY

auth_cache = caches['auth']

@pytest.mark.django_db
class TestVerifyOTPView:

    def setup_method(self):
        self.client = APIClient()
        self.verify_otp_url = reverse('verify_otp')
        self.phone_number = '09123456789'
        self.otp = 123456
        self.temp_token = uuid.uuid4()

    def _send_otp_for_verification(self):
        # Simulate sending OTP to populate cache
        auth_cache.set(self.phone_number, {'otp': self.otp, 'temp_token': str(self.temp_token)})

    def test_verify_otp_success(self):
        self._send_otp_for_verification()
        data = {
            'phone_number': self.phone_number,
            'otp': self.otp,
            'temp_token': str(self.temp_token),
        }
        response = self.client.post(self.verify_otp_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert auth_cache.get(f'verified_{self.phone_number}') is not None
        assert response.data['detail'] == OTP_VERIFIED_SUCCESSFULLY

    def test_verify_otp_invalid_otp(self):
        self._send_otp_for_verification()
        data = {
            'phone_number': self.phone_number,
            'otp': 999999,  # Wrong OTP
            'temp_token': str(self.temp_token),
        }
        response = self.client.post(self.verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert INVALID_OTP in response.data['otp'][0]

    def test_verify_otp_invalid_temp_token(self):
        self._send_otp_for_verification()
        data = {
            'phone_number': self.phone_number,
            'otp': self.otp,
            'temp_token': str(uuid.uuid4()),  # Wrong temp token
        }
        response = self.client.post(self.verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert INVALID_TEMP_TOKEN in response.data['temp_token'][0]

    def test_verify_otp_expired_otp(self):
        data = {
            'phone_number': self.phone_number,
            'otp': self.otp,
            'temp_token': str(self.temp_token),
        }

        auth_cache.delete(self.phone_number)
        response = self.client.post(self.verify_otp_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        print(response.data)
        assert OTP_EXPIRED in response.data['phone_number'][0]