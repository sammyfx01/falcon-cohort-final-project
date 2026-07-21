from django.db import models
from django.contrib.auth.models import User


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.restaurant.name}"