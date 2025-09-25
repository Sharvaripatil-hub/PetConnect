from django.db import models
from django.urls import reverse

class Pet(models.Model):
    """
    Pet model representing animals available for adoption.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Enter the pet's name"
    )
    
    breed = models.CharField(
        max_length=100,
        help_text="Enter the pet's breed"
    )
    
    age = models.PositiveIntegerField(
        help_text="Enter the pet's age in years"
    )
    
    description = models.TextField(
        help_text="Provide a detailed description of the pet"
    )
    
    adopted = models.BooleanField(
        default=False,
        help_text="Check if the pet has been adopted"
    )
    
    # Add image field
    image = models.ImageField(
        upload_to='pet_images/',
        blank=True,
        null=True,
        help_text="Upload a photo of the pet"
    )
    
    # Add created and updated timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']  # Show newest pets first
        verbose_name = "Pet"
        verbose_name_plural = "Pets"
    
    def __str__(self):
        """Return string representation of the pet."""
        return f"{self.name} ({self.breed})"
    
    def get_absolute_url(self):
        """Return the URL for the pet detail view."""
        return reverse('pet_detail', kwargs={'pet_id': self.pk})
    
    @property
    def is_available(self):
        """Return True if the pet is available for adoption."""
        return not self.adopted
