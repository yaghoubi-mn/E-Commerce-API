from django.db import models
from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone_number: str, password: str, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number: str, password: str, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)


class AdminManager(models.Manager):
    def create_admin(self, user, job_title, contact_phone, work_phone):
        admin = self.create(user=user, job_title=job_title, contact_phone=contact_phone, work_phone=work_phone)
        return admin


class SellerManager(models.Manager):
    def create_seller(self, user_data, seller_data):
        user = self.model_meta.get_field('user').related_model.objects.create_user(**user_data, role='seller')
        seller = self.create(user=user, **seller_data)
        return seller