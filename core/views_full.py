"""
Views for the PetConnect core application.

This module contains all the view functions for handling user requests,
including authentication, pet listings, and admin functionality.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from .models import Pet
from .forms import CustomUserCreationForm, ContactForm


def home(request):
    """
    Home page view displaying welcome message and featured pets.
    """
    # Get the latest 3 available pets for featured section
    featured_pets = Pet.objects.filter(adopted=False)[:3]
    
    context = {
        'featured_pets': featured_pets,
        'total_pets': Pet.objects.filter(adopted=False).count(),
        'adopted_pets': Pet.objects.filter(adopted=True).count(),
    }
    
    return render(request, 'core/home.html', context)


def register_view(request):
    """
    User registration view using custom registration form.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    username = form.cleaned_data.get('username')
                    messages.success(
                        request, 
                        f'Account created successfully for {username}! You can now log in.'
                    )
                    return redirect('login')
            except Exception as e:
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})


class CustomLoginView(LoginView):
    """
    Custom login view with enhanced messaging and redirect handling.
    """
    template_name = 'core/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    """
    Custom logout view with success message.
    """
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)
        

def adopt_view(request):
    """
    Pet adoption listing view with search and pagination.
    """
    pets_list = Pet.objects.filter(adopted=False).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        pets_list = pets_list.filter(
            models.Q(name__icontains=search_query) |
            models.Q(breed__icontains=search_query) |
            models.Q(description__icontains=search_query)
        )
    
    # Filter by breed
    breed_filter = request.GET.get('breed', '')
    if breed_filter:
        pets_list = pets_list.filter(breed__icontains=breed_filter)
    
    # Filter by age range
    age_filter = request.GET.get('age', '')
    if age_filter:
        if age_filter == 'young':
            pets_list = pets_list.filter(age__lte=2)
        elif age_filter == 'adult':
            pets_list = pets_list.filter(age__gt=2, age__lte=7)
        elif age_filter == 'senior':
            pets_list = pets_list.filter(age__gt=7)
    
    # Pagination
    paginator = Paginator(pets_list, 9)  # Show 9 pets per page
    page_number = request.GET.get('page')
    pets = paginator.get_page(page_number)
    
    # Get available breeds for filter dropdown
    available_breeds = Pet.objects.filter(adopted=False).values_list('breed', flat=True).distinct()
    
    context = {
        'pets': pets,
        'search_query': search_query,
        'breed_filter': breed_filter,
        'age_filter': age_filter,
        'available_breeds': available_breeds,
        'total_available': Pet.objects.filter(adopted=False).count(),
    }
    
    return render(request, 'core/adopt.html', context)


def pet_detail_view(request, pet_id):
    """
    Individual pet detail view with adoption interest handling.
    """
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Get related pets (same breed, excluding current pet)
    related_pets = Pet.objects.filter(
        breed=pet.breed, 
        adopted=False
    ).exclude(id=pet.id)[:3]
    
    # Handle adoption interest form submission
    if request.method == 'POST' and request.user.is_authenticated:
        # Here you could handle adoption interest logic
        messages.success(request, f'Thank you for your interest in {pet.name}! We will contact you soon.')
        return redirect('pet_detail', pet_id=pet.id)
    
    context = {
        'pet': pet,
        'related_pets': related_pets,
    }
    
    return render(request, 'core/pet_detail.html', context)


def is_staff_user(user):
    """Helper function to check if user is staff."""
    return user.is_staff


@user_passes_test(is_staff_user)
def admin_dashboard_view(request):
    """
    Admin dashboard view restricted to staff users only.
    Displays pet statistics and management tools.
    """
    # Calculate statistics
    total_pets = Pet.objects.count()
    available_pets = Pet.objects.filter(adopted=False).count()
    adopted_pets = Pet.objects.filter(adopted=True).count()
    
    # Recent pets (last 10)
    recent_pets = Pet.objects.order_by('-created_at')[:10]
    
    # Breed statistics
    from django.db.models import Count
    breed_stats = Pet.objects.values('breed').annotate(
        total=Count('id'),
        available=Count('id', filter=models.Q(adopted=False)),
        adopted=Count('id', filter=models.Q(adopted=True))
    ).order_by('-total')[:5]
    
    context = {
        'total_pets': total_pets,
        'available_pets': available_pets,
        'adopted_pets': adopted_pets,
        'recent_pets': recent_pets,
        'breed_stats': breed_stats,
        'adoption_rate': round((adopted_pets / total_pets * 100) if total_pets > 0 else 0, 1),
    }
    
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def toggle_adoption_status(request, pet_id):
    """
    AJAX view to toggle pet adoption status.
    """
    if request.method == 'POST' and request.user.is_staff:
        try:
            pet = get_object_or_404(Pet, id=pet_id)
            pet.adopted = not pet.adopted
            pet.save()
            
            status_text = 'Adopted' if pet.adopted else 'Available'
            return JsonResponse({
                'success': True,
                'adopted': pet.adopted,
                'status_text': status_text,
                'message': f'{pet.name} has been marked as {status_text.lower()}.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while updating the pet status.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request or insufficient permissions.'
    })


def about_view(request):
    """About page view."""
    return render(request, 'core/about.html')


def contact_view(request):
    """
    Contact page view with form handling.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, you would send email here
            name = form.cleaned_data['name']
            messages.success(
                request, 
                f'Thank you, {name}! Your message has been sent. We will get back to you soon.'
            )
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'core/contact.html', {'form': form})
