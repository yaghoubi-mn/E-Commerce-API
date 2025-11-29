import pytest
from products.models import Category, Product


@pytest.fixture
def category(db):
    return Category.objects.create(
        name='Existing Category',
        description='Description',
        slug='existing-category',
        icon_url='http://example.com/existing-icon.png',
        is_active=True,
    )

