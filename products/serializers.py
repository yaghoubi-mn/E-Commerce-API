from rest_framework import serializers
from products.models import Category


class CategorySerializer(serializers.Serializer):

    class Meta:
        model = Category
        fields = "__all__"
