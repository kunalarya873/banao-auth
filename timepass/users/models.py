from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import uuid
class Profile(models.Model):
    SPECIALTIES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Ortho', 'Ortho'),
        ('Trauma', 'Trauma'),
        ('General Surgery', 'General Surgery')
    ]
    speciality = models.CharField(max_length=100, choices=SPECIALTIES, blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField(blank=True)
    address_line1 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=30, blank=True)
    state = models.CharField(max_length=30, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    
    USER_TYPES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patient')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar and hasattr(self.avatar, 'path'):
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
        super().save(*args, **kwargs)
        if self.photo and hasattr(self.photo, 'path'):
            img = Image.open(self.photo.path)
            if img.height > 286 or img.width > 180:
                new_img_size = (286, 180)
                img.thumbnail(new_img_size)
                img.save(self.photo.path)

class DoctorProfile(models.Model):
    SPECIALTIES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Ortho', 'Ortho'),
        ('Trauma', 'Trauma'),
        ('General Surgery', 'General Surgery')
    ]
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, limit_choices_to={'user_type': 'doctor'})
    speciality = models.CharField(max_length=100, choices=SPECIALTIES)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.profile.avatar and hasattr(self.profile.avatar, 'path'):
            img = Image.open(self.profile.avatar.path)
            if img.height > 100 or img.width > 100:
                new_img_size = (100, 100)
                img.thumbnail(new_img_size)
                img.save(self.profile.avatar.path)

    def __str__(self):
        return f'Dr. {self.profile.user.username} - {self.speciality}'

        


class Appointment(models.Model):
    SPECIALTIES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Ortho', 'Ortho'),
        ('Trauma', 'Trauma'),
        ('General Surgery', 'General Surgery')
    ]

    speciality = models.CharField(max_length=100, choices=SPECIALTIES, verbose_name="Speciality")
    patient = models.ForeignKey(User, related_name='patient_appointments', on_delete=models.CASCADE, verbose_name="Patient")
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE, verbose_name="Doctor")
    date = models.DateField(verbose_name="Appointment Date")
    time = models.TimeField(verbose_name="Appointment Time")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")


    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        unique_together = ('doctor', 'date', 'time')

    def save(self, *args, **kwargs):
        if self.doctor.profile.user_type != 'doctor':
            raise ValueError("The selected user is not a doctor.")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'Dr. {self.doctor} with Pt. {self.patient} at {self.date} {self.time}'