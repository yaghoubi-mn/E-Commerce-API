from django.urls import reverse
from rest_framework import status
import pytest
from products.models import Product, ProductImage
from products.serializers import ProductImageSerializer


@pytest.fixture
def product_image_list_url(product):
    return reverse('product-images-list', kwargs={"product_id": product.pk})


@pytest.fixture
def product_image_detail_url(product_image):
    return reverse('product-image-detail', kwargs={'product_image_id': product_image.pk})


@pytest.fixture
def product_image_data(product):
    return {
        'product': product.pk,
        'url': 'https://test-url.com',
        'thumbnail_url': "https://test-url.com",
        'alt_text': 'Test Image',
        'position': 2,
        'is_primary': True
    }


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name='Existing Product',
        description='Description for existing product',
        category=category,
        brand='Existing Brand',
        slug='existing-product',
        sku='EP-001',
        price='50.00',
        weight_kg='0.500',
        dimensions='5x5x5',
        is_active=True,
        is_featured=False
    )

@pytest.fixture
def product_image(db, product):
    return ProductImage.objects.create(
        product=product,
        url="https://test-url.com",
        thumbnail_url="https://test-url.com",
        alt_text='Test Image',
        position=2,
        is_primary=True
    )

@pytest.mark.django_db
class TestProductImage:

    def test_create_product_image(self, authenticated_client, product_image_list_url, product_image_data):
        response = authenticated_client.post(product_image_list_url, product_image_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert ProductImage.objects.count() == 1
        assert ProductImage.objects.get().alt_text == 'Test Image'

    def test_create_product_image_unauthenticated(self, api_client, product_image_list_url, product_image_data):
        response = api_client.post(product_image_list_url, product_image_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_product_image_list(self, authenticated_client, product_image_list_url, product_image_data, product_image):
        response = authenticated_client.get(product_image_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['alt_text'] == product_image_data["alt_text"]

    def test_get_product_image_list_unauthenticated(self, api_client, product_image_list_url, product_image_data):
        response = api_client.get(product_image_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_product_image_detail(self, authenticated_client, product_image_list_url, product_image_data):
        response = authenticated_client.get(product_image_list_url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_product_image_detail_unauthenticated(self, api_client, product_image_detail_url, product_image_data):
        response = api_client.get(product_image_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_product_image(self, authenticated_client, product_image_detail_url, product_image_data):
        updated_data = product_image_data
        updated_data['alt_text'] = 'Updated Product image'
        response = authenticated_client.put(product_image_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_update_product_image_unauthenticated(self, api_client, product_image_detail_url, product_image_data):
        updated_data = product_image_data
        updated_data['alt_text'] = 'Updated Product image'
        response = api_client.put(product_image_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_product_image(self, authenticated_client, product_image_detail_url):
        response = authenticated_client.delete(product_image_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert ProductImage.objects.count() == 0

    def test_delete_product_image_unauthenticated(self, api_client, product_image_detail_url):
        response = api_client.delete(product_image_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
