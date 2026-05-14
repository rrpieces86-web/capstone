from django.contrib import admin
from .models import Product
from .models import Category
from .models import Brand, Order, OrderItem
# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Order)
admin.site.register(OrderItem)