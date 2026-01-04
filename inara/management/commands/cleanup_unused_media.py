"""
Django management command to clean up unused media files

This command scans your Django database for image references and identifies 
unused images/files in the media directory that can be safely removed.

Usage:
    python manage.py cleanup_unused_media              # Dry run (check only)
    python manage.py cleanup_unused_media --delete     # Actually delete files
"""

import os
import json
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from inara import models as inara_models


class Command(BaseCommand):
    help = 'Clean up unused media files (images) from the media directory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete unused files (default: dry run)',
        )

    def handle(self, *args, **options):
        dry_run = not options['delete']
        
        self.stdout.write(self.style.SUCCESS(
            '🔍 Scanning for unused images and files in Django media...\n'
        ))
        self.stdout.write(
            f"Mode: {'DRY RUN (no files will be deleted)' if dry_run else 'LIVE (files will be deleted)'}\n"
        )
        
        # Get MEDIA_ROOT from settings
        media_root = settings.MEDIA_ROOT
        if isinstance(media_root, Path):
            media_root = str(media_root)
        
        self.stdout.write(f"Media root: {media_root}\n")
        
        # Statistics
        stats = {
            'total_images': 0,
            'used_images': 0,
            'unused_images': 0,
            'deleted_files': 0,
            'errors': [],
        }
        
        # Step 1: Get all image references from database
        used_images = self.get_all_image_fields(stats)
        
        # Step 2: Get all image files from media directory
        all_images = self.get_all_image_files(media_root, stats)
        
        # Step 3: Identify unused images
        self.stdout.write('🔎 Identifying unused images...')
        unused_images = []
        used_image_list = []
        
        for image_info in all_images:
            if self.is_image_used(image_info, used_images):
                used_image_list.append(image_info)
                stats['used_images'] += 1
            else:
                unused_images.append(image_info)
                stats['unused_images'] += 1
        
        # Step 4: Display results
        self.stdout.write('\n📊 Results:')
        self.stdout.write(f"   Total images: {stats['total_images']}")
        self.stdout.write(f"   Used images: {stats['used_images']}")
        self.stdout.write(f"   Unused images: {stats['unused_images']}\n")
        
        if unused_images:
            self.stdout.write('🗑️  Unused images:')
            for i, img in enumerate(unused_images[:50], 1):  # Show first 50
                self.stdout.write(f"   {i}. {img['relative_path']}")
            
            if len(unused_images) > 50:
                self.stdout.write(f"   ... and {len(unused_images) - 50} more\n")
            else:
                self.stdout.write('')
            
            # Step 5: Delete unused images (if not dry run)
            if not dry_run:
                self.stdout.write('🗑️  Deleting unused images...')
                for img in unused_images:
                    try:
                        if os.path.exists(img['absolute_path']):
                            os.remove(img['absolute_path'])
                            stats['deleted_files'] += 1
                            self.stdout.write(
                                self.style.SUCCESS(f"   ✓ Deleted: {img['relative_path']}")
                            )
                    except Exception as e:
                        error_msg = f"Error deleting {img['relative_path']}: {str(e)}"
                        stats['errors'].append(error_msg)
                        self.stdout.write(
                            self.style.ERROR(f"   ✗ {error_msg}")
                        )
                self.stdout.write(f"\n   Deleted {stats['deleted_files']} files\n")
            else:
                self.stdout.write(
                    self.style.WARNING('💡 Run with --delete flag to actually delete these files\n')
                )
        else:
            self.stdout.write(self.style.SUCCESS('✅ No unused images found!\n'))
        
        # Display errors if any
        if stats['errors']:
            self.stdout.write(self.style.WARNING('⚠️  Errors encountered:'))
            for error in stats['errors']:
                self.stdout.write(f"   - {error}")
            self.stdout.write('')
        
        # Summary
        self.stdout.write('📈 Summary:')
        self.stdout.write(f"   Total images scanned: {stats['total_images']}")
        self.stdout.write(f"   Used: {stats['used_images']}")
        self.stdout.write(f"   Unused: {stats['unused_images']}")
        if not dry_run:
            self.stdout.write(f"   Deleted: {stats['deleted_files']}")
        self.stdout.write('')
        
        # Generate report file
        report_path = os.path.join(settings.BASE_DIR, 'unused-media-report.json')
        report = {
            'timestamp': datetime.now().isoformat(),
            'dry_run': dry_run,
            'media_root': media_root,
            'stats': {
                'total_images': stats['total_images'],
                'used_images': stats['used_images'],
                'unused_images': stats['unused_images'],
                'deleted_files': 0 if dry_run else stats['deleted_files'],
            },
            'unused_images': [
                {
                    'path': img['relative_path'],
                    'absolute_path': img['absolute_path'],
                    'filename': img['filename'],
                }
                for img in unused_images
            ],
            'errors': stats['errors'],
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(f"📄 Report saved to: {report_path}")

    def get_all_image_fields(self, stats):
        """Get all ImageField values from Django models."""
        used_images = set()
        
        # Define models and their image fields
        model_fields = [
            (inara_models.User, 'profile_pic'),
            (inara_models.Category, 'icon'),
            (inara_models.Item, 'image'),
            (inara_models.ItemGallery, 'image'),
            (inara_models.Bundle, 'image'),
            (inara_models.SiteSettings, 'site_logo'),
            (inara_models.SiteSettings, 'site_banner_image'),
            (inara_models.SiteSettings, 'site_splash'),
            (inara_models.SiteSettings, 'footer_logo'),
            (inara_models.SiteSettings, 'app_store'),
            (inara_models.SiteImage, 'image'),
            (inara_models.Voucher, 'image'),
        ]
        
        self.stdout.write('📊 Querying database for image references...')
        
        for model_class, field_name in model_fields:
            try:
                # Get all non-null image field values
                queryset = model_class.objects.exclude(**{f'{field_name}__isnull': True})
                queryset = queryset.exclude(**{f'{field_name}': ''})
                
                count = 0
                for obj in queryset:
                    image_field = getattr(obj, field_name, None)
                    if image_field:
                        # Get the relative path from MEDIA_ROOT
                        image_path = str(image_field)
                        if image_path:
                            used_images.add(image_path)
                            # Also add variations (with/without leading slash)
                            if not image_path.startswith('/'):
                                used_images.add('/' + image_path)
                            else:
                                used_images.add(image_path.lstrip('/'))
                            # Add just the filename
                            filename = os.path.basename(image_path)
                            if filename:
                                used_images.add(filename)
                            count += 1
                
                if count > 0:
                    self.stdout.write(
                        f"   {model_class.__name__}.{field_name}: {count} images"
                    )
            except Exception as e:
                error_msg = f"Error querying {model_class.__name__}.{field_name}: {str(e)}"
                stats['errors'].append(error_msg)
                self.stdout.write(self.style.WARNING(f"   ⚠️  {error_msg}"))
        
        self.stdout.write(f"\n   Found {len(used_images)} unique image references in database\n")
        return used_images

    def get_all_image_files(self, media_root, stats):
        """Get all image files from media directory."""
        image_files = []
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.avif']
        ignore_directories = ['__pycache__', '.git', 'node_modules']
        
        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING(f"⚠️  Media directory not found: {media_root}"))
            return image_files
        
        self.stdout.write(f'📁 Scanning media directory: {media_root}...')
        
        for root, dirs, files in os.walk(media_root):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_directories]
            
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in image_extensions:
                    # Get relative path from MEDIA_ROOT
                    rel_path = os.path.relpath(file_path, media_root)
                    # Normalize path separators
                    rel_path = rel_path.replace('\\', '/')
                    
                    image_files.append({
                        'absolute_path': file_path,
                        'relative_path': rel_path,
                        'filename': file,
                        'directory': os.path.dirname(rel_path),
                    })
        
        stats['total_images'] = len(image_files)
        self.stdout.write(f"   Found {len(image_files)} image files\n")
        return image_files

    def is_image_used(self, image_info, used_images):
        """Check if an image is referenced in the database."""
        rel_path = image_info['relative_path']
        filename = image_info['filename']
        
        # Check exact path match
        if rel_path in used_images:
            return True
        
        # Check path with leading slash
        if '/' + rel_path in used_images:
            return True
        
        # Check path without leading slash
        if rel_path.lstrip('/') in used_images:
            return True
        
        # Check filename match
        if filename in used_images:
            return True
        
        # Check if any used image path contains this filename
        for used_path in used_images:
            if filename in used_path or used_path in rel_path:
                return True
        
        return False

