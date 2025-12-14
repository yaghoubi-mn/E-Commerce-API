import pytest
from django.urls import reverse
from rest_framework import status

from products.models import Category
from products.serializers import CategorySerializer


@pytest.fixture
def category_list_url():
    return reverse('categories-list')


@pytest.fixture
def category_detail_url(category):
    return reverse('categories-detail', kwargs={'pk': category.pk})


@pytest.fixture
def category_data():
    return {
        'name': 'Test Category',
        'description': 'Description for test category',
        'slug': 'test-category',
        'icon_url': 'http://example.com/icon.png',
        'is_active': True,
    }


@pytest.mark.django_db
class TestCategory:

    def test_create_category(self, authenticated_client, category_list_url, category_data):
        response = authenticated_client.post(category_list_url, category_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.count() == 1
        assert Category.objects.get().name == 'Test Category'

    def test_create_category_unauthenticated(self, api_client, category_list_url, category_data):
        response = api_client.post(category_list_url, category_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_category_list(self, authenticated_client, category_list_url, category):
        response = authenticated_client.get(category_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == category.name

    def test_get_category_list_unauthenticated(self, api_client, category_list_url, category):
        response = api_client.get(category_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_category_detail(self, authenticated_client, category_detail_url, category):
        response = authenticated_client.get(category_detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name

    def test_get_category_detail_unauthenticated(self, api_client, category_detail_url, category):
        response = api_client.get(category_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_category(self, authenticated_client, category_detail_url, category_data, category):
        updated_data = category_data
        updated_data['name'] = 'Updated Category Name'
        response = authenticated_client.put(category_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == 'Updated Category Name'

    def test_update_category_unauthenticated(self, api_client, category_detail_url, category_data, category):
        updated_data = category_data
        updated_data['name'] = 'Updated Category Name'
        response = api_client.put(category_detail_url, updated_data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_category(self, authenticated_client, category_detail_url, category):
        response = authenticated_client.delete(category_detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Category.objects.count() == 0

    def test_delete_category_unauthenticated(self, api_client, category_detail_url, category):
        response = api_client.delete(category_detail_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
