from django.urls import path
from . import mfa_views

urlpatterns = [
    path('setup/', mfa_views.totp_setup, name='mfa_setup'),
    path('verify/', mfa_views.totp_verify, name='mfa_verify'),
    path('disable/', mfa_views.totp_disable, name='mfa_disable'),
]
