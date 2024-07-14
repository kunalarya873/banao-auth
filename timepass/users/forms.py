from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile, Tweet

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

    class Meta:
        model = User
        fields = ['user_type', 'first_name', 'last_name', 'avatar', 'username', 'email', 'password1', 'password2', 'address_line1', 'city', 'state', 'pincode']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()

            # Create or update Profile instance with UUID
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
    
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'address_line1', 'city', 'state', 'pincode', 'user_type']
    
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
    
    is_draft = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

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