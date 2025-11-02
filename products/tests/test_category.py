import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from products.models import Category


@pytest.mark.django_db
def test_category_creation_without_auth_returns_401(category_data):
    client = APIClient()
    url = reverse("categories-list")

    data = category_data

    response = client.post(url, data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_category_creation_returns_201(make_authorized_client, category_data):
    client, _ = make_authorized_client("09140329711")

    url = reverse("categories-list")

    data = category_data

    response = client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_get_categories_returns_200(make_authorized_client):

    client, _ = make_authorized_client("09140329711")

    Category.objects.create(
        icon_url="", name="sport", description="this is test", display_order=1
    )

    url = reverse("categories-list")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_single_category_returns_200(make_authorized_client):

    client, _ = make_authorized_client("09140329711")

    categ = Category.objects.create(
        icon_url="", name="sport", description="this is test", display_order=1
    )

    url = reverse("categories-detail", kwargs={"pk": categ.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_not_existense_category_returns_404(make_authorized_client):

    client, _ = make_authorized_client("09140329711")

    url = reverse("categories-detail", kwargs={"pk": 2})

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_category_returns_204(make_authorized_client):

    client, _ = make_authorized_client("09140329711")

    categ = Category.objects.create(
        icon_url="", name="sport", description="this is test", display_order=1
    )

    url = reverse("categories-detail", kwargs={"pk": categ.id})

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
