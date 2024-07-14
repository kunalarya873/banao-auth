from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from .forms import *
from .models import *

def home(request):
    tweets = Tweet.objects.all().order_by('created_at')
    return render(request, 'users/tweet_list.html', {'tweets': tweets})

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
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'users/profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')  # Redirect to home page after logout
    return render(request, 'logout.html')  # Render a confirmation page for GET request

@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            if 'publish' in request.POST:
                tweet.is_draft = False
                messages.success(request, 'Tweet published successfully')
            else:
                tweet.is_draft = True
                messages.success(request, 'Tweet saved as draft')
            tweet.save()
            return redirect('home')
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

def tweet_view(request, tweet_id):
    if request.user.is_authenticated:
        tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    else:
        tweet = get_object_or_404(Tweet, pk=tweet_id)
    
    return render(request, 'users/tweet_view.html', {'tweet': tweet})