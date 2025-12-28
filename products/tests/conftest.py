from datetime import timedelta
import pytest
from products.models import Category, Product
from django.utils import timezone


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Existing Category',
        description='Description',
        slug='existing-category',
        icon_url='http://example.com/existing-icon.png',
        is_active=True,
    )


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
            "category": category.id if is_post_method_data else category,
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
def product(category_data):

    category = Category.objects.create(**category_data)

    product = Product.objects.create(
        category=category,
        name="perfume",
        brand="Tom ford",
        slug="tom-ford-perfume2",
        sku="tom-ford2",
        price=99.99,
        weight_kg=1.25,
        dimensions="2cm x 10cm",
        description="this is test",
    )

    return product


@pytest.fixture
def product_two(category_data):

    category = Category.objects.create(**category_data)

    product = Product.objects.create(
        category=category,
        name="perfume 2",
        brand="Tom ford",
        slug="tom-ford-perfume",
        sku="tom-ford",
        price=99.99,
        weight_kg=1.25,
        dimensions="2cm x 10cm",
        description="this is test",
    )

    return product


@pytest.fixture
def cart_data(make_authorized_client):
    """Arguments:
    is_post_method_data(Default = Fasle): if turns true in field that are foreign keys will be a number
    passed using HTTP method and if it is false it will be and Instance of model


    """

    _, user = make_authorized_client("09123456789")

    def _make(is_post_method_data=False, user=user):

        return {
            "user": user.id if is_post_method_data else user,
            "items": [
                {"product_id": 1, "quantity": 4},
                {"product_id": 2, "quantity": 2},
            ],
            "subtotal": 0.00,
            "total_amount": 0.00,
            "status": "ACTIVE",
            "expires_at": timezone.now() + timedelta(days=7),
        }

    return _make