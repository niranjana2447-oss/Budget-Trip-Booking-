from django.db import models
from django.contrib.auth.models import User

class Trip(models.Model):
    place_name = models.CharField(max_length=100)
    state_or_country = models.CharField(max_length=100)
    price = models.IntegerField()
    duration = models.CharField(max_length=50)
    best_time = models.CharField(max_length=100)
    places_covered = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to='trip_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.place_name


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    persons = models.IntegerField()
    travel_date = models.DateField()

    total_amount = models.IntegerField()

    payment_status = models.CharField(max_length=20, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Create your models here.
