"""
Django management command to optimize images in the media folder.
This command will:
1. Convert PNG images to WebP format with compression
2. Resize large images to reasonable dimensions
3. Maintain aspect ratio
4. Create backups of original images

Usage:
    python manage.py optimize_images
    python manage.py optimize_images --path=media/slider
    python manage.py optimize_images --quality=85 --max-width=1920
"""

from django.core.management.base import BaseCommand, CommandError
from PIL import Image
import os
from pathlib import Path
from django.conf import settings
import shutil


class Command(BaseCommand):
    help = 'Optimize images in the media folder by converting to WebP and resizing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default='media',
            help='Relative path to images folder (default: media)',
        )
        parser.add_argument(
            '--quality',
            type=int,
            default=85,
            help='WebP quality 0-100 (default: 85)',
        )
        parser.add_argument(
            '--max-width',
            type=int,
            default=1920,
            help='Maximum width for images (default: 1920)',
        )
        parser.add_argument(
            '--max-height',
            type=int,
            default=1080,
            help='Maximum height for images (default: 1080)',
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create backup of original images',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )

    def handle(self, *args, **options):
        media_path = Path(options['path'])
        quality = options['quality']
        max_width = options['max_width']
        max_height = options['max_height']
        create_backup = options['backup']
        dry_run = options['dry_run']

        if not media_path.exists():
            raise CommandError(f'Path does not exist: {media_path}')

        self.stdout.write(self.style.SUCCESS(f'🔍 Scanning for images in: {media_path}'))
        
        # Find all PNG and JPG images
        image_extensions = ['*.png', '*.PNG', '*.jpg', '*.JPG', '*.jpeg', '*.JPEG']
        image_files = []
        for ext in image_extensions:
            image_files.extend(media_path.rglob(ext))

        if not image_files:
            self.stdout.write(self.style.WARNING('⚠️  No images found to optimize'))
            return

        self.stdout.write(f'📸 Found {len(image_files)} images to optimize')
        
        total_original_size = 0
        total_optimized_size = 0
        optimized_count = 0
        skipped_count = 0

        for image_path in image_files:
            try:
                original_size = image_path.stat().st_size
                total_original_size += original_size
                
                # Skip if already has a WebP version
                webp_path = image_path.with_suffix('.webp')
                if webp_path.exists() and webp_path.stat().st_size < original_size:
                    self.stdout.write(
                        self.style.WARNING(f'⏭️  Skipping {image_path.name} (WebP version exists)')
                    )
                    skipped_count += 1
                    continue

                if dry_run:
                    self.stdout.write(
                        self.style.NOTICE(
                            f'Would optimize: {image_path.name} '
                            f'({self.format_size(original_size)})'
                        )
                    )
                    continue

                # Open and optimize image
                with Image.open(image_path) as img:
                    # Convert RGBA/LA/P to RGB
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparency
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background

                    # Resize if needed
                    original_dimensions = img.size
                    if img.width > max_width or img.height > max_height:
                        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                        self.stdout.write(
                            f'   Resized from {original_dimensions[0]}x{original_dimensions[1]} '
                            f'to {img.size[0]}x{img.size[1]}'
                        )

                    # Create backup if requested
                    if create_backup:
                        backup_path = image_path.with_suffix(image_path.suffix + '.backup')
                        if not backup_path.exists():
                            shutil.copy2(image_path, backup_path)

                    # Save as WebP
                    img.save(
                        webp_path,
                        'WEBP',
                        quality=quality,
                        method=6,  # Better compression
                        optimize=True
                    )

                    optimized_size = webp_path.stat().st_size
                    total_optimized_size += optimized_size
                    optimized_count += 1
                    
                    savings = original_size - optimized_size
                    savings_percent = (savings / original_size) * 100 if original_size > 0 else 0

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ {image_path.name} → {webp_path.name}\n'
                            f'   Original: {self.format_size(original_size)} → '
                            f'Optimized: {self.format_size(optimized_size)}\n'
                            f'   Saved: {self.format_size(savings)} ({savings_percent:.1f}%)'
                        )
                    )

                    # Optionally remove original PNG/JPG if WebP is significantly smaller
                    if optimized_size < original_size * 0.7:  # WebP is at least 30% smaller
                        self.stdout.write(
                            self.style.NOTICE(
                                f'   💡 Consider removing {image_path.name} to save space'
                            )
                        )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error optimizing {image_path.name}: {str(e)}')
                )
                continue

        # Summary
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.NOTICE('DRY RUN - No changes made'))
        else:
            self.stdout.write(self.style.SUCCESS('📊 Optimization Summary:'))
            self.stdout.write(f'   Images optimized: {optimized_count}')
            self.stdout.write(f'   Images skipped: {skipped_count}')
            if optimized_count > 0:
                self.stdout.write(
                    f'   Total original size: {self.format_size(total_original_size)}'
                )
                self.stdout.write(
                    f'   Total optimized size: {self.format_size(total_optimized_size)}'
                )
                total_savings = total_original_size - total_optimized_size
                total_savings_percent = (
                    (total_savings / total_original_size) * 100 
                    if total_original_size > 0 else 0
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'   Total saved: {self.format_size(total_savings)} '
                        f'({total_savings_percent:.1f}%)'
                    )
                )
        self.stdout.write('='*60)

    def format_size(self, size_bytes):
        """Format size in bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'

