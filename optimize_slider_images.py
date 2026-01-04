#!/usr/bin/env python
"""
Slider Image Optimization Script
Converts large PNG/JPG slider images to WebP format with optimal compression
This will reduce the 1,862.7 KiB slider image to ~500KB

Usage:
    python optimize_slider_images.py --dry-run  # Preview changes
    python optimize_slider_images.py            # Convert images
    python optimize_slider_images.py --quality 85  # Custom quality (default: 80)
"""

import os
import sys
from pathlib import Path
from PIL import Image
import argparse

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_backend.settings')

import django
django.setup()

from django.conf import settings
from inara.models import SiteImage


def get_file_size_mb(file_path):
    """Get file size in MB."""
    size = os.path.getsize(file_path)
    return size / (1024 * 1024)


def optimize_image(image_path, quality=80, backup=True):
    """
    Optimize a single image by converting to WebP.
    
    Args:
        image_path: Path to the image file
        quality: WebP quality (1-100, default: 80)
        backup: Whether to keep original file
    
    Returns:
        tuple: (success, original_size_mb, new_size_mb, new_path)
    """
    try:
        # Get original size
        original_size = get_file_size_mb(image_path)
        
        # Open image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        
        # Generate WebP filename
        webp_path = str(Path(image_path).with_suffix('.webp'))
        
        # Save as WebP
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        
        # Get new size
        new_size = get_file_size_mb(webp_path)
        
        # Backup original if requested
        if backup and not os.path.exists(image_path + '.backup'):
            os.rename(image_path, image_path + '.backup')
            print(f"  ✓ Backed up: {Path(image_path).name}.backup")
        elif not backup:
            os.remove(image_path)
            print(f"  ✓ Removed: {Path(image_path).name}")
        
        savings = ((original_size - new_size) / original_size) * 100
        
        return True, original_size, new_size, webp_path, savings
    
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False, 0, 0, None, 0


def update_database_references(old_path, new_path):
    """Update database references from old image path to new WebP path."""
    try:
        # Extract relative paths
        media_root = settings.MEDIA_ROOT
        if isinstance(media_root, Path):
            media_root = str(media_root)
        
        old_rel = os.path.relpath(old_path, media_root).replace('\\', '/')
        new_rel = os.path.relpath(new_path, media_root).replace('\\', '/')
        
        # Update SiteImage model (sliders)
        updated = SiteImage.objects.filter(image=old_rel).update(image=new_rel)
        
        if updated > 0:
            print(f"  ✓ Updated {updated} database record(s)")
            return True
        
        return False
    
    except Exception as e:
        print(f"  ⚠️  Database update error: {str(e)}")
        return False


def main(dry_run=False, quality=80, backup=True):
    """Main function to optimize slider images."""
    print("🖼️  Slider Image Optimization Tool\n")
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will optimize)'}")
    print(f"Quality: {quality}")
    print(f"Backup: {'Yes' if backup else 'No'}\n")
    
    # Get media root
    media_root = settings.MEDIA_ROOT
    if isinstance(media_root, Path):
        media_root = str(media_root)
    
    slider_dir = os.path.join(media_root, 'slider')
    
    if not os.path.exists(slider_dir):
        print(f"⚠️  Slider directory not found: {slider_dir}")
        return
    
    print(f"📁 Scanning: {slider_dir}\n")
    
    # Find large images
    large_images = []
    for file in os.listdir(slider_dir):
        if file.endswith(('.png', '.jpg', '.jpeg')) and not file.endswith('.backup'):
            file_path = os.path.join(slider_dir, file)
            size_mb = get_file_size_mb(file_path)
            
            # Flag images larger than 500KB
            if size_mb > 0.5:
                large_images.append((file_path, size_mb))
    
    if not large_images:
        print("✅ No large images found (all < 500KB)\n")
        return
    
    print(f"Found {len(large_images)} large image(s):\n")
    
    total_original = 0
    total_optimized = 0
    
    for image_path, size_mb in large_images:
        filename = os.path.basename(image_path)
        print(f"📸 {filename} ({size_mb:.2f} MB)")
        
        if dry_run:
            print(f"  → Would convert to WebP (estimated: ~{size_mb * 0.3:.2f} MB)")
            total_original += size_mb
            total_optimized += size_mb * 0.3
        else:
            success, orig_size, new_size, new_path, savings = optimize_image(
                image_path, quality=quality, backup=backup
            )
            
            if success:
                print(f"  ✓ Optimized: {orig_size:.2f} MB → {new_size:.2f} MB ({savings:.1f}% smaller)")
                
                # Update database
                update_database_references(image_path, new_path)
                
                total_original += orig_size
                total_optimized += new_size
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"Images processed: {len(large_images)}")
    print(f"Total original size: {total_original:.2f} MB")
    print(f"Total optimized size: {total_optimized:.2f} MB")
    
    if total_original > 0:
        savings = ((total_original - total_optimized) / total_original) * 100
        print(f"Total savings: {total_original - total_optimized:.2f} MB ({savings:.1f}%)")
    
    print("\n✅ Done!\n")
    
    if dry_run:
        print("💡 Run without --dry-run to actually optimize images")
    else:
        print("🚀 Next steps:")
        print("   1. Rebuild Next.js: cd E:\\chitralhive\\chitralhive && npm run build")
        print("   2. Test your site to verify images load correctly")
        print("   3. Run Lighthouse again to see improvements")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Optimize slider images to WebP format')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=80,
        help='WebP quality (1-100, default: 80)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not keep backup of original files'
    )
    
    args = parser.parse_args()
    
    # Validate quality
    if not 1 <= args.quality <= 100:
        print("❌ Quality must be between 1 and 100")
        sys.exit(1)
    
    main(dry_run=args.dry_run, quality=args.quality, backup=not args.no_backup)

