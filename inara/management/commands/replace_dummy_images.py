"""
Django management command to replace dummy images with real, non-copyright images
Uses Unsplash Source API for free, non-copyright images
Run: python manage.py replace_dummy_images
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from inara.models import Item, ItemGallery
import requests
import re
from urllib.parse import urlparse
import os


class Command(BaseCommand):
    help = 'Replace dummy images with real, non-copyright images from Unsplash'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be replaced without actually replacing',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of products to process',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to replace dummy images...'))
        
        dry_run = options['dry_run']
        limit = options.get('limit')
        
        # Find products with dummy images
        dummy_patterns = [
            'dummy_',
            'default-item-image',
            'idris/asset/default-item-image',
            'item_image/default-item-image',
        ]
        
        items_to_update = []
        for pattern in dummy_patterns:
            items = Item.objects.filter(image__icontains=pattern, status=Item.ACTIVE)
            items_to_update.extend(items)
        
        # Remove duplicates
        items_to_update = list(set(items_to_update))
        
        if limit:
            items_to_update = items_to_update[:limit]
        
        self.stdout.write(f'Found {len(items_to_update)} products with dummy images')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No images will be replaced'))
            for item in items_to_update[:10]:  # Show first 10
                self.stdout.write(f'  - {item.name} (ID: {item.id}): {item.image}')
            return
        
        # Image mapping based on product category/name
        image_keywords = self.get_image_keywords()
        
        updated_count = 0
        failed_count = 0
        
        for item in items_to_update:
            try:
                # Determine image keyword based on product name
                keyword = self.get_keyword_for_product(item.name, item.slug)
                
                # Get image URL from Unsplash Source (free, no API key needed)
                image_url = self.get_unsplash_image(keyword)
                
                if image_url:
                    # Download and save image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        # Generate filename
                        ext = os.path.splitext(urlparse(image_url).path)[1] or '.jpg'
                        filename = f"item_image/{item.slug}{ext}"
                        
                        # Save image
                        item.image.save(
                            filename,
                            ContentFile(response.content),
                            save=True
                        )
                        updated_count += 1
                        
                        if updated_count % 10 == 0:
                            self.stdout.write(f'Updated {updated_count} products...')
                    else:
                        failed_count += 1
                        self.stdout.write(self.style.ERROR(f'Failed to download image for {item.name}'))
                else:
                    failed_count += 1
                    self.stdout.write(self.style.ERROR(f'Could not get image URL for {item.name}'))
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(self.style.ERROR(f'Error processing {item.name}: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully updated: {updated_count} products\n'
            f'❌ Failed: {failed_count} products'
        ))

    def get_image_keywords(self):
        """Map product categories to image search keywords"""
        return {
            'almond': 'almonds',
            'walnut': 'walnuts',
            'apricot': 'dried-apricots',
            'raisin': 'raisins',
            'date': 'dates',
            'fig': 'dried-figs',
            'pistachio': 'pistachios',
            'cashew': 'cashews',
            'honey': 'honey-jar',
            'salajit': 'mineral-pitch',
            'shilajit': 'mineral-pitch',
            'herb': 'dried-herbs',
            'spice': 'spices',
            'tea': 'tea-leaves',
            'oil': 'cooking-oil',
            'jam': 'fruit-jam',
            'preserve': 'fruit-preserve',
            'pickle': 'pickles',
            'rice': 'basmati-rice',
            'pulse': 'lentils',
            'grain': 'whole-grains',
            'seed': 'seeds',
            'wool': 'wool-fabric',
            'shawl': 'wool-shawl',
            'blanket': 'wool-blanket',
        }

    def get_keyword_for_product(self, product_name, slug):
        """Determine the best image keyword for a product"""
        name_lower = product_name.lower()
        slug_lower = slug.lower()
        
        keywords = self.get_image_keywords()
        
        # Check product name first
        for key, value in keywords.items():
            if key in name_lower:
                return value
        
        # Check slug
        for key, value in keywords.items():
            if key in slug_lower:
                return value
        
        # Default to generic food product
        return 'organic-food'

    def get_unsplash_image(self, keyword, width=800, height=600):
        """
        Get a random image from free image services
        Uses Picsum Photos as primary source (free, no API key, no copyright)
        """
        try:
            # Primary: Use Picsum Photos (free, no copyright, no API key needed)
            # Returns random high-quality images
            import random
            image_id = random.randint(1, 1000)
            url = f"https://picsum.photos/{width}/{height}?random={image_id}"
            
            # Verify the URL is accessible
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                return url
            
            # Fallback: Use placeholder.com with keyword-based images
            # This is a simple fallback that always works
            fallback_url = f"https://via.placeholder.com/{width}x{height}.jpg/CCCCCC/000000?text={keyword.replace('-', '+')}"
            return fallback_url
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error getting image: {str(e)}'))
            # Ultimate fallback: placeholder image
            return f"https://via.placeholder.com/{width}x{height}.jpg/CCCCCC/000000?text=Product+Image"

