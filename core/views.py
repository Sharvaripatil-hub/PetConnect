from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Pet
from .forms import CustomUserCreationForm, ContactForm
import os
from django.conf import settings

def home(request):
    """Home page view with featured pets and statistics."""
    # Get featured pets (latest 3 available pets)
    featured_pets = Pet.objects.filter(adopted=False).order_by('-created_at')[:3]
    
    # Get statistics
    total_pets = Pet.objects.count()
    available_pets = Pet.objects.filter(adopted=False).count()
    adopted_pets = Pet.objects.filter(adopted=True).count()
    
    context = {
        'featured_pets': featured_pets,
        'total_pets': total_pets,
        'available_pets': available_pets,
        'adopted_pets': adopted_pets,
    }
    
    return render(request, 'core/home.html', context)

def adopt_view(request):
    """Pet adoption listing with search and filtering."""
    pets = Pet.objects.filter(adopted=False).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        pets = pets.filter(
            Q(name__icontains=search_query) |
            Q(breed__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Filter by breed
    breed_filter = request.GET.get('breed', '')
    if breed_filter:
        pets = pets.filter(breed=breed_filter)
    
    # Filter by age
    age_filter = request.GET.get('age', '')
    if age_filter:
        if age_filter == '5':
            pets = pets.filter(age__gte=5)
        else:
            pets = pets.filter(age=age_filter)
    
    # Get all breeds for filter dropdown
    all_breeds = Pet.objects.values_list('breed', flat=True).distinct().order_by('breed')
    
    # Pagination
    paginator = Paginator(pets, 12)  # Show 12 pets per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'pets': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'breed_filter': breed_filter,
        'age_filter': age_filter,
        'all_breeds': all_breeds,
    }
    
    return render(request, 'core/adopt.html', context)

def pet_detail_view(request, pet_id):
    """Individual pet detail page."""
    pet = get_object_or_404(Pet, id=pet_id)
    
    # Get related pets (same breed, excluding current pet)
    related_pets = Pet.objects.filter(
        breed=pet.breed,
        adopted=False
    ).exclude(id=pet.id)[:3]
    
    context = {
        'pet': pet,
        'related_pets': related_pets,
    }
    
    return render(request, 'core/pet_detail.html', context)

def about_view(request):
    """About page view."""
    return render(request, 'core/about.html')

def contact_view(request):
    """Contact page with form handling."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form (e.g., send email, save to database)
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'core/contact.html', context)

def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to PetConnect.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    context = {'form': form}
    return render(request, 'core/register.html', context)

class CustomLoginView(LoginView):
    """Custom login view with template and success message."""
    template_name = 'core/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Welcome back to PetConnect!')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """Custom logout view with success message."""
    next_page = '/'
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)

# Helper function for admin dashboard
def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_staff

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard_view(request):
    """Admin dashboard with statistics and management tools."""
    # Get statistics
    total_pets = Pet.objects.count()
    available_pets = Pet.objects.filter(adopted=False).count()
    adopted_pets = Pet.objects.filter(adopted=True).count()
    
    # Get recent pets
    recent_pets = Pet.objects.order_by('-created_at')[:10]
    
    # Calculate additional stats
    if total_pets > 0:
        adoption_rate = round((adopted_pets / total_pets) * 100, 1)
    else:
        adoption_rate = 0
    
    # Get popular breed
    popular_breed = Pet.objects.values('breed').annotate(
        count=Count('breed')
    ).order_by('-count').first()
    
    # Get average age
    average_age = Pet.objects.aggregate(Avg('age'))['age__avg'] or 0
    
    # Get pets added this month
    this_month = timezone.now().replace(day=1)
    pets_this_month = Pet.objects.filter(created_at__gte=this_month).count()
    
    # Get total users
    from django.contrib.auth.models import User
    total_users = User.objects.count()
    
    # Get media files count
    media_files_count = 0
    media_path = os.path.join(settings.BASE_DIR, 'media', 'pet_images')
    if os.path.exists(media_path):
        media_files_count = len([f for f in os.listdir(media_path) if os.path.isfile(os.path.join(media_path, f))])
    
    import django
    django_version = django.get_version()
    
    context = {
        'total_pets': total_pets,
        'available_pets': available_pets,
        'adopted_pets': adopted_pets,
        'recent_pets': recent_pets,
        'adoption_rate': adoption_rate,
        'popular_breed': popular_breed['breed'] if popular_breed else 'N/A',
        'average_age': round(average_age, 1),
        'pets_this_month': pets_this_month,
        'total_users': total_users,
        'media_files_count': media_files_count,
        'django_version': django_version,
    }
    
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(is_staff_user)
def toggle_adoption_status(request, pet_id):
    """AJAX view to toggle pet adoption status."""
    if request.method == 'POST':
        pet = get_object_or_404(Pet, id=pet_id)
        pet.adopted = not pet.adopted
        pet.save()
        
        return JsonResponse({
            'success': True,
            'adopted': pet.adopted,
            'message': f'{pet.name} has been marked as {"adopted" if pet.adopted else "available"}.'
        })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
