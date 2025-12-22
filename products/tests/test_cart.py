import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from products.models import Cart, Product


@pytest.mark.django_db
def test_cart_creation_without_auth_returns_401(cart_data):
    client = APIClient()
    url = reverse("carts-list")

    data = cart_data(True)

    response = client.post(url, data)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_cart_creation_without_admin_rights_returns_403(
    make_authorized_client, cart_data
):
    client, user = make_authorized_client("09140329711", False)

    data = cart_data(True, user)

    url = reverse("carts-list")

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_create_cart_with_auth_returns_201(make_authorized_client, cart_data):

    client, user = make_authorized_client("09140329711", True)

    data = cart_data(True, user)

    url = reverse("carts-list")

    response = client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["items"] == data["items"]


@pytest.mark.django_db
def test_get_cart_returns_200(make_authorized_client, cart_data):

    client, user = make_authorized_client("09140329711")

    url = reverse("carts-me")

    data = cart_data(False, user)

    Cart.objects.create(**data).save()

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_get_single_cart_returns_200(make_authorized_client, cart_data):

    client, user = make_authorized_client("09140329711", True)

    data = cart_data(False, user)

    cart = Cart.objects.create(**data)

    url = reverse("carts-detail", kwargs={"pk": cart.cart_id})
    url = reverse("carts-detail", kwargs={"pk": cart.id})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["items"] == cart.items


@pytest.mark.django_db
def test_get_single_not_existence_cart_returns_404(make_authorized_client, cart_data):

    client, user = make_authorized_client("09140329711", True)

    data = cart_data(False, user)

    cart = Cart.objects.create(**data)

    url = reverse("carts-detail", kwargs={"pk": cart.cart_id + 1})
    url = reverse("carts-detail", kwargs={"pk": cart.id + 1})

    response = client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_cart_returns_204(make_authorized_client, cart_data):

    client, user = make_authorized_client("09140329711", True)

    data = cart_data(False, user)

    cart = Cart.objects.create(**data)

    url = reverse("carts-detail", kwargs={"pk": cart.cart_id})
    url = reverse("carts-detail", kwargs={"pk": cart.id})

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_add_items_to_cart_returns_200(make_authorized_client, cart_data, product_data):

    client, user = make_authorized_client("09140329711")

    data = cart_data(False, user)

    Cart.objects.create(**data)

    product = product_data()

    product_one = Product.objects.create(**product)

    product["slug"] = "test"
    product["sku"] = "test"

    product_two = Product.objects.create(**product)

    request_data = [
        {"product_id": product_one.product_id, "quantity": 2},
        {"product_id": product_two.product_id, "quantity": 2},
        {"product_id": product_one.id, "quantity": 2},
        {"product_id": product_two.id, "quantity": 2},
    ]

    url = reverse("carts-me-items")

    response = client.post(url, data=request_data, content_type="application/json")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_delete_items_from_cart_returns_204(
    make_authorized_client, cart_data, product_data
):

    client, user = make_authorized_client("09140329711")

    data = cart_data(False, user)

    Cart.objects.create(**data)

    product = product_data()

    url = reverse("carts-me-items-delete", kwargs={"item_id": 1})

    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
