from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=200, blank=True)
    street_address = models.CharField(max_length=200, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name="profile")
    profile_picture = models.ImageField(upload_to="profile_images/",blank=True,null=True)
    bio = models.TextField(blank=True)
    dob = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
