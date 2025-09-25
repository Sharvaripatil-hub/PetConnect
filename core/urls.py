"""
URL configuration for the core app.

This module defines all the URL patterns for the PetConnect core application.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('adopt/', views.adopt_view, name='adopt'),
    path('pet/<int:pet_id>/', views.pet_detail_view, name='pet_detail'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('toggle-adoption/<int:pet_id>/', views.toggle_adoption_status, name='toggle_adoption'),
]
