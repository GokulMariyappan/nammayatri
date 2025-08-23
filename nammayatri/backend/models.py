from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('driver', 'Driver'),
    ]
    username = models.CharField(max_length = 20 , null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    def __str__(self):
        return f"{self.email} - {self.role}"
    
class RideRequest(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ride_requests')
    driver = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='accepted_rides')
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    worded_from_location = models.CharField(max_length=500, null = True)
    worded_to_location = models.CharField(max_length= 500, null = True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    zone = models.CharField(max_length=20, default='normal')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class Token(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    tokens = models.IntegerField(null=True)
    profit = models.IntegerField(default=0)



