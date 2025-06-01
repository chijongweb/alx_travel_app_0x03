from django.core.management.base import BaseCommand
from listings.models import Listing
import random

class Command(BaseCommand):
    help = "Seed the database with sample listings"

    def handle(self, *args, **kwargs):
        # Clear existing data
        Listing.objects.all().delete()

        sample_listings = [
            {
                'title': 'Cozy Apartment in City Center',
                'description': 'A beautiful apartment located in the heart of the city.',
                'price': 50.00,
                'location': 'Johannesburg',
            },
            {
                'title': 'Beachfront Villa',
                'description': 'Luxury villa with stunning beach views.',
                'price': 200.00,
                'location': 'Durban',
            },
            {
                'title': 'Mountain Cabin Retreat',
                'description': 'Secluded cabin in the mountains for a peaceful getaway.',
                'price': 120.00,
                'location': 'Drakensberg',
            },
        ]

        for data in sample_listings:
            listing = Listing.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f'Created listing: {listing.title}'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))
