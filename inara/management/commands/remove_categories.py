"""
Django management command to remove categories and their products
Run: python manage.py remove_categories
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from inara.models import Category, Item, CategoryItem, BundleItem, Wishlist, ProductReview

class Command(BaseCommand):
    help = 'Remove specified categories and all their products'



    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--soft-delete',
            action='store_true',
            help='Set status to DELETED instead of hard deleting',
        )

    def handle(self, *args, **options):
        # Categories to remove
        categories_to_remove = [
            'chitrali tea',
            'chitrali jams & preserves',
            'chitrali herbs',
            'chitrali seeds',
            'chitrali medicinal plants',
            'chitrali grains',
        ]

        dry_run = options['dry_run']
        soft_delete = options['soft_delete']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(self.style.SUCCESS(f'Starting removal of {len(categories_to_remove)} categories...'))

        with transaction.atomic():
            total_categories = 0
            total_items = 0
            total_category_items = 0
            total_bundle_items = 0
            total_wishlist_items = 0
            total_reviews = 0

            for category_name in categories_to_remove:
                # Find categories by name (case-insensitive)
                categories = Category.objects.filter(name__iexact=category_name)
                
                if not categories.exists():
                    self.stdout.write(self.style.WARNING(f'Category not found: {category_name}'))
                    continue

                for category in categories:
                    # Also find child categories
                    child_categories = Category.objects.filter(parentId=category)
                    all_categories = [category] + list(child_categories)
                    
                    if child_categories.exists():
                        self.stdout.write(f'  Found {child_categories.count()} child categories')
                    self.stdout.write(f'\nProcessing category: {category.name} (ID: {category.id})')
                    
                    # Get all items in this category and its children
                    category_items = CategoryItem.objects.filter(
                        categoryId__in=all_categories,
                        status=CategoryItem.ACTIVE
                    )
                    
                    item_ids = list(category_items.values_list('itemId_id', flat=True))
                    items = Item.objects.filter(id__in=item_ids)
                    
                    item_count = items.count()
                    self.stdout.write(f'  Found {item_count} items in category')
                    
                    if item_count > 0:
                        # Count related data
                        bundle_items_count = BundleItem.objects.filter(
                            itemId__in=item_ids,
                            status=BundleItem.ACTIVE
                        ).count()
                        
                        wishlist_count = Wishlist.objects.filter(
                            item__in=item_ids
                        ).count()
                        
                        reviews_count = ProductReview.objects.filter(
                            itemid__in=item_ids
                        ).count()
                        
                        self.stdout.write(f'  Related data:')
                        self.stdout.write(f'    - Bundle items: {bundle_items_count}')
                        self.stdout.write(f'    - Wishlist entries: {wishlist_count}')
                        self.stdout.write(f'    - Product reviews: {reviews_count}')
                        
                        if not dry_run:
                            # Remove bundle items
                            if bundle_items_count > 0:
                                BundleItem.objects.filter(
                                    itemId__in=item_ids,
                                    status=BundleItem.ACTIVE
                                ).update(status=BundleItem.DELETED)
                                self.stdout.write(self.style.SUCCESS(f'    ✓ Removed {bundle_items_count} bundle items'))
                            
                            # Remove wishlist entries
                            if wishlist_count > 0:
                                Wishlist.objects.filter(item__in=item_ids).delete()
                                self.stdout.write(self.style.SUCCESS(f'    ✓ Removed {wishlist_count} wishlist entries'))
                            
                            # Remove product reviews
                            if reviews_count > 0:
                                ProductReview.objects.filter(itemid__in=item_ids).delete()
                                self.stdout.write(self.style.SUCCESS(f'    ✓ Removed {reviews_count} product reviews'))
                            
                            # Remove category-item relationships
                            category_items_count = category_items.count()
                            category_items.update(status=CategoryItem.DELETED)
                            self.stdout.write(self.style.SUCCESS(f'    ✓ Removed {category_items_count} category-item relationships'))
                            
                            # Delete or soft-delete items
                            if soft_delete:
                                items.update(status=Item.DELETED)
                                self.stdout.write(self.style.SUCCESS(f'    ✓ Soft-deleted {item_count} items'))
                            else:
                                items.delete()
                                self.stdout.write(self.style.SUCCESS(f'    ✓ Hard-deleted {item_count} items'))
                            
                            total_items += item_count
                            total_category_items += category_items_count
                            total_bundle_items += bundle_items_count
                            total_wishlist_items += wishlist_count
                            total_reviews += reviews_count
                        else:
                            total_items += item_count
                            total_category_items += category_items.count()
                            total_bundle_items += bundle_items_count
                            total_wishlist_items += wishlist_count
                            total_reviews += reviews_count
                    
                    # Delete or soft-delete category and its children
                    if not dry_run:
                        for cat in all_categories:
                            if soft_delete:
                                cat.status = Category.DELETED
                                cat.save()
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Soft-deleted category: {cat.name}'))
                            else:
                                cat.delete()
                                self.stdout.write(self.style.SUCCESS(f'  ✓ Hard-deleted category: {cat.name}'))
                        total_categories += len(all_categories)
                    else:
                        total_categories += len(all_categories)

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'  Categories processed: {total_categories}')
        self.stdout.write(f'  Items processed: {total_items}')
        self.stdout.write(f'  Category-Item relationships: {total_category_items}')
        self.stdout.write(f'  Bundle items: {total_bundle_items}')
        self.stdout.write(f'  Wishlist entries: {total_wishlist_items}')
        self.stdout.write(f'  Product reviews: {total_reviews}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - No changes were made'))
            self.stdout.write(self.style.WARNING('Run without --dry-run to actually delete'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ Removal completed successfully!'))

