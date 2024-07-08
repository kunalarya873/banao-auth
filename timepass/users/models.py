from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import uuid

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True)
    address_line1 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=30, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    
    # Define choices for user_type field
    USER_TYPES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize avatar image if it exceeds 100x100 pixels
        img = Image.open(self.avatar.path)
        if img.height > 100 or img.width > 100:
            new_img_size = (100, 100)
            img.thumbnail(new_img_size)
            img.save(self.avatar.path)
