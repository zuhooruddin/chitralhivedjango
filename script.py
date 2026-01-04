#!/usr/bin/env python
"""
Unused Images and Files Cleanup Script for Django

This script scans your Django database for image references and identifies 
unused images/files in the media directory that can be safely removed.

Usage:
    - Dry run (check only, no deletion):  python script.py
    - Delete unused files:                 python script.py --delete
    - Using Django management command:     python manage.py cleanup_unused_media
                                           python manage.py cleanup_unused_media --delete

The script will:

    1. Query all ImageField values from Django models
    2. List all images in media directory
    3. Identify which images are not referenced in database
    4. Generate a report (unused-media-report.json)
    5. Optionally delete unused images (if --delete flag is used)

Note: Always run in dry-run mode first to review what will be deleted!
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')

import django
django.setup()

from django.conf import settings
from django.db import models
from inara import models as inara_models


# Configuration
CONFIG = {
    # Image file extensions to check
    'image_extensions': ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico', '.avif'],
    # Directories to ignore (relative to MEDIA_ROOT)
    'ignore_directories': ['__pycache__', '.git', 'node_modules'],
    # Dry run mode (set to False to actually delete files)
    'dry_run': True,
}

# Statistics
stats = {
    'total_images': 0,
    'used_images': 0,
    'unused_images': 0,
    'deleted_files': 0,
    'errors': [],
}


def get_all_image_fields():
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
    
    print('📊 Querying database for image references...')
    
    for model_class, field_name in model_fields:
        try:
            # Get all non-null image field values
            queryset = model_class.objects.exclude(**{f'{field_name}__isnull': True})
            queryset = queryset.exclude(**{f'{field_name}': ''})
            
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
        except Exception as e:
            error_msg = f"Error querying {model_class.__name__}.{field_name}: {str(e)}"
            stats['errors'].append(error_msg)
            print(f"   ⚠️  {error_msg}")
    
    print(f"   Found {len(used_images)} unique image references in database\n")
    return used_images


def get_all_image_files(media_root):
    """Get all image files from media directory."""
    image_files = []
    
    if not os.path.exists(media_root):
        print(f"⚠️  Media directory not found: {media_root}")
        return image_files
    
    print(f'📁 Scanning media directory: {media_root}...')
    
    for root, dirs, files in os.walk(media_root):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in CONFIG['ignore_directories']]
        
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file)[1].lower()
            
            if file_ext in CONFIG['image_extensions']:
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
    print(f"   Found {len(image_files)} image files\n")
    return image_files


def is_image_used(image_info, used_images):
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


def main(dry_run=True):
    """Main function."""
    print('🔍 Scanning for unused images and files in Django media...\n')
    print(f"Mode: {'DRY RUN (no files will be deleted)' if dry_run else 'LIVE (files will be deleted)'}\n")
    
    # Get MEDIA_ROOT from settings
    media_root = settings.MEDIA_ROOT
    if isinstance(media_root, Path):
        media_root = str(media_root)
    
    print(f"Media root: {media_root}\n")
    
    # Step 1: Get all image references from database
    used_images = get_all_image_fields()
    
    # Step 2: Get all image files from media directory
    all_images = get_all_image_files(media_root)
    
    # Step 3: Identify unused images
    print('🔎 Identifying unused images...')
    unused_images = []
    used_image_list = []
    
    for image_info in all_images:
        if is_image_used(image_info, used_images):
            used_image_list.append(image_info)
            stats['used_images'] += 1
        else:
            unused_images.append(image_info)
            stats['unused_images'] += 1
    
    # Step 4: Display results
    print('\n📊 Results:')
    print(f"   Total images: {stats['total_images']}")
    print(f"   Used images: {stats['used_images']}")
    print(f"   Unused images: {stats['unused_images']}\n")
    
    if unused_images:
        print('🗑️  Unused images:')
        for i, img in enumerate(unused_images[:50], 1):  # Show first 50
            print(f"   {i}. {img['relative_path']}")
        
        if len(unused_images) > 50:
            print(f"   ... and {len(unused_images) - 50} more\n")
        else:
            print('')
        
        # Step 5: Delete unused images (if not dry run)
        if not dry_run:
            print('🗑️  Deleting unused images...')
            for img in unused_images:
                try:
                    if os.path.exists(img['absolute_path']):
                        os.remove(img['absolute_path'])
                        stats['deleted_files'] += 1
                        print(f"   ✓ Deleted: {img['relative_path']}")
                except Exception as e:
                    error_msg = f"Error deleting {img['relative_path']}: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"   ✗ {error_msg}")
            print(f"\n   Deleted {stats['deleted_files']} files\n")
        else:
            print('💡 Run with --delete flag to actually delete these files\n')
    else:
        print('✅ No unused images found!\n')
    
    # Display errors if any
    if stats['errors']:
        print('⚠️  Errors encountered:')
        for error in stats['errors']:
            print(f"   - {error}")
        print('')
    
    # Summary
    print('📈 Summary:')
    print(f"   Total images scanned: {stats['total_images']}")
    print(f"   Used: {stats['used_images']}")
    print(f"   Unused: {stats['unused_images']}")
    if not dry_run:
        print(f"   Deleted: {stats['deleted_files']}")
    print('')
    
    # Generate report file
    report_path = os.path.join(BASE_DIR, 'unused-media-report.json')
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
    
    print(f"📄 Report saved to: {report_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean up unused media files in Django project')
    parser.add_argument(
        '--delete',
        action='store_true',
        help='Actually delete unused files (default: dry run)'
    )
    
    args = parser.parse_args()
    main(dry_run=not args.delete)

