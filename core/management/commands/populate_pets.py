from django.core.management.base import BaseCommand
from core.models import Pet
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populate the database with sample pets'

    def handle(self, *args, **options):
        # Clear existing pets
        Pet.objects.all().delete()
        
        # Sample pets data with images
        pets_data = [
            {'name': 'Buddy', 'breed': 'Golden Retriever', 'age': 3, 'description': 'Friendly and energetic dog who loves playing fetch and swimming. Great with kids and other pets.'},
            {'name': 'Luna', 'breed': 'Siamese Cat', 'age': 2, 'description': 'Beautiful and intelligent cat with striking blue eyes. Very vocal and loves attention.'},
            {'name': 'Max', 'breed': 'German Shepherd', 'age': 5, 'description': 'Loyal and protective companion. Well-trained and excellent guard dog. Needs experienced owner.'},
            {'name': 'Bella', 'breed': 'Labrador Mix', 'age': 4, 'description': 'Sweet and gentle mixed breed. Perfect family dog who gets along with everyone.'},
            {'name': 'Charlie', 'breed': 'Beagle', 'age': 6, 'description': 'Friendly hunting dog with great nose. Loves long walks and exploring outdoors.'},
            {'name': 'Lucy', 'breed': 'Persian Cat', 'age': 3, 'description': 'Fluffy and calm indoor cat. Enjoys quiet environments and gentle petting.'},
            {'name': 'Rocky', 'breed': 'Bulldog', 'age': 4, 'description': 'Sturdy and affectionate companion. Low energy but very loving and loyal.'},
            {'name': 'Daisy', 'breed': 'Border Collie', 'age': 2, 'description': 'Highly intelligent and active herding dog. Needs mental stimulation and exercise.'},
            {'name': 'Milo', 'breed': 'Maine Coon Cat', 'age': 5, 'description': 'Large and gentle giant cat. Very social and gets along well with other pets.'},
            {'name': 'Sadie', 'breed': 'Poodle', 'age': 3, 'description': 'Hypoallergenic and intelligent breed. Great for families with allergies.'},
            {'name': 'Jake', 'breed': 'Rottweiler', 'age': 4, 'description': 'Strong and confident dog. Needs firm but loving training. Very protective of family.'},
            {'name': 'Coco', 'breed': 'Ragdoll Cat', 'age': 1, 'description': 'Young and playful kitten with beautiful blue eyes. Very docile and relaxed nature.'},
            {'name': 'Zeus', 'breed': 'Great Dane', 'age': 6, 'description': 'Gentle giant with calm temperament. Despite size, very friendly and good with children.'},
            {'name': 'Nala', 'breed': 'Husky', 'age': 3, 'description': 'Energetic and adventurous sled dog. Needs lots of exercise and mental stimulation.'},
            {'name': 'Oliver', 'breed': 'British Shorthair', 'age': 4, 'description': 'Calm and dignified cat with beautiful grey coat. Independent but affectionate.'},
            {'name': 'Ruby', 'breed': 'Cocker Spaniel', 'age': 2, 'description': 'Sweet and gentle sporting dog. Great with families and loves outdoor activities.'},
            {'name': 'Toby', 'breed': 'Mixed Breed', 'age': 5, 'description': 'Unique mixed breed with wonderful personality. Very adaptable and loving companion.'},
            {'name': 'Princess', 'breed': 'Chihuahua', 'age': 3, 'description': 'Small but mighty personality. Loyal to owner and makes excellent lap dog.'},
            {'name': 'Bear', 'breed': 'Saint Bernard', 'age': 4, 'description': 'Massive but gentle rescue dog. Great with kids and very patient and calm.'},
            {'name': 'Whiskers', 'breed': 'Tabby Cat', 'age': 2, 'description': 'Playful tabby with distinctive markings. Very social and loves interactive toys.'},
        ]
        
        # Create pets
        for pet_data in pets_data:
            Pet.objects.create(**pet_data)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(pets_data)} sample pets!')
        )
