from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path


router = DefaultRouter()
router.register(r"categories", views.CategoryViews, basename="categories")
router.register(r"products", views.ProductViews, basename="products")
router.register(r"carts", views.CartViews, basename="carts")


images_router = DefaultRouter()
images_router.register(
    r"products/(?P<product_id>\d+)/images",
    views.ProductImageViewSet,
    basename="product-images"
)
images_router.register(
    r"product-images",
    views.ProductImageDetailViewSet,
    basename="product-image"
)

urlpatterns = [
    path("carts/me/", views.GetCartView.as_view(), name="carts-me"),
    path("carts/me/items/", views.UserCart.as_view(), name="carts-me-items"),
    path(
        "carts/me/items/<int:item_id>/",
        views.UserCart.as_view(),
        name="carts-me-items-detail",
    ),
]

urlpatterns += router.urls
urlpatterns += images_router.urls