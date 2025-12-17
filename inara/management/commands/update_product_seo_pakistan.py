"""
Django management command to update existing product SEO to be Pakistan-wide focused
Run: python manage.py update_product_seo_pakistan
"""
from django.core.management.base import BaseCommand
from inara.models import Item, Category
from inara.utils.seo_helpers import generate_meta_title, generate_meta_description, generate_pakistan_seo_keywords


class Command(BaseCommand):
    help = 'Update existing product SEO descriptions to be Pakistan-wide focused'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of products to process',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to update product SEO for Pakistan-wide focus...'))
        
        dry_run = options['dry_run']
        limit = options.get('limit')
        
        # Get all active products
        products = Item.objects.filter(status=Item.ACTIVE)
        
        if limit:
            products = products[:limit]
        
        total_count = products.count()
        self.stdout.write(f'Found {total_count} products to update')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No products will be updated'))
            for product in products[:5]:  # Show first 5
                old_title = product.metaTitle or 'No title'
                old_desc = product.metaDescription or 'No description'
                new_title = generate_meta_title(product.name, 'product')
                new_desc = generate_meta_description(product.description or product.name, product.name, 'product')
                self.stdout.write(f'\nProduct: {product.name}')
                self.stdout.write(f'  Old Title: {old_title}')
                self.stdout.write(f'  New Title: {new_title}')
                self.stdout.write(f'  Old Desc: {old_desc[:80]}...')
                self.stdout.write(f'  New Desc: {new_desc[:80]}...')
            return
        
        updated_count = 0
        skipped_count = 0
        
        for product in products:
            try:
                # Check if already has Pakistan-focused SEO
                has_pakistan_seo = (
                    product.metaDescription and 
                    ('Pakistan' in product.metaDescription or 'Karachi' in product.metaDescription or 'Lahore' in product.metaDescription)
                )
                
                if has_pakistan_seo and 'Pakistan' in (product.metaTitle or ''):
                    skipped_count += 1
                    continue
                
                # Update meta title
                if not product.metaTitle or 'Pakistan' not in product.metaTitle:
                    product.metaTitle = generate_meta_title(product.name, 'product')
                
                # Update meta description
                description = product.description or product.name
                if not product.metaDescription or 'Pakistan' not in product.metaDescription:
                    product.metaDescription = generate_meta_description(
                        description, 
                        product.name, 
                        'product'
                    )
                
                # Update meta URL if not set
                if not product.metaUrl:
                    product.metaUrl = f"/products/{product.slug}"
                
                product.save()
                updated_count += 1
                
                if updated_count % 100 == 0:
                    self.stdout.write(f'Updated {updated_count} products...')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating {product.name}: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully updated: {updated_count} products\n'
            f'⏭️  Skipped (already updated): {skipped_count} products\n'
            f'📊 Total processed: {total_count} products'
        ))











