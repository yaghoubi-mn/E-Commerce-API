import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.cache import caches
import uuid

from accounts.models import Role, User
from utils.error_messages import PHONE_NUMBER_VALIDATION_REQUIRED, INVALID_TOKEN, USER_REGISTERED_SUCCESSFULLY

auth_cache = caches['auth']

@pytest.mark.django_db
class TestRegisterView:

    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.role, _ = Role.objects.get_or_create(
            id=1,
            defaults={
                "name": "customer",
                "display_name": "customer",
                "description": 'test',
                "permissions": '{}'
            }
        )
    
    def test_register_success(self):
        temp_token = uuid.uuid4()
        phone_number = '09123456788'
        auth_cache.set(f'verified_{phone_number}', {'temp_token': str(temp_token)})

        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': phone_number,
            'password': 'password123',
            'temp_token': str(temp_token),
        }

        response = self.client.post(self.register_url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(phone_number=phone_number).exists()
        assert response.data['detail'] == 'User registered successfully.'

    def test_register_invalid_temp_token(self):
        data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '09123456788',
            'password': 'password123',
            'temp_token': str(uuid.uuid4()),
        }

        response = self.client.post(self.register_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PHONE_NUMBER_VALIDATION_REQUIRED in response.data['phone_number'][0]