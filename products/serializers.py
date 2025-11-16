from rest_framework import serializers
from products.models import Category


class CategorySerializer(serializers.Serializer):

    class Meta:
        model = Category
        fields = "__all__"

    def create(self, validated_data):
        category = Category.objects.create(**validated_data)
        return category
