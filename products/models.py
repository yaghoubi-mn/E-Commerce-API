from django.db import models

# from accounts.models import


class BaseModels(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Product(BaseModels):

    product_id = models.AutoField(primary_key=True)
    category_id = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )

    brand = models.CharField(max_length=128)

    price = models.DecimalField(max_digits=6, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=3, decimal_places=2)


class ProductImage(models.Model):

    product_image_id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    url = models.URLField()
    alt_text = models.CharField(max_length=32)
    position = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


class Category(BaseModels):

    category_id = models.AutoField(primary_key=True)
    parent_id = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    slug = models.SlugField()

    icon_url = models.URLField()
    banner_url = models.URLField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"


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

    cart_id = models.AutoField(primary_key=True)
    # TODO
    # user_id = models.ForeignKey(, on_delete=models.CASCADE)

    # the price of products in cart before applying discount
    subtotal = models.DecimalField(max_digits=6, decimal_places=2)

    # TODO
    # discount_id = models.ForeignKey(, null=True, blank=True, on_delete=models.SET_NULL)

    # the amount of money that user should be paying
    total_amount = models.DecimalField(max_digits=6, decimal_places=2)

    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default=active)
    items = models.JSONField()

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
