from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CustomTokenObtainPairView, TempRegisterView, RoleViewset

router = DefaultRouter()
router.register(r"roles", RoleViewset, basename="roles")
urlpatterns = [
    path('accounts/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/register/', TempRegisterView.as_view(), name='temp_register'),
] + router.urls