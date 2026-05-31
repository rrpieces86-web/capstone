from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from services.models import Service
 
 
class Category(models.Model):
    name = models.CharField(max_length=128)
 
    def __str__(self):
        return self.name
 
 
class Brand(models.Model):
    name = models.CharField(max_length=128)
 
    def __str__(self):
        return self.name
 
 
class Product(models.Model):
    img = models.ImageField(upload_to='product_pics/', blank=True, null=True)
    title = models.CharField(max_length=128)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
 
    def __str__(self):
        return f"{self.title} - {self.brand} - {self.category}"
 
    def get_absolute_url(self):
        return reverse("product_detail", args=[self.id])
 
 
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
 
    def __str__(self):
        return f"{self.user.username}'s order"
 
 
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    # Either product or service will be set — the other will be null
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
 
    def __str__(self):
        if self.product:
            return f"{self.product.title} - #{self.quantity}"
        return f"{self.service.title} - #{self.quantity}"
 
    @property
    def title(self):
        return self.product.title if self.product else self.service.title
 
    @property
    def price(self):
        return self.product.price if self.product else self.service.price
 
    @property
    def img(self):
        return self.product.img if self.product else self.service.img
 
    @property
    def subtotal(self):
        return self.price * self.quantity
    
    
