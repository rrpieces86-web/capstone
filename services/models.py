from django.db import models
from django.urls import reverse

# Create your models here.
class Service(models.Model):
    img = models.ImageField(upload_to='product_pics/', blank=True, null=True)
    title = models.CharField(max_length=128)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.img} - {self.title} - {self.price}"
    
    def get_absolute_url(self):
        return reverse("service_detail", args=[self.id])