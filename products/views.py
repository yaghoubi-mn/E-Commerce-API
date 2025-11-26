from products.serializers import CategorySerializer, ProductSerializer
from rest_framework import viewsets
from products.models import Category, Product
from rest_framework.permissions import IsAuthenticated


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