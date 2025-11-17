import pytest
from accounts.models import User, Role
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from products.models import Category
import factory


@pytest.fixture
def make_authorized_client(db):
    def _make(phone_number):
        role = Role.objects.create(name="Test", permissions="{}")
        user = User.objects.create_user(
            phone_number=phone_number, role=role, password="something"
        )
        access_token = str(RefreshToken.for_user(user).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return client, user

    return _make


@pytest.fixture
def category_data():
    return {
        "icon_url": "",
        "name": "sport",
        "description": "this is test",
        "display_order": 1,
    }
