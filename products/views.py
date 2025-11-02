from products.serializers import CategorySerializer
from rest_framework import viewsets
from products.models import Category
from rest_framework.permissions import IsAuthenticated


class CategoryViews(viewsets.ModelViewSet):

    serializer_class = CategorySerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Category.objects.all()
