from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from accounts.models import User, Address, Role
import pytest
from rest_framework.test import APIClient
from utils import error_messages


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def customer_role():
    return Role.objects.create(id=1, name="customer", display_name="customer", description="test", permissions={})


@pytest.fixture
def user(db, customer_role):
    user = User.objects.create_user(
        email='test@example.com',
        phone_number='09123456789',
        password='testpassword',
        role=customer_role
    )
    user.is_active = True
    user.save()
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def address_list_url():
    return reverse('address-list')


@pytest.mark.django_db
class TestAddress:

    def test_create_address_success(self, authenticated_client, address_list_url):
        data = {
            "title": "Home Address",
            "full_address": "123 Main St, Anytown, USA",
            "postal_code": "12345",
            "city": "Anytown",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
        response = authenticated_client.post(address_list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Address.objects.count() == 1
        assert Address.objects.get().title == "Home Address"

    def test_create_address_unauthenticated(self, api_client, address_list_url):
        data = {
            "title": "Home Address",
            "full_address": "123 Main St, Anytown, USA",
            "postal_code": "12345",
            "city": "Anytown",
            "latitude": 34.0522,
            "longitude": -118.2437
        }
        response = api_client.post(address_list_url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_address_missing_fields(self, authenticated_client, address_list_url):
        data = {
            "title": "Home Address",
            "postal_code": "12345",
            "city": "Anytown",
            "latitude": 34.0522,
            "longitude": -118.2437
        } # Missing full_address
        response = authenticated_client.post(address_list_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'full_address' in response.data
        assert error_messages.ERR_REQUIRED_FIELD in response.data['full_address'][0]

    def test_get_address_list_success(self, authenticated_client, address_list_url, user):
        Address.objects.create(user=user, title="Work Address", full_address="456 Oak Ave", postal_code="54321", city="Anytown", latitude=34.0, longitude=-118.0)
        Address.objects.create(user=user, title="Vacation Home", full_address="789 Pine Ln", postal_code="98765", city="Othertown", latitude=35.0, longitude=-119.0)

        response = authenticated_client.get(address_list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert response.data[0]['title'] == "Work Address"

    def test_get_address_list_unauthenticated(self, api_client, address_list_url):
        response = api_client.get(address_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_single_address_success(self, authenticated_client, user):
        address = Address.objects.create(user=user, title="Home Address", full_address="123 Main St", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Home Address"

    def test_get_single_address_unauthenticated(self, api_client, user):
        address = Address.objects.create(user=user, title="Home Address", full_address="123 Main St", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_single_address_not_found(self, authenticated_client):
        url = reverse('address-detail', kwargs={'pk': 999})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_single_address_of_another_user(self, authenticated_client, user, customer_role):
        another_user = User.objects.create_user(
            email='another@example.com',
            phone_number='09111111111',
            password='anotherpassword',
            role=customer_role
        )
        another_address = Address.objects.create(user=another_user, title="Other User Address", full_address="456 Other St", postal_code="54321", city="Othertown", latitude=35.0, longitude=-119.0)
        url = reverse('address-detail', kwargs={'pk': another_address.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND # Should be 404, or 403 if object exists but no permission

    def test_update_address_success(self, authenticated_client, user):
        address = Address.objects.create(user=user, title="Old Title", full_address="Old Address", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        data = {
            "title": "New Title",
            "full_address": "New Address",
            "postal_code": "54321",
            "city": "New City",
            "latitude": 35.0,
            "longitude": -119.0
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        address.refresh_from_db()
        assert address.title == "New Title"

    def test_update_address_unauthenticated(self, api_client, user):
        address = Address.objects.create(user=user, title="Old Title", full_address="Old Address", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        data = {"title": "New Title"}
        response = api_client.put(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_address_of_another_user(self, authenticated_client, user, customer_role):
        another_user = User.objects.create_user(
            email='another@example.com',
            phone_number='09111111111',
            password='anotherpassword',
            role=customer_role
        )
        another_address = Address.objects.create(user=another_user, title="Other User Address", full_address="456 Other St", postal_code="54321", city="Othertown", latitude=35.0, longitude=-119.0)
        url = reverse('address-detail', kwargs={'pk': another_address.pk})
        data = {"title": "Attempted Update"}
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_address_success(self, authenticated_client, user):
        address = Address.objects.create(user=user, title="To Be Deleted", full_address="Delete Me", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Address.objects.filter(pk=address.pk).exists()

    def test_delete_address_unauthenticated(self, api_client, user):
        address = Address.objects.create(user=user, title="To Be Deleted", full_address="Delete Me", postal_code="12345", city="Anytown", latitude=34.0, longitude=-118.0)
        url = reverse('address-detail', kwargs={'pk': address.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_address_of_another_user(self, authenticated_client, user, customer_role):
        another_user = User.objects.create_user(
            email='another@example.com',
            phone_number='09111111111',
            password='anotherpassword',
            role=customer_role
        )
        another_address = Address.objects.create(user=another_user, title="Other User Address", full_address="456 Other St", postal_code="54321", city="Othertown", latitude=35.0, longitude=-119.0)
        url = reverse('address-detail', kwargs={'pk': another_address.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

