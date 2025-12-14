from django.db import models
from accounts.models import User
    


class Product(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    category = models.ForeignKey(
        "Category", null=True, on_delete=models.SET_NULL
    )

    brand = models.CharField(max_length=100)
    slug = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=100, unique=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3)
    dimensions = models.CharField(max_length=50)

    view_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    review_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(default=False)


class ProductImage(models.Model):

    product_image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    url = models.URLField()
    thumbnail_url = models.URLField()
    alt_text = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Category(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    parent = models.ForeignKey(
        "self", null=True, on_delete=models.SET_NULL
    )

    slug = models.SlugField()

    icon_url = models.URLField()
    banner_url = models.URLField(null=True)

    display_order = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = "Categories"


class Discount(models.Model):

    TYPE_CHOICES = [
        ("percentage", "درصد"),
        ("fixed", "ثابت"),
        ("free_shipping", "حمل و نقل رایگان"),
    ]

    APPLIES_TO_CHOICES = [
        ("all", "همه"),
        ("products", "محصولات"),
        ("categories", "دسته بندی ها"),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()

    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, default="percentage", choices=TYPE_CHOICES)

    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2)
    usage_limit_total = models.PositiveIntegerField(null=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True)
    used_count = models.PositiveIntegerField(default=0)

    applies_to = models.CharField(max_length=20, default="all", choices=TYPE_CHOICES)
    traget_ids = models.JSONField(default=list)
    first_purchase_only = models.BooleanField(default=False)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):

    # status choices

    active = "ACTIVE"
    checkedOut = "CHECKED OUT"
    expired = "EXPIRED"

    STATUS_CHOICES = (
        (active, "فعال"),
        (checkedOut, "پرداخت شده"),
        (expired, "منقضی شده"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # the price of products in cart before applying discount
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    discount = models.ForeignKey(
        Discount, null=True, on_delete=models.SET_NULL
    )

    # the amount of money that user should be paying
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default=active)
    items = models.JSONField(default=list)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
