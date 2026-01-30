"""
Management command to clear product cache.
Run: python manage.py clear_product_cache
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache

class Command(BaseCommand):
    help = 'Clears all product-related cache entries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing product cache...'))
        
        # Clear all cache entries with the prefix
        try:
            # If using Redis, we can clear specific keys
            # For now, clear all cache (you can make this more specific)
            cache.clear()
            self.stdout.write(self.style.SUCCESS('Product cache cleared successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error clearing cache: {str(e)}'))
            self.stdout.write(self.style.WARNING('You may need to restart Redis or clear cache manually'))

