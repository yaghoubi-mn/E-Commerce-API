from django.urls import reverse
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from unittest.mock import PropertyMock

from products.models import Discount


@pytest.fixture
def discounts_list_url():
    return reverse('discounts-list')

@pytest.fixture
def discounts_detail_url():
    return reverse('discounts-detail')

@pytest.fixture
def discount_payload():
    """Valid basic payload for creating a discount"""
    start = timezone.now()
    return {
        "title": "Summer Sale",
        "description": "Hot deals",
        "code": "SUMMER2024",
        "discount_type": "percentage",
        "value": 15.00,
        "max_discount": 50.00,
        "starts_at": start,
        "ends_at": start + timedelta(days=7),
        "is_active": True,
        "target_ids": [], 
        "applies_to": "all"
    }

@pytest.mark.django_db
class TestDiscountPermissions:
    
    def test_list_discounts_anonymous(self, api_client, discounts_list_url):
        """Anonymous users cannot list discounts."""
        response = api_client.get(discounts_list_url)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_list_discounts_regular_user(self, authenticated_client, discounts_list_url):
        """Regular users (non-Admin) cannot list discounts."""
        
        response = authenticated_client.get(discounts_list_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_discount_admin_user(self, admin_client, admin_user, discount_payload, discounts_list_url):
        """Admin users can create discounts."""
        
        response = admin_client.post(discounts_list_url, discount_payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Discount.objects.count() == 1
        
        discount = Discount.objects.first()
        assert discount.created_by == admin_user
        assert discount.code == "SUMMER2024"


@pytest.mark.django_db
class TestDiscountValidation:
    
    def test_dates_validation_error(self, admin_client, discount_payload, discounts_list_url):
        """Test that ends_at cannot be before starts_at."""
        
        # Set End date before Start date
        discount_payload['ends_at'] = discount_payload['starts_at'] - timedelta(days=1)
        
        response = admin_client.post(discounts_list_url, discount_payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ends_at" in response.data

    def test_percentage_value_validation(self, admin_client, discount_payload, discounts_list_url):
        """Test that percentage discount cannot exceed 100."""
        
        discount_payload['discount_type'] = 'percentage'
        discount_payload['value'] = 101.00
        
        response = admin_client.post(discounts_list_url, discount_payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "value" in response.data

    def test_fixed_value_validation_pass(self, admin_client, discount_payload, discounts_list_url):
        """Fixed discounts CAN be greater than 100."""
        
        discount_payload['discount_type'] = 'fixed'
        discount_payload['value'] = 500000
        
        response = admin_client.post(discounts_list_url, discount_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestDiscountFunctionality:

    def test_queryset_ordering(self, admin_client, discounts_list_url, admin_user):
        """Ensure discounts are ordered by -starts_at (newest first)."""
        
        now = timezone.now()
        
        # Create directly in DB to save time
        d1 = Discount.objects.create(
            title="Old", code="OLD", created_by=admin_user, 
            starts_at=now - timedelta(days=10), ends_at=now, max_discount=0
        )
        d2 = Discount.objects.create(
            title="New", code="NEW", created_by=admin_user, 
            starts_at=now, ends_at=now + timedelta(days=5), max_discount=0
        )
        
        response = admin_client.get(discounts_list_url)
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        
        # Expected: d2 (New) then d1 (Old) because of -starts_at
        assert results[0]['code'] == "NEW"
        assert results[1]['code'] == "OLD"

    def test_update_discount(self, admin_client, admin_user):
        """Admin can update a discount."""
        
        now = timezone.now()
        discount = Discount.objects.create(
            title="Update Me", code="UPDATE", created_by=admin_user,
            starts_at=now, ends_at=now + timedelta(days=1), max_discount=10
        )
        
        url = reverse('discounts-detail', kwargs={'pk': discount.id})
        data = {
            "title": "Updated Title",
            "starts_at": discount.starts_at,
            "ends_at": discount.ends_at,
            "max_discount": 10,
            "code": "UPDATE",
            "description": 'new test'
        }
        
        response = admin_client.put(url, data, format='json')
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        
        discount.refresh_from_db()
        assert discount.title == "Updated Title"

    def test_delete_discount(self, admin_client, admin_user):
        """Admin can delete a discount."""
        
        now = timezone.now()
        discount = Discount.objects.create(
            title="Delete Me", code="DEL", created_by=admin_user,
            starts_at=now, ends_at=now + timedelta(days=1), max_discount=10
        )
        
        url = reverse('discounts-detail', kwargs={'pk': discount.id})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Discount.objects.filter(id=discount.id).exists() is False

    def test_read_only_fields(self, admin_client, admin_user, user_two, discount_payload, discounts_list_url):
        """Ensure created_by cannot be manually set/overwritten via API."""
        
        discount_payload['created_by'] = user_two.id
        
        response = admin_client.post(discounts_list_url, discount_payload, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        discount = Discount.objects.get(code=discount_payload['code'])
        
        assert discount.created_by == admin_user
        assert discount.created_by != user_two