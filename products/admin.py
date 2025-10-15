from django.contrib import admin
from .models import Cart, Category, ProductImage, Product

allModels = [Product, ProductImage, Category, Cart]

admin.site.register(allModels)
