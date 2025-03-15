from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
    ]
    username = models.CharField(max_length = 20 , null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.email} - {self.role}"
    
class RideRequest(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ride_requests')
    driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_rides')
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

