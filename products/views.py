from products.serializers import CategorySerializer
from rest_framework.viewsets import ViewSet
from products.models import Category
from rest_framework.permissions import IsAuthenticated


class CategoryViews(ViewSet):

    serializer_class = CategorySerializer
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Category.objects.all()
