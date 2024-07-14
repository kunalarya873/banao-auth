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

class Tweet(models.Model):
    BLOG_TYPES = [
        ('Mental Health', 'Mental Health'),
        ('Heart Disease', 'Heart Disease'),
        ('Covid19', 'Covid19'),
        ('Immunization', 'Immunization')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Title')
    category = models.CharField(max_length=50, choices=BLOG_TYPES)
    content = models.TextField(max_length=500)
    summary = models.TextField(max_length=250)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - {self.summary[:15]}...'

    def save(self, *args, **kwargs):
        if self.photo:
            super().save(*args, **kwargs)
            img = Image.open(self.photo.path)
            if img.height > 286 or img.width > 180:
                new_img_size = (286, 180)
                img.thumbnail(new_img_size)
                img.save(self.photo.path)
    def draft(self, *args, **kwargs):
        if self.photo:
            super().save(*args, **kwargs)
            img = Image.open(self.photo.path)
            if img.height > 286 or img.width > 180:
                new_img_size = (286, 180)
                img.thumbnail(new_img_size)
                img.save(self.photo.path)

        