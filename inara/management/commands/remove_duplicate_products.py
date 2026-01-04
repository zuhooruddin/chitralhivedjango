"""
Django management command to find and remove duplicate products
Run: python manage.py remove_duplicate_products
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q
from inara.models import Item, CategoryItem, BundleItem, Wishlist, ProductReview, ItemGallery
from collections import defaultdict

class Command(BaseCommand):
    help = 'Find and remove duplicate products based on various criteria'

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
        parser.add_argument(
            '--method',
            type=str,
            choices=['extposid', 'name', 'name_sku', 'name_slug', 'all'],
            default='all',
            help='Method to detect duplicates: extposid, name, name_sku, name_slug, or all (default: all)',
        )
        parser.add_argument(
            '--keep',
            type=str,
            choices=['oldest', 'newest', 'most_complete', 'highest_id'],
            default='oldest',
            help='Which duplicate to keep: oldest, newest, most_complete, or highest_id (default: oldest)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        soft_delete = options['soft_delete']
        method = options['method']
        keep_strategy = options['keep']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write(self.style.SUCCESS(f'Finding duplicates using method: {method}'))
        self.stdout.write(f'Keeping strategy: {keep_strategy}')

        duplicates_found = {}
        total_duplicates = 0
        total_to_delete = 0

        # Find duplicates by extPosId
        if method in ['extposid', 'all']:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Checking duplicates by extPosId...')
            extposid_dups = self.find_duplicates_by_extposid()
            if extposid_dups:
                duplicates_found['extPosId'] = extposid_dups
                total_duplicates += len(extposid_dups)
                self.stdout.write(self.style.WARNING(f'Found {len(extposid_dups)} groups of duplicates by extPosId'))

        # Find duplicates by name (case-insensitive)
        if method in ['name', 'all']:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Checking duplicates by name (case-insensitive)...')
            name_dups = self.find_duplicates_by_name()
            if name_dups:
                duplicates_found['name'] = name_dups
                total_duplicates += len(name_dups)
                self.stdout.write(self.style.WARNING(f'Found {len(name_dups)} groups of duplicates by name'))

        # Find duplicates by name + SKU
        if method in ['name_sku', 'all']:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Checking duplicates by name + SKU...')
            name_sku_dups = self.find_duplicates_by_name_sku()
            if name_sku_dups:
                duplicates_found['name_sku'] = name_sku_dups
                total_duplicates += len(name_sku_dups)
                self.stdout.write(self.style.WARNING(f'Found {len(name_sku_dups)} groups of duplicates by name+SKU'))

        # Find duplicates by name + slug
        if method in ['name_slug', 'all']:
            self.stdout.write('\n' + '='*60)
            self.stdout.write('Checking duplicates by name + slug...')
            name_slug_dups = self.find_duplicates_by_name_slug()
            if name_slug_dups:
                duplicates_found['name_slug'] = name_slug_dups
                total_duplicates += len(name_slug_dups)
                self.stdout.write(self.style.WARNING(f'Found {len(name_slug_dups)} groups of duplicates by name+slug'))

        if not duplicates_found:
            self.stdout.write(self.style.SUCCESS('\nNo duplicates found!'))
            return

        # Process duplicates
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('PROCESSING DUPLICATES:'))
        self.stdout.write('='*60)

        with transaction.atomic():
            for dup_type, dup_groups in duplicates_found.items():
                self.stdout.write(f'\nProcessing {dup_type} duplicates...')
                
                for group_key, items in dup_groups.items():
                    if len(items) <= 1:
                        continue
                    
                    # Determine which item to keep
                    item_to_keep = self.select_item_to_keep(items, keep_strategy)
                    items_to_delete = [item for item in items if item.id != item_to_keep.id]
                    
                    self.stdout.write(f'\n  Group: {group_key}')
                    self.stdout.write(f'    Keeping: {item_to_keep.name} (ID: {item_to_keep.id}, SKU: {item_to_keep.sku})')
                    self.stdout.write(f'    Deleting: {len(items_to_delete)} duplicate(s)')
                    
                    for item in items_to_delete:
                        self.stdout.write(f'      - {item.name} (ID: {item.id}, SKU: {item.sku})')
                    
                    if not dry_run:
                        deleted_count = self.delete_item_and_relations(items_to_delete, soft_delete)
                        total_to_delete += deleted_count
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Removed {deleted_count} item(s) and related data'))
                    else:
                        total_to_delete += len(items_to_delete)

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SUMMARY:'))
        self.stdout.write(f'  Duplicate groups found: {total_duplicates}')
        self.stdout.write(f'  Total items to delete: {total_to_delete}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nThis was a DRY RUN - No changes were made'))
            self.stdout.write(self.style.WARNING('Run without --dry-run to actually delete'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Removed {total_to_delete} duplicate products successfully!'))

    def find_duplicates_by_extposid(self):
        """Find duplicates by extPosId"""
        duplicates = defaultdict(list)
        
        # Find extPosIds that appear more than once
        extposid_counts = Item.objects.values('extPosId').annotate(
            count=Count('id')
        ).filter(count__gt=1, status=Item.ACTIVE)
        
        for entry in extposid_counts:
            items = Item.objects.filter(
                extPosId=entry['extPosId'],
                status=Item.ACTIVE
            ).order_by('id')
            if items.count() > 1:
                duplicates[entry['extPosId']] = list(items)
        
        return dict(duplicates)

    def find_duplicates_by_name(self):
        """Find duplicates by name (case-insensitive)"""
        duplicates = defaultdict(list)
        
        # Find names that appear more than once (case-insensitive)
        from django.db.models.functions import Lower
        name_counts = Item.objects.annotate(
            name_lower=Lower('name')
        ).values('name_lower').annotate(
            count=Count('id')
        ).filter(count__gt=1, status=Item.ACTIVE)
        
        for entry in name_counts:
            items = Item.objects.filter(
                name__iexact=entry['name_lower'],
                status=Item.ACTIVE
            ).order_by('id')
            if items.count() > 1:
                duplicates[entry['name_lower']] = list(items)
        
        return dict(duplicates)

    def find_duplicates_by_name_sku(self):
        """Find duplicates by name + SKU combination"""
        duplicates = defaultdict(list)
        
        # Find name+SKU combinations that appear more than once
        from django.db.models.functions import Lower, Concat
        from django.db.models import CharField, Value
        
        name_sku_counts = Item.objects.annotate(
            name_lower=Lower('name'),
            name_sku=Concat(
                Lower('name'),
                Value('|'),
                'sku',
                output_field=CharField()
            )
        ).values('name_sku').annotate(
            count=Count('id')
        ).filter(count__gt=1, status=Item.ACTIVE)
        
        for entry in name_sku_counts:
            name, sku = entry['name_sku'].split('|', 1)
            items = Item.objects.filter(
                name__iexact=name,
                sku=sku,
                status=Item.ACTIVE
            ).order_by('id')
            if items.count() > 1:
                duplicates[entry['name_sku']] = list(items)
        
        return dict(duplicates)

    def find_duplicates_by_name_slug(self):
        """Find duplicates by name + slug combination"""
        duplicates = defaultdict(list)
        
        # Find name+slug combinations that appear more than once
        from django.db.models.functions import Lower, Concat
        from django.db.models import CharField, Value
        
        name_slug_counts = Item.objects.annotate(
            name_lower=Lower('name'),
            name_slug=Concat(
                Lower('name'),
                Value('|'),
                'slug',
                output_field=CharField()
            )
        ).values('name_slug').annotate(
            count=Count('id')
        ).filter(count__gt=1, status=Item.ACTIVE)
        
        for entry in name_slug_counts:
            name, slug = entry['name_slug'].split('|', 1)
            items = Item.objects.filter(
                name__iexact=name,
                slug=slug,
                status=Item.ACTIVE
            ).order_by('id')
            if items.count() > 1:
                duplicates[entry['name_slug']] = list(items)
        
        return dict(duplicates)

    def select_item_to_keep(self, items, strategy):
        """Select which item to keep based on strategy"""
        if strategy == 'oldest':
            # Keep the one with oldest timestamp (or lowest ID if timestamp is same)
            return min(items, key=lambda x: (x.timestamp or x.id, x.id))
        elif strategy == 'newest':
            # Keep the one with newest timestamp (or highest ID if timestamp is same)
            return max(items, key=lambda x: (x.timestamp or x.id, x.id))
        elif strategy == 'highest_id':
            # Keep the one with highest ID
            return max(items, key=lambda x: x.id)
        elif strategy == 'most_complete':
            # Keep the one with most complete data
            def completeness_score(item):
                score = 0
                if item.description:
                    score += 1
                if item.image and item.image.name != 'idris/asset/default-item-image.jpg':
                    score += 1
                if item.mrp:
                    score += 1
                if item.salePrice:
                    score += 1
                if item.stock:
                    score += 1
                if item.metaTitle:
                    score += 1
                if item.metaDescription:
                    score += 1
                return score
            
            return max(items, key=completeness_score)
        else:
            # Default to oldest
            return min(items, key=lambda x: (x.timestamp or x.id, x.id))

    def delete_item_and_relations(self, items, soft_delete):
        """Delete items and all their related data"""
        deleted_count = 0
        
        for item in items:
            item_id = item.id
            
            # Get related data counts
            category_items_count = CategoryItem.objects.filter(itemId=item).count()
            bundle_items_count = BundleItem.objects.filter(itemId=item).count()
            wishlist_count = Wishlist.objects.filter(item=item).count()
            reviews_count = ProductReview.objects.filter(itemid=item).count()
            gallery_count = ItemGallery.objects.filter(itemId=item).count()
            
            # Delete related data
            if category_items_count > 0:
                CategoryItem.objects.filter(itemId=item).update(status=CategoryItem.DELETED)
            
            if bundle_items_count > 0:
                BundleItem.objects.filter(itemId=item).update(status=BundleItem.DELETED)
            
            if wishlist_count > 0:
                Wishlist.objects.filter(item=item).delete()
            
            if reviews_count > 0:
                ProductReview.objects.filter(itemid=item).delete()
            
            if gallery_count > 0:
                ItemGallery.objects.filter(itemId=item).update(status=ItemGallery.DELETED)
            
            # Delete or soft-delete the item
            if soft_delete:
                item.status = Item.DELETED
                item.save()
            else:
                item.delete()
            
            deleted_count += 1
        
        return deleted_count




