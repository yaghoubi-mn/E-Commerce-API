import pytest
from accounts.models import User, Role
from products.models import Category
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from datetime import datetime, timedelta


# returns authorized client to send HTTP request and a user object to be used accross user relations
@pytest.fixture
def make_authorized_client(db):
    def _make(phone_number, isAdmin=False):
        role = (
            Role.objects.create(name="Test", permissions="{}")
            if not isAdmin
            else Role.objects.create(name="Admin", permissions="{}")
        )
        user = User.objects.create_user(
            phone_number=phone_number, role=role, password="something"
        )
        access_token = str(RefreshToken.for_user(user).access_token)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        return client, user

    return _make


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_role():
    return Role.objects.create(id=1, name="customer", display_name="customer", description="test", permissions={})


@pytest.fixture
def phone_number():
    return '09123456789'


@pytest.fixture
def user_password():
    return 'testpassword'

@pytest.fixture
def user(db, customer_role, phone_number, user_password):
    user = User.objects.create_user(
        email='test@example.com',
        phone_number=phone_number,
        password=user_password,
        role=customer_role
    )
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client
