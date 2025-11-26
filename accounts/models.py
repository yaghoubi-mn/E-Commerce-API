from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import AdminManager, SellerManager, UserManager
from utils.validators import validate_bank_account, validate_phone_number


class Role(models.Model):
    name = models.CharField(max_length=50, verbose_name="نام")
    display_name = models.CharField(max_length=50, verbose_name="نام نمایشی")
    description = models.TextField(null=True, verbose_name="توضیحات")
    permissions = models.JSONField(verbose_name="سطوح دسترسی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده در")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی شده در")

    class Meta:
        verbose_name = "نقش"
        verbose_name_plural = "نقش ها"

    def __str__(self):
        return self.display_name


class User(AbstractBaseUser):
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="نقش")
    email = models.EmailField(null=True, unique=True, verbose_name="ایمیل")
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    phone_number = models.CharField(max_length=12, unique=True, validators=[validate_phone_number], verbose_name="شماره تلفن")
    avatar_url = models.URLField(null=True, verbose_name="آدرس آواتار")
    registered_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت نام")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}, {self.phone_number}"


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='admin', verbose_name="کاربر")

    job_title = models.CharField(max_length=100, verbose_name="عنوان شغلی")
    objects = AdminManager()
    cantact_phone = models.CharField(max_length=20, validators=[validate_phone_number], verbose_name="شماره تماس")
    work_phone = models.CharField(max_length=20, validators=[validate_phone_number], verbose_name="شماره کاری")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verified_admins', verbose_name="ایجاد شده توسط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده در")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی شده در")

    class Meta:
        verbose_name = "ادمین"
        verbose_name_plural = "ادمین ها"

    def __str__(self):
        return str(self.user)


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='seller', verbose_name="کاربر")
    cantact_phone = models.CharField(max_length=20, validators=[validate_phone_number], verbose_name="شماره تماس")
    objects = SellerManager()
    work_phone = models.CharField(max_length=20, validators=[validate_phone_number], verbose_name="شماره کاری")
    bank_account = models.CharField(max_length=100, validators=[validate_bank_account], verbose_name="حساب بانکی")
    is_verified = models.BooleanField(default=False, verbose_name="تایید شده")
    verified_at = models.DateTimeField(null=True, verbose_name="تایید شده در")
    verified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verified_seller', verbose_name="تایید شده توسط")
    average_monthly_sales = models.PositiveIntegerField(default=0, verbose_name="میانگین فروش ماهانه")

    class Meta:
        verbose_name = "فروشنده"
        verbose_name_plural = "فروشندگان"

    def __str__(self):
        return str(self.user)


class Address(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    full_address = models.TextField()
    reciever_name = models.CharField(max_length=100)
    reciever_phone = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="ایجاد شده در")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="بروزرسانی شده در")
    
    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس ها"
