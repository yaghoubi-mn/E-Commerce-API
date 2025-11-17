from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    assigned_to = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True, related_name='assigned_to_user')
    department = models.CharField(max_length=100, default='general')
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, db_index=True)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, db_index=True)
    satisfaction_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(1), MaxValueValidator(5)])
    satisfaction_comment = models.TextField()
    last_response_at = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)
    message = models.TextField()
    attachments = models.JSONField(default=list)
    is_internal = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
