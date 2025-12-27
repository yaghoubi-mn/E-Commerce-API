import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from accounts.models import Role


@pytest.mark.django_db
def test_role_creation_without_auth_returns_401(role_data):
    client = APIClient()
    url = reverse("roles-list")

    data = role_data()

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_role_creation_with_auth_returns_201(role_data, make_authorized_client):
    client, _ = make_authorized_client("09123456789")
    url = reverse("roles-list")

    data = role_data()
    

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
def test_get_roles_returns_200(role_data,make_authorized_client):

    client, _ = make_authorized_client("09140329711")
    data = role_data()

    instance = Role.objects.create(**data)

    url = reverse("roles-list")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    # we use 1 index because we have one role defined before
    assert instance.name == response.data[1]["name"]


@pytest.mark.django_db
def test_get_single_role_returns_200(role_data, make_authorized_client):

    client, _ = make_authorized_client("09123456789")

    data = role_data()

    role = Role.objects.create(**data)

    url = reverse("roles-detail", kwargs={"pk": role.pk})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert role.name == response.data["name"]


@pytest.mark.django_db
def test_get_not_existense_role_returns_404(make_authorized_client):

    client, _ = make_authorized_client("09123456789")

    url = reverse("roles-detail", kwargs={"pk": 2})

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_role_returns_204(role_data, make_authorized_client):

    client, _ = make_authorized_client("09123456789")

    data = role_data()

    role = Role.objects.create(**data)

    url = reverse("roles-detail", kwargs={"pk": role.pk})

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT

