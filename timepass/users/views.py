from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import *
from .models import *
from oauth2_provider.views.generic import ProtectedResourceView
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import pytz
from django.http import HttpResponse
from django.http import JsonResponse
from django.utils import timezone
from .utlis import *

def home(request):
    user = request.user
    blog_types = Tweet.objects.values_list('category', flat=True).distinct()
    selected_blog_type = request.GET.get('blog_type')
    
    if selected_blog_type:
        tweets = Tweet.objects.filter(category=selected_blog_type, is_draft=False).order_by('created_at')
    else:
        tweets = Tweet.objects.filter(is_draft=False).order_by('created_at')
    
    has_upcoming_appointments_flag = False
    has_scheduled_calls_flag = False
    
    if user.is_authenticated:
        try:
            profile = user.profile
            print(f"Profile: {profile}")  # Debugging print
            # Check if the profile has upcoming appointments or scheduled calls
            has_upcoming_appointments_flag = has_upcoming_appointments(request.user.profile)
            has_scheduled_calls_flag = has_scheduled_calls(request.user.profile)
        except Profile.DoesNotExist:
            print("Profile does not exist")  # Debugging print
    
    context = {
        'tweets': tweets,
        'blog_types': blog_types,
        'selected_blog_type': selected_blog_type,
        'has_upcoming_appointments': has_upcoming_appointments_flag,
        'has_scheduled_calls': has_scheduled_calls_flag,
    }
    
    return render(request, 'users/tweet_list.html', context)


class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'users/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
        return render(request, self.template_name, {'form': form})

class CustomLoginView(LoginView):
    form_class = LoginForm

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super().form_valid(form)

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_message = ("We've emailed you instructions for setting your password, "
                       "if an account exists with the email you entered. You should receive them shortly. "
                       "If you don't receive an email, "
                       "please make sure you've entered the address you registered with, and check your spam folder.")
    success_url = reverse_lazy('home')

class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')


@login_required
def profile(request):
    user = request.user
    profile = user.profile
    doctor_profile_form = None

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if profile.user_type == 'doctor':
            doctor_profile, created = DoctorProfile.objects.get_or_create(profile=profile)
            doctor_profile_form = DoctorProfileForm(request.POST, instance=doctor_profile)

        if user_form.is_valid() and profile_form.is_valid() and (not doctor_profile_form or doctor_profile_form.is_valid()):
            user_form.save()
            profile_form.save()
            if doctor_profile_form:
                doctor_profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

        if profile.user_type == 'doctor':
            doctor_profile, created = DoctorProfile.objects.get_or_create(profile=profile)
            doctor_profile_form = DoctorProfileForm(instance=doctor_profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'doctor_profile_form': doctor_profile_form,
    }

    return render(request, 'users/profile.html', context)


@login_required
def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        return redirect('home')  # Redirect to home page after logout
    return render(request, 'users/logout.html')  # Render a confirmation page for GET request

@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            if 'save-draft' in request.POST:
                tweet.is_draft = True
                messages.success(request, 'Tweet saved as draft')
            else:
                tweet.is_draft = False
                messages.success(request, 'Tweet published successfully')
            tweet.save()
            return redirect('tweet_draft') if tweet.is_draft else redirect('home') 
    else:
        form = TweetForm()
    
    return render(request, 'users/tweet_form.html', {'form': form})

@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            if 'publish' in request.POST:
                tweet.is_draft = False
                messages.success(request, 'Tweet updated and published successfully')
            else:
                tweet.is_draft = True
                messages.success(request, 'Tweet updated and saved as draft')
            tweet.save()
            return redirect('tweet_view', tweet_id=tweet.pk)
    else:
        form = TweetForm(instance=tweet)
    
    return render(request, 'users/tweet_form.html', {'form': form, 'tweet': tweet})

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        messages.success(request, 'Tweet deleted successfully')
        return redirect('home')
    
    return render(request, 'users/tweet_confirm_delete.html', {'tweet': tweet})

@login_required
def tweet_view(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if tweet.is_draft and tweet.user != request.user:
        messages.error(request, 'You do not have permission to view this draft')
        return redirect('home')
    return render(request, 'users/tweet_view.html', {'tweet': tweet})

@login_required
def tweet_draft(request):
    drafts = Tweet.objects.filter(user=request.user, is_draft=True).order_by('created_at')
    return render(request, 'users/tweet_draft_list.html', {'drafts': drafts})


@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('confirm_appointment', appointment_id=appointment.id)
    else:
        form = AppointmentForm(user=request.user)
    
    return render(request, 'users/book_appointment.html', {'form': form})

@login_required
def get_doctors_by_speciality(request):
    speciality = request.GET.get('speciality')
    doctors = User.objects.filter(profile__user_type='doctor', profile__speciality=speciality)
    doctor_list = [{'id': doctor.id, 'name': doctor.get_full_name()} for doctor in doctors]
    return JsonResponse(doctor_list, safe=False)

@login_required
def confirm_appointment(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    return render(request, 'users/confirm_appointment.html', {'appointment': appointment})

class CalendarView(ProtectedResourceView):
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return HttpResponse("This is your calendar view")
    
@login_required
def scheduled_calls(request):
    profile = request.user.profile
    
    if profile.user_type == 'doctor':
        appointments = Appointment.objects.filter(
            doctor=profile,
            date__gte=timezone.now().date()
        )
    else:
        appointments = []

    return render(request, 'users/scheduled_calls.html', {'appointments': appointments})


@login_required
def upcoming_appointments(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated
    
    profile = request.user.profile
    appointments = []

    if profile.user_type == 'patient':
        appointments = Appointment.objects.filter(
            patient=profile.user,
            date__gte=timezone.now().date()
        )

    context = {
        'appointments': appointments
    }
    return render(request, 'users/upcoming_appointments.html', context)
