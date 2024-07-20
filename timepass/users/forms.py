from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *

from django.contrib import admin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'address_line1', 'city', 'state', 'pincode', 'avatar')
    search_fields = ('user__username', 'user__email', 'city', 'state')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'speciality')
    search_fields = ('profile__user__username', 'profile__user__email', 'speciality')

class RegisterForm(UserCreationForm):
    TYPES_OF_USERS = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    user_type = forms.ChoiceField(choices=TYPES_OF_USERS, widget=forms.Select(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-control'}))
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'}))
    password1 = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control', 'data-toggle': 'password', 'id': 'password'}))
    password2 = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-control', 'data-toggle': 'password', 'id': 'password'}))
    address_line1 = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Address Line 1', 'class': 'form-control'}))
    city = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'City', 'class': 'form-control'}))
    state = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'State', 'class': 'form-control'}))
    pincode = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'placeholder': 'Pincode', 'class': 'form-control'}))
    speciality = forms.ChoiceField(choices=DoctorProfile.SPECIALTIES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['user_type', 'first_name', 'last_name', 'avatar', 'username', 'email', 'password1', 'password2', 'address_line1', 'city', 'state', 'pincode', 'speciality']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the specialty field as required only if user_type is 'doctor'
        self.fields['speciality'].required = self.data.get('user_type') == 'doctor'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': self.cleaned_data['user_type'],
                    'address_line1': self.cleaned_data['address_line1'],
                    'city': self.cleaned_data['city'],
                    'state': self.cleaned_data['state'],
                    'pincode': self.cleaned_data['pincode'],
                    'avatar': self.cleaned_data.get('avatar', None)
                }
            )

            if not created:
                profile.user_type = self.cleaned_data['user_type']
                profile.address_line1 = self.cleaned_data['address_line1']
                profile.city = self.cleaned_data['city']
                profile.state = self.cleaned_data['state']
                profile.pincode = self.cleaned_data['pincode']
                profile.avatar = self.cleaned_data.get('avatar', None)
                profile.save()

            if profile.user_type == 'doctor':
                print("Saving doctor profile")  # Debugging print statement
                print("Speciality:", self.cleaned_data['speciality'])  # Debugging print statement
                doctor_profile, doc_created = DoctorProfile.objects.get_or_create(
                    profile=profile,
                    defaults={'speciality': self.cleaned_data['speciality']}
                )
                if not doc_created:
                    doctor_profile.speciality = self.cleaned_data['speciality']
                    doctor_profile.save()


        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(max_length=50, required=True, widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control', 'data-toggle': 'password', 'id': 'password', 'name': 'password'}))
    remember_me = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class UpdateProfileForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))
    address_line1 = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pincode = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    TYPES_OF_USERS = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor')
    ]
    user_type = forms.ChoiceField(choices=TYPES_OF_USERS, widget=forms.Select(attrs={'class': 'form-control'}))
    speciality = forms.ChoiceField(choices=DoctorProfile.SPECIALTIES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'address_line1', 'city', 'state', 'pincode', 'user_type', 'speciality']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].choices = self.TYPES_OF_USERS
        if self.instance:
            self.fields['user_type'].initial = self.instance.user_type
            self.fields['bio'].initial = self.instance.bio
            self.fields['address_line1'].initial = self.instance.address_line1
            self.fields['city'].initial = self.instance.city
            self.fields['state'].initial = self.instance.state
            self.fields['pincode'].initial = self.instance.pincode
            self.fields['avatar'].initial = self.instance.avatar

            # Set initial values for DoctorProfile fields if the user is a doctor
            if self.instance.user_type == 'doctor':
                if doctor_profile := getattr(self.instance, 'doctorprofile', None):
                    self.fields['speciality'].initial = doctor_profile.speciality
                else:
                    self.fields['speciality'].initial = ''

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.bio = self.cleaned_data['bio']
        profile.address_line1 = self.cleaned_data['address_line1']
        profile.city = self.cleaned_data['city']
        profile.state = self.cleaned_data['state']
        profile.pincode = self.cleaned_data['pincode']
        profile.user_type = self.cleaned_data['user_type']
        if commit:
            profile.save()

            if profile.user_type == 'doctor':
                doctor_profile, created = DoctorProfile.objects.get_or_create(
                    profile=profile,
                    defaults={
                        'speciality': self.cleaned_data.get('speciality', ''),  # Handle None value
                    }
                )
                if not created:
                    doctor_profile.speciality = self.cleaned_data.get('speciality', '')
                    doctor_profile.save()
            else:
                DoctorProfile.objects.filter(profile=profile).delete()
        return profile
class TweetForm(forms.ModelForm):
    title = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(max_length=500, required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))
    photo = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    summary = forms.CharField(max_length=250, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    BLOG_TYPES = [
        ('Mental Health', 'Mental Health'), 
        ('Heart Disease', 'Heart Disease'), 
        ('Covid19', 'Covid19'), 
        ('Immunization', 'Immunization')
    ]
    
    category = forms.ChoiceField(choices=BLOG_TYPES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    is_draft = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input mx-2'}))

    class Meta:
        model = Tweet
        fields = ('title', 'content', 'photo', 'category', 'summary', 'is_draft')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].choices = self.BLOG_TYPES
        
        if self.instance:
            self.fields['title'].initial = self.instance.title
            self.fields['content'].initial = self.instance.content
            self.fields['category'].initial = self.instance.category
            self.fields['summary'].initial = self.instance.summary
            self.fields['is_draft'].initial = self.instance.is_draft

    def save(self, commit=True):
        tweet = super().save(commit=False)
        tweet.title = self.cleaned_data['title']
        tweet.content = self.cleaned_data['content']
        tweet.category = self.cleaned_data['category']
        tweet.summary = self.cleaned_data['summary']
        tweet.is_draft = self.cleaned_data['is_draft']
        
        if 'photo' in self.cleaned_data:
            tweet.photo = self.cleaned_data['photo']
        
        if commit:
            tweet.save()
        
        return tweet
    def draft(self, commit=True):
        tweet = super().save(commit=False)
        tweet.title = self.cleaned_data['title']
        tweet.content = self.cleaned_data['content']
        tweet.category = self.cleaned_data['category']
        tweet.summary = self.cleaned_data['summary']
        tweet.is_draft = self.cleaned_data['is_draft']
        
        if 'photo' in self.cleaned_data:
            tweet.photo = self.cleaned_data['photo']
        if commit:
            tweet.save()
        
        return tweet


class AppointmentForm(forms.ModelForm):
    SPECIALTIES = [
        ('Cardiology', 'Cardiology'),
        ('Dermatology', 'Dermatology'),
        ('Neurology', 'Neurology'),
        ('Pediatrics', 'Pediatrics'),
        ('Ortho', 'Ortho'),
        ('Trauma', 'Trauma'),
        ('General Surgery', 'General Surgery')
    ]
    speciality = forms.ChoiceField(choices=SPECIALTIES, widget=forms.Select(attrs={'class': 'form-control'}))
    doctor = forms.ModelChoiceField(queryset=User.objects.filter(profile__user_type='doctor'), widget=forms.Select(attrs={'class': 'form-control'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    
    class Meta:
        model = Appointment
        fields = ['speciality', 'doctor', 'date', 'time']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.profile.user_type == 'patient':
            self.fields['doctor'].queryset = User.objects.filter(profile__user_type='doctor')

    def clean(self):
        cleaned_data = super().clean()
        speciality = cleaned_data.get('speciality')
        doctor = cleaned_data.get('doctor')
        
        if doctor and speciality:
            doctor_profile = Profile.objects.get(user=doctor)
            if doctor_profile.speciality != speciality:
                self.add_error('speciality', 'The selected doctor does not have the required speciality for this appointment.')

        return cleaned_data

    def save(self, commit=True):
        appointment = super().save(commit=False)
        doctor_profile = Profile.objects.get(user=appointment.doctor)
        appointment.speciality = doctor_profile.speciality  # This should match the doctor's speciality
        if commit:
            appointment.save()
        return appointment
    
class UpdateDoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['speciality']
        widgets = {
            'speciality': forms.Select(attrs={'class': 'form-control'})
        }
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_type', 'bio', 'address_line1', 'city', 'state', 'pincode', 'avatar']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['speciality']
        widgets = {
            'speciality': forms.Select(attrs={'class': 'form-control'}),
        }