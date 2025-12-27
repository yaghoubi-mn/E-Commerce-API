from products.serializers import CategorySerializer, ProductSerializer, CartSerializer
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from products.models import Category, Product, Cart
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from products.permission import IsAdminUser
import json


class CategoryViews(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Category.objects.all()


class ProductViews(viewsets.ModelViewSet):

    serializer_class = ProductSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Product.objects.all()


class CartViews(viewsets.ModelViewSet):

    serializer_class = CartSerializer
    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
    ]
    queryset = Cart.objects.all()


class GetCartView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, format="json"):
        cart, _ = Cart.objects.get_or_create(
            user_id=self.request.user,
            defaults={"expires_at": datetime.now() + timedelta(days=7)},
        )

        return Response(CartSerializer(cart).data)


class UserCart(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get_cart(self):
        cart = Cart.objects.get(user_id=self.request.user)

        return cart

    def post(self, request, format="json"):
        cart = self.get_cart()
        cartItems = cart.items
        items = request.data

        if not isinstance(items, list):
            return Response({"detail": "Invalid item format"}, status=400)

        for item in items:
            if not isinstance(item, dict):
                return Response({"detail": "Invalid item format"}, status=400)
            product = get_object_or_404(Product, pk=item.get("product_id"))
            cartItems.append(item)
        cart.items = json.dumps(cartItems)
        cart.save()

        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id=None):
        cart = self.get_cart()

        before = len(cart.items)

        cart.items = [i for i in cart.items if str(i.get("product_id")) != str(item_id)]
        after = len(cart.items)

        if before == after:
            return Response({"detail": "Item not found."}, status=404)

        cart.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_204_NO_CONTENT)
