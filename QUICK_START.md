# Quick Start - Seed Chitrali Products

## Current Status
✅ **Database switched to SQLite** (no PostgreSQL needed for testing)

## Run the Seed Command Now

```bash
cd chitralhivedjango

# Run migrations first (if not done)
python manage.py migrate

# Seed 2000 Chitrali products
python manage.py seed_chitrali_products
```

## What Happens

1. Creates main category: "Chitrali Products"
2. Creates 8 subcategories (Dry Fruits, Salajit, Herbs, etc.)
3. Creates 2000 Chitrali products with proper structure
4. Links products to categories

## Switch Back to PostgreSQL Later

When you install PostgreSQL:

1. Edit `ecommerce_backend/settings.py`
2. Comment out SQLite config
3. Uncomment PostgreSQL config
4. Run migrations: `python manage.py migrate`
5. Run seed command again

## Install PostgreSQL (Optional - For Production)

1. Download: https://www.postgresql.org/download/windows/
2. Install with:
   - Port: 5432
   - Username: `chitral`
   - Password: `chitral`
   - Database: `chitral_hive`
3. Start PostgreSQL service
4. Update settings.py to use PostgreSQL

