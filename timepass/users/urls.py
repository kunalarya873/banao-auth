from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('tweet/create/', tweet_create, name='tweet_create'),
    path('tweet/edit/<int:tweet_id>/', tweet_edit, name='tweet_edit'),
    path('tweet/delete/<int:tweet_id>/', tweet_delete, name='tweet_delete'),
    path('tweet/view/<int:tweet_id>/', tweet_view, name='tweet_view'),
    path('tweet/draft/', tweet_draft, name='tweet_draft'),

]
