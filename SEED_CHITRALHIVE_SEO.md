# ChitralHive SEO-Friendly Data Seeding Guide

This guide explains how to seed ChitralHive with SEO-friendly categories, subcategories, products, and bundles.

## Overview

The seed command creates:
- **Categories** with SEO-friendly URLs (e.g., `/categories/chitrali-dry-fruits`)
- **Subcategories** with proper parent relationships
- **Products** with SEO URLs (e.g., `/products/chitrali-almonds-100g-100001`)
- **Bundles** with SEO URLs (e.g., `/bundles/chitrali-dry-fruits-combo-pack`)

All entries include:
- ✅ SEO-friendly slugs
- ✅ Meta URLs
- ✅ Meta titles
- ✅ Meta descriptions
- ✅ Proper database relationships

## Running the Seed Command

### Basic Usage

```bash
cd /var/www/chitralhive/api
source venv/bin/activate
python manage.py seed_chitralhive_seo
```

### What Gets Created

1. **Main Category**: "Chitrali Products"
   - URL: `/categories/chitrali-products`
   - SEO Title: "Chitrali Products - Authentic Chitral Products Online | ChitralHive"

2. **1






 Main Categories**:
   - Dry Fruits (`/categories/chitrali-dry-fruits`) - 600 products
   - Salajit (`/categories/chitrali-salajit`) - 200 products
   - Chitrali Herbs (`/categories/chitrali-herbs`
   
   
    - 300 products
   - Chitrali Honey (`/categories/chitrali-honey`) - 150 products
   - Chitrali Nuts (`/categories/chitrali-nuts`) - 250 products
   - Chitrali Spices (`/categories/chitrali-spices`) - 200 products
   - Chitrali Apricots (`/categories/chitrali-apricots`) - 150 products
   - Chitrali Grains (`/categories/chitrali-grains`) - 150 products
   - Chitrali Oils (`/categories/chitrali-oils`) - 100 products
   - Chitrali Tea (`/categories/chitrali-tea`) - 80 products
   - Chitrali Jams & Preserves (`/categories/chitrali-jams-preserves`) - 60 products
   - Chitrali Seeds (`/categories/chitrali-seeds`) - 120 products
   - Chitrali Pickles (`/categories/chitrali-pickles`) - 70 products
   - Chitrali Rice & Pulses (`/categories/chitrali-rice-pulses`) - 100 products
   - Chitrali Medicinal Plants (`/categories/chitrali-medicinal-plants`) - 90 products
   - Chitrali Wool Products (`/categories/chitrali-wool-products`) - 50 products
   - Chitrali Traditional Foods (`/categories/chitrali-traditional-foods`) - 40 products

3. **Products** (Total: ~2,860 products)
   - Each product has unique SEO-friendly URL
   - Format: `/products/{product-slug}-{weight}-{id}`
   - Example: `/products/chitrali-almonds-100g-100001`

4. **Bundles** (5 bundles)
   - Each bundle has SEO-friendly URL
   - Format: `/bundles/{bundle-slug}`
   - Example: `/bundles/chitrali-dry-fruits-combo-pack`

## SEO Features

### URL Structure

- **Categories**: `/categories/{category-slug}`
- **Products**: `/products/{product-slug}`
- **Bundles**: `/bundles/{bundle-slug}`

### Meta Tags

All entries include:
- `metaUrl`: SEO-friendly URL path
- `metaTitle`: Optimized title (60-70 characters)
- `metaDescription`: SEO description (150-160 characters)

### Slug Generation

- Uses Django's `slugify()` for URL-safe slugs
- Ensures uniqueness with ID suffixes
- Lowercase, hyphen-separated

## Database Structure

### Categories Table
- `slug`: Unique SEO-friendly identifier
- `metaUrl`: Full URL path for SEO
- `metaTitle`: Page title for search engines
- `metaDescription`: Meta description for SEO
- `parentId`: For subcategories

### Items (Products) Table
- `slug`: Unique SEO-friendly identifier
- `metaUrl`: Full URL path (`/products/{slug}`)
- `metaTitle`: Product page title
- `metaDescription`: Product description for SEO

### Bundle Table
- `slug`: Unique SEO-friendly identifier
- `metaUrl`: Full URL path (`/bundles/{slug}`)
- `metaTitle`: Bundle page title
- `metaDescription`: Bundle description for SEO

## Example URLs

After seeding, you'll have URLs like:

```
https://chitralhive.com/categories/chitrali-products
https://chitralhive.com/categories/chitrali-dry-fruits
https://chitralhive.com/products/chitrali-almonds-100g-100001
https://chitralhive.com/bundles/chitrali-dry-fruits-combo-pack
```

## Updating Existing Data

To update SEO fields for existing data:

```python
from inara.models import Category, Item, Bundle
from inara.utils.seo_helpers import generate_seo_url, generate_meta_title, generate_meta_description

# Update category SEO
category = Category.objects.get(slug='chitrali-dry-fruits')
category.metaUrl = generate_seo_url('category', category.slug)
category.metaTitle = generate_meta_title(category.name, 'category')
category.metaDescription = generate_meta_description(category.description, category.name, 'category')
category.save()

# Update product SEO
product = Item.objects.get(slug='some-product')
product.metaUrl = generate_seo_url('product', product.slug)
product.metaTitle = generate_meta_title(product.name, 'product')
product.metaDescription = generate_meta_description(product.description, product.name, 'product')
product.save()
```

## Troubleshooting

### Duplicate Slugs
If you get duplicate slug errors, the command will skip and continue. Check logs for details.

### Missing SEO Fields
If meta fields are empty, run the update script above or re-run the seed command (it uses `get_or_create` so won't duplicate).

### Database Errors
Ensure migrations are up to date:
```bash
python manage.py migrate
```

## Notes

- The seed command uses `get_or_create` so it's safe to run multiple times
- Existing entries won't be overwritten
- SEO URLs follow best practices (lowercase, hyphen-separated, descriptive)
- All meta descriptions are optimized for search engines (150-160 characters)

