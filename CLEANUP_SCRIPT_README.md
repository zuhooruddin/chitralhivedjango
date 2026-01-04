# Unused Media Files Cleanup Scripts

This directory contains scripts to identify and remove unused images and files from the Chitral Hive Django project.

## Available Scripts

### 1. `script.py` - Standalone Python Script

A standalone Python script that can be run directly.

**Usage:**
```bash
# Dry run (check only, no deletion)
python script.py

# Actually delete unused files
python script.py --delete
```

### 2. `inara/management/commands/cleanup_unused_media.py` - Django Management Command

A Django management command (recommended way to run).

**Usage:**
```bash
# Dry run (check only, no deletion)
python manage.py cleanup_unused_media

# Actually delete unused files
python manage.py cleanup_unused_media --delete
```

## What the Scripts Do

1. **Query Database**: Scans all Django models with `ImageField` to find referenced images:
   - `User.profile_pic`
   - `Category.icon`
   - `Item.image`
   - `ItemGallery.image`
   - `Bundle.image`
   - `SiteSettings.site_logo`
   - `SiteSettings.site_banner_image`
   - `SiteSettings.site_splash`
   - `SiteSettings.footer_logo`
   - `SiteSettings.app_store`
   - `SiteImage.image`
   - `Voucher.image`

2. **Scan Media Directory**: Lists all image files in the `media/` directory

3. **Compare**: Identifies images that exist in the media directory but are not referenced in the database

4. **Report**: Generates a JSON report (`unused-media-report.json`) with:
   - List of unused images
   - Statistics (total, used, unused)
   - Any errors encountered

5. **Delete** (optional): Removes unused images if `--delete` flag is used

## Requirements

- Django project must be properly configured
- Database must be accessible (PostgreSQL, SQLite, etc.)
- Python 3.x

## Safety Features

- **Dry Run by Default**: Scripts run in dry-run mode unless `--delete` is explicitly used
- **Detailed Reporting**: Always generates a report before deletion
- **Error Handling**: Continues processing even if some operations fail
- **Path Normalization**: Handles different path formats (Windows/Unix)

## Example Output

```
🔍 Scanning for unused images and files in Django media...

Mode: DRY RUN (no files will be deleted)

Media root: E:\chitralhive\chitralhivedjango\media

📊 Querying database for image references...
   User.profile_pic: 150 images
   Category.icon: 45 images
   Item.image: 1200 images
   ...
   Found 1450 unique image references in database

📁 Scanning media directory...
   Found 2000 image files

🔎 Identifying unused images...

📊 Results:
   Total images: 2000
   Used images: 1450
   Unused images: 550

🗑️  Unused images:
   1. item_image/old-product-1.jpg
   2. item_image/old-product-2.jpg
   ...

💡 Run with --delete flag to actually delete these files

📈 Summary:
   Total images scanned: 2000
   Used: 1450
   Unused: 550

📄 Report saved to: unused-media-report.json
```

## Important Notes

1. **Always run in dry-run mode first** to review what will be deleted
2. **Backup your database** before running with `--delete`
3. **Check the report** (`unused-media-report.json`) before deleting
4. The script handles Django's file field paths correctly (relative to MEDIA_ROOT)
5. Images are matched by:
   - Exact path match
   - Filename match
   - Partial path matching

## Troubleshooting

### Database Connection Errors

If you see database connection errors, make sure:
- Your database server is running
- Database credentials in `settings.py` are correct
- You're using the correct database (check `DATABASES` in settings)

### Permission Errors

If you get permission errors when deleting:
- Make sure you have write permissions to the media directory
- On Linux/Mac, you may need to use `sudo` (not recommended - fix permissions instead)

## Related Files

- `CLEANUP_UNUSED_MEDIA.md` - Previous cleanup documentation
- `unused-media-report.json` - Generated report (created after running script)

