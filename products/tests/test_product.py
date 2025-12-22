

# TODO: remove fails due to ondelete=models.RESTRICT used in orderitem table
# @pytest.mark.django_db
# def test_delete_product_returns_204(make_authorized_client, product_data):

#     client, _ = make_authorized_client("09140329711")

#     data = product_data()

#     product = Product.objects.create(**data)

#     url = reverse("products-detail", kwargs={"pk": product.product_id})

#     response = client.delete(url)

#     assert response.status_code == status.HTTP_204_NO_CONTENT
from django.urls import reverse
from rest_framework import status

from products.models import Product, Category
from products.serializers import ProductSerializer


@pytest.fixture
def product_list_url():
    return reverse('products-list')


@pytest.fixture
def product_detail_url(product):
    return reverse('products-detail', kwargs={'pk': product.pk})


@pytest.fixture
def product_data(category):
    return {
        'name': 'Test Product',
        'description': 'Description for test product',
        'category': category.pk,
        'brand': 'Test Brand',
        'slug': 'test-product',
        'sku': 'TP-001',
        'price': '100.00',
        'weight_kg': '1.500',
        'dimensions': '10x10x10',
        'is_active': True,
        'is_featured': False
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


@pytest.mark.django_db
class TestProduct:

    def test_create_product(self, authenticated_client, product_list_url, product_data):
        response = authenticated_client.post(product_list_url, product_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() == 1
        assert Product.objects.get().name == 'Test Product'

    def test_create_product_unauthenticated(self, api_client, product_list_url, product_data):
        response = api_client.post(product_list_url, product_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_product_list(self, authenticated_client, product_list_url, product):
        response = authenticated_client.get(product_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == product.name

    def test_get_product_list_unauthenticated(self, api_client, product_list_url, product):
        response = api_client.get(product_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_product_detail(self, authenticated_client, product_detail_url, product):
        response = authenticated_client.get(product_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == product.name

    def test_get_product_detail_unauthenticated(self, api_client, product_detail_url, product):
        response = api_client.get(product_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_product(self, authenticated_client, product_detail_url, product_data, product):
        updated_data = product_data
        updated_data['name'] = 'Updated Product Name'
        response = authenticated_client.put(product_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == 'Updated Product Name'

    def test_update_product_unauthenticated(self, api_client, product_detail_url, product_data, product):
        updated_data = product_data
        updated_data['name'] = 'Updated Product Name'
        response = api_client.put(product_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_product(self, authenticated_client, product_detail_url, product):
        response = authenticated_client.delete(product_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0

    def test_delete_product_unauthenticated(self, api_client, product_detail_url, product):
        response = api_client.delete(product_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
