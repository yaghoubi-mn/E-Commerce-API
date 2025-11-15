from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import AdminManager, SellerManager, UserManager
from utils.validators import validate_bank_account, validate_phone_number


class Role(models.Model):
    name = models.CharField(max_length=50)
    display_name = models.CharField(max_length=50)
    description = models.TextField(null=True)
    permissions = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractBaseUser):
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    email = models.EmailField(null=True, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12, unique=True, validators=[validate_phone_number])
    avatar_url = models.URLField(null=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.phone_number}"


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='admin')

    job_title = models.CharField(max_length=100)
    objects = AdminManager()
    cantact_phone = models.CharField(max_length=20, validators=[validate_phone_number])
    work_phone = models.CharField(max_length=20, validators=[validate_phone_number])
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verified_admins')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='seller')
    cantact_phone = models.CharField(max_length=20, validators=[validate_phone_number])
    objects = SellerManager()
    work_phone = models.CharField(max_length=20, validators=[validate_phone_number])
    bank_account = models.CharField(max_length=100, validators=[validate_bank_account])
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True)
    verified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verified_seller')
    average_monthly_sales = models.PositiveIntegerField(default=0)


class Address(models.Model):
    # TODO: implement this
    pass