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


# returns category data needed to create one
@pytest.fixture
def category_data():
    return {
        "icon_url": "https://test.com",
        "name": "sport",
        "slug": "sport-thisistest",
        "description": "this is test",
        "display_order": 1,
    }


# returns products data needed to create one
@pytest.fixture
def product_data(category_data):
    """Arguments:
    is_post_method_data(Default = Fasle): if turns true in field that are foreign keys will be a number
    passed using HTTP method and if it is false it will be and Instance of model


    """

    category = Category.objects.create(**category_data)

    def _make(is_post_method_data=False):

        return {
            "category_id": category.category_id if is_post_method_data else category,
            "name": "perfume",
            "brand": "Tom ford",
            "slug": "tom-ford-perfume",
            "sku": "tom-ford",
            "price": 99.99,
            "weight_kg": 1.25,
            "dimensions": "2cm x 10cm",
            "description": "this is test",
        }

    return _make


@pytest.fixture
def cart_data(make_authorized_client):
    """Arguments:
    is_post_method_data(Default = Fasle): if turns true in field that are foreign keys will be a number
    passed using HTTP method and if it is false it will be and Instance of model


    """

    _, user = make_authorized_client("09123456789")

    def _make(is_post_method_data=False, user=user):

        return {
            "user_id": user.id if is_post_method_data else user,
            "items": [
                {"product_id": 1, "quantity": 4},
                {"product_id": 2, "quantity": 2},
            ],
            "expires_at": datetime.now() + timedelta(days=7),
        }

    return _make
