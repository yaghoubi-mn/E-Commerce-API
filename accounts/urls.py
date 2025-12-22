from django.urls import path
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import CustomTokenObtainPairView, TempRegisterView, RoleViewset
from .views import (
    CustomTokenObtainPairView,
    RegisterView,
    SendOTPView,
    VerifyOTPView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    ResetPasswordView,
    AddressViewSet,
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

router = DefaultRouter()
router.register(r"roles", RoleViewset, basename="roles")
urlpatterns = [
    path("accounts/send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("accounts/verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path('accounts/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/register/', TempRegisterView.as_view(), name='temp_register'),
    path('accounts/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('accounts/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('accounts/register/', RegisterView.as_view(), name='register'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include(router.urls)),
] + router.urls
