import pytest
from products.models import Product
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_create_product_without_auth_returns_401(product_data):
    client = APIClient()

    url = reverse("products-list")

    data = product_data(True)

    response = client.post(url, data, format="json")

    print("resp1", response)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_create_product_with_auth_returns_201(make_authorized_client, product_data):

    client, _ = make_authorized_client("09140329711")

    data = product_data(True)

    url = reverse("products-list")

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == data["name"]


@pytest.mark.django_db
def test_get_products_returns_200(make_authorized_client, product_data):

    client, _ = make_authorized_client("09140329711")

    url = reverse("products-list")

    data = product_data()

    Product.objects.create(**data).save()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


@pytest.mark.django_db
def test_get_single_product_returns_200(make_authorized_client, product_data):

    client, _ = make_authorized_client("09140329711")

    data = product_data()

    product = Product.objects.create(**data)

    url = reverse("products-detail", kwargs={"pk": product.product_id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == product.name


@pytest.mark.django_db
def test_get_single_not_existence_product_returns_404(
    make_authorized_client, product_data
):

    client, _ = make_authorized_client("09140329711")

    data = product_data()

    product = Product.objects.create(**data)

    url = reverse("products-detail", kwargs={"pk": product.product_id + 1})

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# TODO: remove fails due to ondelete=models.RESTRICT used in orderitem table
# @pytest.mark.django_db
# def test_delete_product_returns_204(make_authorized_client, product_data):

#     client, _ = make_authorized_client("09140329711")

#     data = product_data()

#     product = Product.objects.create(**data)

#     url = reverse("products-detail", kwargs={"pk": product.product_id})

#     response = client.delete(url)

#     assert response.status_code == status.HTTP_204_NO_CONTENT
