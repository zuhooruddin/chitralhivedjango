"""
Django management command to set up home page sections with ChitralHive categories
Run: python manage.py setup_homepage_sections
"""
import re
from django.core.management.base import BaseCommand
from inara.models import Category, Individual_BoxOrder, Configuration, SectionSequence


class Command(BaseCommand):
    help = 'Set up home page sections with ChitralHive categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing Individual_BoxOrder and SectionSequence data before setting up',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up home page sections...'))
        
        # Step 1: Clear old placeholder data
        self.clear_old_data(clear_all=options['clear'])
        
        # Step 1.5: Clean up placeholder categories (set showAtHome=0)
        self.cleanup_placeholder_categories()
        
        # Step 2: Get ChitralHive categories
        categories = self.get_chitralhive_categories()
        
        if not categories:
            self.stdout.write(self.style.ERROR('No ChitralHive categories found! Run seed_chitralhive_seo first.'))
            return
        
        # Step 3: Create Individual Box Orders
        boxes_created = self.create_individual_box_orders(categories)
        
        # Step 4: Set up Configuration
        self.setup_configuration(len(categories))
        
        # Step 5: Create Section Sequences (optional)
        sections_created = self.create_section_sequences(categories)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully set up:\n'
            f'   - Individual Box Orders: {boxes_created}\n'
            f'   - Section Sequences: {sections_created}\n'
            f'   - Configuration updated\n'
            f'Home page sections are now configured!'
        ))

    def clear_old_data(self, clear_all=False):
        """Clear old placeholder Individual_BoxOrder entries"""
        if clear_all:
            self.stdout.write('Clearing all existing data...')
            Individual_BoxOrder.objects.all().delete()
            SectionSequence.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All data cleared'))
        else:
            # Remove Individual_BoxOrder entries that reference placeholder categories
            self.stdout.write('Removing placeholder category entries...')
            
            # Find placeholder categories (Category1, Category2, Category 1, etc.)
            placeholder_pattern = re.compile(r'^Category\s*\d+$', re.IGNORECASE)
            placeholder_categories = Category.objects.filter(
                name__iregex=r'^Category\s*\d+$'
            )
            
            if placeholder_categories.exists():
                placeholder_ids = list(placeholder_categories.values_list('id', flat=True))
                
                # Remove Individual_BoxOrder entries referencing placeholder categories
                deleted_boxes = Individual_BoxOrder.objects.filter(
                    category_id__in=placeholder_ids
                ).delete()
                
                # Remove SectionSequence entries referencing placeholder categories
                deleted_sections = SectionSequence.objects.filter(
                    category__in=placeholder_ids
                ).delete()
                
                self.stdout.write(self.style.SUCCESS(
                    f'Removed {deleted_boxes[0]} Individual_BoxOrder entries and '
                    f'{deleted_sections[0]} SectionSequence entries for placeholder categories'
                ))
            else:
                self.stdout.write('No placeholder categories found')
            
            # Also remove entries with placeholder names directly in Individual_BoxOrder
            deleted_direct = Individual_BoxOrder.objects.filter(
                category_name__iregex=r'^Category\s*\d+$'
            ).delete()
            
            if deleted_direct[0] > 0:
                self.stdout.write(self.style.SUCCESS(
                    f'Removed {deleted_direct[0]} Individual_BoxOrder entries with placeholder names'
                ))

    def cleanup_placeholder_categories(self):
        """Disable placeholder categories so they don't appear on home page"""
        placeholder_categories = Category.objects.filter(
            name__iregex=r'^Category\s*\d+$'
        )
        
        if placeholder_categories.exists():
            count = placeholder_categories.update(
                showAtHome=0,  # Hide from home page
                status=Category.INACTIVE  # Set as inactive
            )
            self.stdout.write(self.style.SUCCESS(
                f'Disabled {count} placeholder categories (Category1, Category2, etc.)'
            ))
        else:
            self.stdout.write('No placeholder categories to clean up')

    def get_chitralhive_categories(self):
        """Get ChitralHive categories that should appear on home page (SEO-optimized)"""
        # Get all eligible categories, excluding placeholder categories
        all_categories = Category.objects.filter(
            parentId=None,
            isBrand=False,
            status=Category.ACTIVE,
            showAtHome=1
        ).exclude(
            slug__isnull=True
        ).exclude(
            slug=''
        ).exclude(
            name__iregex=r'^Category\s*\d+$'  # Exclude Category1, Category2, etc.
        )
        
        # Separate categories with and without SEO fields
        categories_with_seo = []
        categories_without_seo = []
        
        for cat in all_categories:
            if cat.metaUrl or cat.metaTitle or cat.metaDescription:
                categories_with_seo.append(cat)
            else:
                categories_without_seo.append(cat)
        
        # Sort: SEO-optimized first, then by priority, then by ID
        categories_with_seo.sort(key=lambda x: (x.priority or 0, x.id))
        categories_without_seo.sort(key=lambda x: (x.priority or 0, x.id))
        
        # Combine: SEO categories first, then others
        categories_list = categories_with_seo + categories_without_seo
        categories_list = categories_list[:8]  # Get first 8 categories
        
        # Log SEO status
        self.stdout.write('Categories selected (SEO-optimized):')
        for cat in categories_list:
            seo_status = []
            if cat.metaUrl:
                seo_status.append('metaUrl')
            if cat.metaTitle:
                seo_status.append('metaTitle')
            if cat.metaDescription:
                seo_status.append('metaDescription')
            
            if seo_status:
                self.stdout.write(self.style.SUCCESS(f'  ✓ {cat.name}: SEO fields: {", ".join(seo_status)}'))
            else:
                self.stdout.write(self.style.WARNING(f'  ⚠ {cat.name}: No SEO fields (using slug: {cat.slug})'))
        
        return categories_list

    def create_individual_box_orders(self, categories):
        """Create Individual_BoxOrder entries for categories"""
        boxes_created = 0
        
        # Create section entries first (type='section')
        # Section 1: sequenceNo=1, type='section'
        # Section 2: sequenceNo=2, type='section'
        if len(categories) >= 2:
            for section_idx in [1, 2]:
                if section_idx <= len(categories):
                    category = categories[section_idx - 1]
                    
                    # Skip placeholder categories
                    if re.match(r'^Category\s*\d+$', category.name, re.IGNORECASE):
                        self.stdout.write(self.style.WARNING(f'Skipping placeholder category: {category.name}'))
                        continue
                    
                    icon_path = category.icon.name if category.icon else 'category_icon/default-category-icon.jpg'
                    
                    # Use SEO-friendly slug (metaUrl if available, otherwise slug)
                    seo_slug = category.metaUrl if category.metaUrl else category.slug
                    
                    section_order, created = Individual_BoxOrder.objects.update_or_create(
                        sequenceNo=section_idx,
                        type='section',
                        defaults={
                            'category_id': category,
                            'category_slug': seo_slug,  # SEO-optimized URL
                            'category_name': category.metaTitle if category.metaTitle else category.name,
                            'image': icon_path,
                            'parent': None,
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created section {section_idx}: {category.name}'))
                    boxes_created += 1
                    
                    # Create section_subcategory entries for child categories
                    child_categories = Category.objects.filter(
                        parentId=category.id,
                        status=Category.ACTIVE
                    )[:5]  # Max 5 subcategories per section
                    
                    for child_idx, child_cat in enumerate(child_categories):
                        # Skip placeholder subcategories
                        if re.match(r'^Category\s*\d+$', child_cat.name, re.IGNORECASE):
                            continue
                        
                        child_icon = child_cat.icon.name if child_cat.icon else 'category_icon/default-category-icon.jpg'
                        
                        # Use SEO-friendly slug for subcategories
                        child_seo_slug = child_cat.metaUrl if child_cat.metaUrl else child_cat.slug
                        
                        # Use category_id and parent to uniquely identify subcategories
                        subcat_order, sub_created = Individual_BoxOrder.objects.update_or_create(
                            type='section_subcategory',
                            category_id=child_cat,
                            parent=category.id,
                            defaults={
                                'sequenceNo': child_idx + 1,  # 1-based index per section
                                'category_slug': child_seo_slug,  # SEO-optimized URL
                                'category_name': child_cat.metaTitle if child_cat.metaTitle else child_cat.name,
                                'image': child_icon,
                            }
                        )
                        
                        if sub_created:
                            self.stdout.write(self.style.SUCCESS(f'  Created subcategory: {child_cat.name}'))
                        boxes_created += 1
        
        # Create box entries (type='box')
        # Section 1: Boxes 1-2
        # Section 2: Boxes 3-8
        box_sequence = [
            (1, 1),   # Section 1, Box 1
            (2, 1),   # Section 1, Box 2
            (3, 2),   # Section 2, Box 1
            (4, 2),   # Section 2, Box 2
            (5, 2),   # Section 2, Box 3
            (6, 2),   # Section 2, Box 4
            (7, 2),   # Section 2, Box 5
            (8, 2),   # Section 2, Box 6
        ]
        
        for idx, (sequence_no, section_no) in enumerate(box_sequence):
            if idx >= len(categories):
                break
                
            category = categories[idx]
            
            # Skip placeholder categories
            if re.match(r'^Category\s*\d+$', category.name, re.IGNORECASE):
                self.stdout.write(self.style.WARNING(f'Skipping placeholder category: {category.name}'))
                continue
            
            # Get category icon or use default
            icon_path = category.icon.name if category.icon else 'category_icon/default-category-icon.jpg'
            
            # Use SEO-friendly slug (metaUrl if available, otherwise slug)
            seo_slug = category.metaUrl if category.metaUrl else category.slug
            
            # Create or update Individual_BoxOrder with SEO-optimized fields
            box_order, created = Individual_BoxOrder.objects.update_or_create(
                sequenceNo=sequence_no,
                type='box',
                defaults={
                    'category_id': category,
                    'category_slug': seo_slug,  # SEO-optimized URL
                    'category_name': category.metaTitle if category.metaTitle else category.name,
                    'image': icon_path,
                    'parent': None,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created box {sequence_no}: {category.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated box {sequence_no}: {category.name}'))
            
            boxes_created += 1
        
        return boxes_created

    def setup_configuration(self, num_boxes):
        """Set up Configuration for number of sections and boxes"""
        self.stdout.write('Setting up configuration...')
        
        # Set number of boxes
        Configuration.objects.update_or_create(
            name='box',
            defaults={'value': str(num_boxes), 'location': 'homepage'}
        )
        
        # Set number of sections (calculate based on boxes)
        # Section 1: 2 boxes, Section 2: 6 boxes, Section 3: 3 boxes, etc.
        num_sections = 3  # Adjust based on your layout
        
        Configuration.objects.update_or_create(
            name='section',
            defaults={'value': str(num_sections), 'location': 'homepage'}
        )
        
        self.stdout.write(self.style.SUCCESS(f'Configuration set: {num_sections} sections, {num_boxes} boxes'))

    def create_section_sequences(self, categories):
        """Create SectionSequence entries for category sections"""
        sections_created = 0
        
        # Create section sequences for main categories
        # Each section can have child categories displayed
        section_categories = categories[:3]  # First 3 categories as sections
        
        for idx, category in enumerate(section_categories, start=1):
            # Get child categories (subcategories) if any
            child_categories = Category.objects.filter(
                parentId=category.id,
                status=Category.ACTIVE
            )[:7]  # Max 7 children
            
            # Use SEO-friendly slug for section
            seo_slug = category.metaUrl if category.metaUrl else category.slug
            
            # Create SectionSequence with SEO-optimized fields
            section_seq, created = SectionSequence.objects.update_or_create(
                sequenceNo=idx,
                defaults={
                    'category': category,
                    'category_slug': seo_slug,  # SEO-optimized URL
                    'name': category.metaTitle if category.metaTitle else category.name,
                }
            )
            
            # Set child categories with SEO fields
            child_fields = ['child1', 'child2', 'child3', 'child4', 'child5', 'child6', 'child7']
            for i, child_cat in enumerate(child_categories[:7]):
                field_name = child_fields[i]
                name_field = f'{field_name}_name'
                slug_field = f'{field_name}_slug'
                
                # Use SEO-friendly slug for child
                child_seo_slug = child_cat.metaUrl if child_cat.metaUrl else child_cat.slug
                
                setattr(section_seq, field_name, child_cat)
                setattr(section_seq, name_field, child_cat.metaTitle if child_cat.metaTitle else child_cat.name)
                setattr(section_seq, slug_field, child_seo_slug)  # SEO-optimized URL
            
            section_seq.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created section {idx}: {category.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated section {idx}: {category.name}'))
            
            sections_created += 1
        
        return sections_created

