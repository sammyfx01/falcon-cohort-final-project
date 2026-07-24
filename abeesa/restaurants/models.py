from django.db import models
from django.contrib.auth.models import User


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    account_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def average_rating(self):
        from django.db.models import Avg
        result = Review.objects.filter(menu_item__restaurant=self).aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None

    def review_count(self):
        return Review.objects.filter(menu_item__restaurant=self).count()


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.restaurant.name}"

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    def review_count(self):
        return self.reviews.count()


class ContactMessage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    response = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} — {self.created_at.strftime('%b %d, %Y')}"


class Review(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('menu_item', 'customer')

    def __str__(self):
        return f"{self.customer.username} rated {self.menu_item.name} — {self.rating}/5"