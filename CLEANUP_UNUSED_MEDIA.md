# 🗑️ Cleanup Unused Media Files (Django Backend)

## Quick Start

### Find Unused Media Files (Safe - No Deletion)

```bash
cd E:\chitralhive\chitralhivedjango
python manage.py find_unused_media
```

### Find Unused Files in Specific Folder

```bash
python manage.py find_unused_media --path=media/slider
python manage.py find_unused_media --path=media/category_icon
python manage.py find_unused_media --path=media/item_image
```

### Delete Unused Files (⚠️ WARNING: Actually Deletes!)

```bash
python manage.py find_unused_media --delete
```

### Dry Run (Preview Only)

```bash
python manage.py find_unused_media --dry-run
```

### Save Report to File

```bash
python manage.py find_unused_media --output=unused_media_report.json
```

---

## What It Does

The command:
1. ✅ Scans all media files in the specified directory
2. ✅ Checks database references (all ImageField/FileField values)
3. ✅ Checks code references (searches Python, JS, HTML, CSS files)
4. ✅ Identifies files that are not referenced anywhere
5. ✅ Generates a detailed JSON report
6. ✅ Optionally deletes unused files (with 5-second warning)

## Supported File Types

The command checks for:
- **Images:** `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`
- **Searches in:** Database fields, `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.html`, `.css`, `.json`

## Usage Examples

### Example 1: Find All Unused Media

```bash
python manage.py find_unused_media
```

**Output:**
```
🔍 Scanning for unused media files in: media
📸 Found 794 media files
🔎 Checking database references...
🔎 Checking code references...
📊 Found 456 unique references

📊 Scan Summary:
   Total files scanned: 794
   Used files: 456
   Unused files: 338
   Total unused size: 45.2 MB

🗑️  Unused Files (Top 20 by size):
   1. slider/old-banner.png (1.86 MB)
   2. category_icon/old-icon.png (1.21 MB)
   ...

📄 Report saved to: media/unused_media_report.json

💡 To delete these files, run:
   python manage.py find_unused_media --delete
```

### Example 2: Find Unused Slider Images Only

```bash
python manage.py find_unused_media --path=media/slider
```

### Example 3: Find Large Unused Files (>1MB)

```bash
python manage.py find_unused_media --min-size=1048576
```

### Example 4: Preview Before Deleting

```bash
# Step 1: Generate report
python manage.py find_unused_media --output=unused_report.json

# Step 2: Review the report
cat unused_report.json

# Step 3: Delete if safe
python manage.py find_unused_media --delete
```

### Example 5: Delete Unused Files

```bash
python manage.py find_unused_media --delete
```

**Warning:** You'll get a 5-second countdown to cancel (Ctrl+C)

---

## Report Format

The generated JSON report contains:

```json
{
  "timestamp": "2026-01-03T12:00:00.000000",
  "total_scanned": 794,
  "total_used": 456,
  "total_unused": 338,
  "total_unused_size": 47395635,
  "total_unused_size_formatted": "45.2 MB",
  "files": [
    {
      "path": "E:\\chitralhive\\chitralhivedjango\\media\\slider\\old-banner.png",
      "relative_path": "slider/old-banner.png",
      "size": 1951744,
      "size_formatted": "1.86 MB"
    }
  ]
}
```

## How It Works

### 1. Database Scanning

The command scans all Django models for:
- `ImageField` fields
- `FileField` fields
- Extracts all file paths from the database

### 2. Code Scanning

The command searches code files for:
- String literals containing image paths
- Patterns like `media/...`, `slider/...`, `category_icon/...`
- File names referenced in code

### 3. Matching

A file is considered **unused** if:
- ❌ Not found in any database field
- ❌ Not referenced in any code file
- ❌ Filename not found in references

## Safety Features

1. **Dry Run by Default** - Only scans and reports, doesn't delete
2. **5-Second Warning** - When using `--delete`, gives you time to cancel
3. **Detailed Report** - JSON report saved before deletion
4. **Sorted by Size** - Shows largest files first (biggest impact)
5. **Path Filtering** - Can scan specific folders only

## Common Use Cases

### 1. Clean Up After Removing Products

After deleting products from database:
```bash
# Find orphaned product images
python manage.py find_unused_media --path=media/item_image

# Review and delete
python manage.py find_unused_media --path=media/item_image --delete
```

### 2. Remove Old Slider Images

```bash
# Find unused slider images
python manage.py find_unused_media --path=media/slider

# Delete if safe
python manage.py find_unused_media --path=media/slider --delete
```

### 3. Find Large Unused Files

```bash
# Find files larger than 500KB
python manage.py find_unused_media --min-size=512000
```

### 4. Regular Maintenance

Add to your monthly maintenance:
```bash
# Generate report
python manage.py find_unused_media --output=monthly_cleanup.json

# Review report
# Delete if safe
python manage.py find_unused_media --delete
```

## Important Notes

### ⚠️ False Positives

The command may flag files as unused if they're:
- Referenced dynamically (e.g., `getattr(model, field_name)`)
- Used in templates with variables
- Referenced in external APIs
- Used in JavaScript with dynamic paths

**Always review the report before deleting!**

### ✅ Safe to Delete

These are typically safe to delete:
- Old slider images replaced by new ones
- Unused product images (after product deletion)
- Deprecated category icons
- Backup files (`.backup`, `.old`)
- Test/demo images

### ❌ Be Careful With

- Files referenced in environment variables
- Files used by external services
- Files that might be used in the future
- Files referenced in migrations

## Integration with Image Optimization

After optimizing images, you might have:
- Original PNG files (if you kept backups)
- Duplicate WebP files
- Old optimized versions

Run this command to find and clean them up:

```bash
# 1. Optimize images (creates backups)
python manage.py optimize_images --backup

# 2. Find unused originals
python manage.py find_unused_media --path=media/backups

# 3. Review and delete if safe
python manage.py find_unused_media --path=media/backups --delete
```

## Troubleshooting

### Permission Errors

If you get permission errors:
```bash
# On Linux/Mac
sudo python manage.py find_unused_media --delete

# On Windows
# Run command prompt as Administrator
```

### Database Connection Issues

If database scanning fails:
- The command will still work with code scanning only
- You'll see a warning message
- Results may be less accurate

### Large Codebase

For very large codebases:
- The code scanning may take a few minutes
- Progress is shown during execution
- Consider using `--path` to scan specific folders

## Expected Savings

After cleanup, you might save:
- **Small projects:** 10-50 MB
- **Medium projects:** 50-200 MB
- **Large projects:** 200-1000 MB+

This improves:
- ✅ Backup times
- ✅ Storage costs
- ✅ Database performance (if using file fields)
- ✅ Deployment size

## Command Options

| Option | Description |
|--------|-------------|
| `--path=PATH` | Scan specific folder (default: `media`) |
| `--delete` | Actually delete unused files |
| `--dry-run` | Preview only (no deletion) |
| `--min-size=BYTES` | Only report files larger than this |
| `--output=FILE` | Save report to specific file |

## Quick Reference

```bash
# Find unused files
python manage.py find_unused_media

# Find in specific folder
python manage.py find_unused_media --path=media/slider

# Find large files only
python manage.py find_unused_media --min-size=1048576

# Preview (dry run)
python manage.py find_unused_media --dry-run

# Delete unused files
python manage.py find_unused_media --delete

# Save report
python manage.py find_unused_media --output=report.json
```

---

**Last Updated:** January 3, 2026  
**Status:** ✅ Ready to use

