from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r"categories", views.CategoryViews, basename="categories")
router.register(r"products", views.ProductViews, basename="products")

urlpatterns = router.urls