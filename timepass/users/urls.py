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
    path('book-appointment/', book_appointment, name='book_appointment'),
    path('confirm-appointment/<int:appointment_id>/', confirm_appointment, name='confirm_appointment'),
    path('get-doctors-by-speciality/', get_doctors_by_speciality, name='get_doctors_by_speciality'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('logout/', logout_view, name='logout'),
    path('scheduled-calls/', scheduled_calls, name='scheduled_calls'),
    path('upcoming-appointments/', upcoming_appointments, name='upcoming_appointments'),

]
