from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# users.User
# addresses.Address
# discounts.Discount
# products.Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('confirmed', 'تأییدشده'),
        ('shipped', 'ارسال‌شده'),
        ('delivered', 'تحویل‌شده'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'پرداخت‌نشده'),
        ('paid', 'پرداخت‌شده'),
        ('refunded', 'بازپرداخت‌شده'),
        ('failed', 'ناموفق'),
    ]

    user = models.ForeignKey(
        User,  # مدل کاربر از اپلیکیشن users
        on_delete=models.RESTRICT,
        related_name='orders',
        verbose_name='کاربر'
    )
    shipping_address = models.ForeignKey(
        'accounts.Address',  # مدل آدرس از اپلیکیشن addresses
        on_delete=models.RESTRICT,
        related_name='orders',
        verbose_name='آدرس حمل‌ونقل'
    )
    discount = models.ForeignKey(
        'products.Discount',  # مدل تخفیف از اپلیکیشن discounts
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='تخفیف'
    )
    order_number = models.CharField(max_length=50, unique=True, verbose_name='شماره سفارش') # random
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ تخفیف')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ کل')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid', verbose_name='وضعیت پرداخت')
    customer_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت مشتری')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت ادمین')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان تأیید')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='زمان به‌روزرسانی')

    class Meta:

        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش‌ها'

    def save(self, *args, **kwargs):
        if self.pk:  # به‌روزرسانی خودکار updated_at
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"سفارش {self.order_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش'
    )
    product = models.ForeignKey(
        'products.Product',  # مدل محصول از اپلیکیشن products
        on_delete=models.RESTRICT,
        related_name='order_items',
        verbose_name='محصول'
    )
    product_name = models.CharField(max_length=255, verbose_name='نام محصول')
    product_snapshot = models.JSONField(blank=True, null=True, verbose_name='تصویر محصول')
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='تعداد')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='قیمت واحد')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ تخفیف')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='قیمت کل')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='زمان ایجاد')

    class Meta:

        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'

    def __str__(self):
        return f"آیتم {self.product_name} در سفارش {self.order.order_number}"


class DiscountUsage(models.Model):
    discount = models.ForeignKey(
        'products.Discount',  # مدل تخفیف از اپلیکیشن discounts
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name='تخفیف'
    )
    user = models.ForeignKey(
        User,  # مدل کاربر از اپلیکیشن users
        on_delete=models.CASCADE,
        related_name='discount_usages',
        verbose_name='کاربر'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='discount_usages',
        verbose_name='سفارش'
    )
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ تخفیف')
    used_at = models.DateTimeField(default=timezone.now, verbose_name='زمان استفاده')

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['used_at']),
        ]
        verbose_name = 'استفاده از تخفیف'
        verbose_name_plural = 'استفاده‌های تخفیف'

    def __str__(self):
        return f"تخفیف {self.discount.code} برای سفارش {self.order.order_number}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('completed', 'تکمیل‌شده'),
        ('failed', 'ناموفق'),
        ('refunded', 'بازپرداخت‌شده'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='سفارش'
    )
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name='شناسه تراکنش') #random
    payment_method = models.CharField(max_length=50, verbose_name='روش پرداخت')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    gateway_response = models.TextField(blank=True, null=True, verbose_name='پاسخ درگاه')
    refund_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه بازپرداخت')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='مبلغ بازپرداخت')
    card_number = models.CharField(max_length=19, blank=True, null=True, verbose_name='شماره کارت (مخفی)')  # مخفی‌شده
    payer_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='نام پرداخت‌کننده')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان پرداخت')
    refunded_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان بازپرداخت')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='زمان به‌روزرسانی')

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'

    def save(self, *args, **kwargs):
        if self.pk:  # به‌روزرسانی خودکار updated_at
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"پرداخت {self.transaction_id} برای سفارش {self.order.order_number}"


class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('picked_up', 'برداشته‌شده'),
        ('in_transit', 'در حال حمل'),
        ('delivered', 'تحویل‌شده'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='shipments',
        verbose_name='سفارش'
    )
    tracking_number = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='شماره پیگیری')
    courier = models.CharField(max_length=100, blank=True, null=True, verbose_name='پیک')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت')
    shipping_notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌های حمل‌ونقل')
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name='زمان تحویل')
    delivered_to = models.CharField(max_length=100, blank=True, null=True, verbose_name='تحویل به')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='زمان ایجاد')
    updated_at = models.DateTimeField(default=timezone.now, verbose_name='زمان به‌روزرسانی')

    class Meta:
        verbose_name = 'حمل‌ونقل'
        verbose_name_plural = 'حمل‌ونقل‌ها'

    def save(self, *args, **kwargs):
        if self.pk:  # به‌روزرسانی خودکار updated_at
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_number