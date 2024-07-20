from django.utils import timezone
from datetime import datetime
from .models import Appointment
def has_upcoming_appointments(user_profile):
    """
    Check if the given user profile (patient) has upcoming appointments.
    """
    if user_profile.user_type == 'patient':
        return Appointment.objects.filter(
            patient=user_profile.user,
            date__gte=timezone.now().date()
        ).exists()
    return False

from django.utils import timezone

def has_scheduled_calls(user_profile):
    """
    Check if the given user profile (doctor) has scheduled calls.
    """
    if user_profile.user_type == 'doctor':
        now = timezone.now().date()  # Get the current date in the server timezone
        # Print debug info
        print(f"Checking for doctor: {user_profile.user.username}")
        print(f"Current date: {now}")
        
        # Query appointments
        appointments = Appointment.objects.filter(
            doctor=user_profile.user,
            date__gte=now
        )
        
        # Debug output
        print(f"Found appointments: {appointments}")
        
        # Return whether any future appointments exist
        return appointments.exists()
    return False

