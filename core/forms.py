"""
Forms for the PetConnect core application.

This module contains all form definitions including user registration
and contact forms with custom styling and validation.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pet


class CustomUserCreationForm(UserCreationForm):
    """
    Extended user registration form that includes email field
    and applies Bootstrap styling to all form fields.
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
            
        # Update placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'
    
    def save(self, commit=True):
        """Save the user with email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PetForm(forms.ModelForm):
    """Form for adding/editing pets."""
    class Meta:
        model = Pet
        fields = ['name', 'breed', 'age', 'description', 'adopted']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pet name'
            }),
            'breed': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pet breed'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '30'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the pet...'
            }),
            'adopted': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class ContactForm(forms.Form):
    """Contact form for user inquiries."""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address'
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...'
        })
    )
    
    def clean_email(self):
        """Validate email format."""
        email = self.cleaned_data.get('email')
        if email and '@' not in email:
            raise forms.ValidationError('Please enter a valid email address.')
        return email
