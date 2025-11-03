import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from accounts.models import User, Role

@pytest.mark.django_db
class TestLogin:
    def setup_method(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.role, _ = Role.objects.get_or_create(
            id=1,
            defaults={
                "name": "customer",
                "display_name": "customer",
                "description": 'test',
                "permissions": '{}'
            }
        )
        self.user = User.objects.create_user(
            phone_number='09123456789',
            password='testpassword',
            role=self.role
        )

    def test_login_success(self):
        data = {
            'phone_number': '09123456789',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self):
        data = {
            'phone_number': '09123456789',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self):
        data = {
            'phone_number': '0987654321',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST