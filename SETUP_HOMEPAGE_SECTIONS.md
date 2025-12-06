# Setup Homepage Sections

This document explains how to set up home page sections with ChitralHive categories.

## Overview

The home page displays categories in different sections with **SEO-optimized URLs and metadata**:
- **Section 1**: 2 category boxes
- **Section 2**: 6 category boxes  
- **Section 3**: 3 category boxes
- **Section 4**: 2 category boxes
- **Section 5**: 1 category box

Each section can also have:
- Main section category (type='section')
- Subcategories (type='section_subcategory')

### SEO Features

The command automatically:
- **Prioritizes categories with SEO fields** (metaUrl, metaTitle, metaDescription)
- **Uses metaUrl** when available (falls back to slug if not set)
- **Uses metaTitle** for display names (falls back to category name)
- **Uses SEO-friendly slugs** for all URLs
- **Logs SEO status** for each category during setup

## Prerequisites

1. Run the SEO seeding command first to create categories:
   ```bash
   python manage.py seed_chitralhive_seo
   ```

2. Ensure categories have `showAtHome=1` and `status=ACTIVE` to appear on home page.

## Usage

### Basic Setup

Run the command to set up home page sections:

```bash
python manage.py setup_homepage_sections
```

This will:
- Get the first 8 categories with `showAtHome=1` (prioritizing SEO-optimized categories)
- Create Individual_BoxOrder entries for boxes and sections with SEO-friendly URLs
- Use `metaUrl` when available, otherwise use `slug`
- Use `metaTitle` for display names when available
- Set up Configuration for number of sections and boxes
- Create SectionSequence entries with SEO metadata

### Clear Existing Data

To remove all existing Individual_BoxOrder and SectionSequence data before setting up:

```bash
python manage.py setup_homepage_sections --clear
```

## What Gets Created

### Individual_BoxOrder Entries

1. **Section entries** (type='section'):
   - sequenceNo=1: First main category section
   - sequenceNo=2: Second main category section

2. **Box entries** (type='box'):
   - sequenceNo=1-2: Section 1 boxes
   - sequenceNo=3-8: Section 2 boxes
   - sequenceNo=9-11: Section 3 boxes (if configured)
   - sequenceNo=12-13: Section 4 boxes (if configured)
   - sequenceNo=14: Section 5 box (if configured)

3. **Subcategory entries** (type='section_subcategory'):
   - Created for child categories of section categories
   - Linked via `parent` field to section category ID

### SectionSequence Entries

- Created for first 3 categories
- Includes child categories (up to 7) in child1-child7 fields

### Configuration

- `box`: Number of boxes configured
- `section`: Number of sections configured

## Customization

To customize which categories appear:

1. Edit `get_chitralhive_categories()` method to filter categories differently
2. Adjust `box_sequence` array to change box layout
3. Modify `create_section_sequences()` to change section configuration

## Frontend Integration

The frontend uses:
- `api.getindvidualorderbox()` → `/webind` endpoint → Returns Individual_BoxOrder data
- `api.getSectionSequence()` → `/getsection` endpoint → Returns SectionSequence data

The home page (`pages/index.jsx`) reads:
- `type='box'` entries for category boxes
- `type='section'` entries for section headers
- `type='section_subcategory'` entries for subcategory navigation

## Troubleshooting

### No categories appearing

- Check that categories have `showAtHome=1` and `status=ACTIVE`
- Verify categories exist: `Category.objects.filter(showAtHome=1, status=1).count()`
- Run `seed_chitralhive_seo` first if no categories exist

### Wrong categories showing

- Check category `priority` field (used for ordering)
- Verify `parentId=None` for main categories
- Ensure `isBrand=False` for regular categories

### Sections not displaying

- Check Configuration table: `Configuration.objects.filter(name='section')`
- Verify Individual_BoxOrder entries: `Individual_BoxOrder.objects.filter(type='section')`
- Check frontend API calls in browser console

