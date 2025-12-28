from rest_framework import serializers
from products.models import Category, Product, Cart, ProductImage


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"
        read_only_fields = ("product",)