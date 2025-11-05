from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r"categories", views.CategoryViews, basename="categories")

urlpatterns = router.urls