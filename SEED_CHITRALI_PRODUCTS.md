# Seed Chitrali Products - Instructions

This script will add 2000 Chitrali products to your database with proper categories and structure.

## Products Distribution

- **Dry Fruits**: 600 products
- **Salajit**: 200 products  
- **Chitrali Herbs**: 300 products
- **Chitrali Honey**: 150 products
- **Chitrali Nuts**: 250 products
- **Chitrali Spices**: 200 products
- **Chitrali Apricots**: 150 products
- **Chitrali Grains**: 150 products

**Total: 2000 Chitrali Products**

## How to Run

1. **Navigate to Django project directory:**
   ```bash
   cd chitralhivedjango
   ```

2. **Run the management command:**
   ```bash
   python manage.py seed_chitrali_products
   ```

3. **Wait for completion:**
   The script will create:
   - Main category: "Chitrali Products"
   - 8 subcategories
   - 2000 products with proper names, descriptions, prices
   - Category-Item relationships

## What Gets Created

### Categories Structure:
```
Chitrali Products (Main Category)
├── Dry Fruits (600 products)
├── Salajit (200 products)
├── Chitrali Herbs (300 products)
├── Chitrali Honey (150 products)
├── Chitrali Nuts (250 products)
├── Chitrali Spices (200 products)
├── Chitrali Apricots (150 products)
└── Chitrali Grains (150 products)
```

### Product Details:
- **Names**: Chitrali-specific product names (e.g., "Chitrali Almonds - 500g")
- **SKUs**: Unique SKUs in format `CHIT-XXX-XXXXXX`
- **Prices**: Realistic price ranges for each category
- **Descriptions**: Detailed Chitrali product descriptions
- **Stock**: Random stock quantities (10-1000 units)
- **Status**: All products set to ACTIVE
- **Online**: All products enabled for online sale

## Product Features

- ✅ Unique slugs and SKUs
- ✅ Realistic pricing (category-specific ranges)
- ✅ Detailed descriptions
- ✅ Stock management enabled
- ✅ Some products marked as "New Arrival" or "Featured"
- ✅ Proper category relationships
- ✅ All products are Chitrali-specific

## Notes

- The script uses `extPosId` starting from 100000 to avoid conflicts
- Products are linked to their respective categories via `CategoryItem` table
- All products have manufacturer set to "Chitral Hive"
- Prices include MRP, Sale Price, and Discount percentages

## Troubleshooting

If you encounter errors:

1. **Duplicate slug/SKU errors**: The script automatically skips duplicates
2. **Category already exists**: The script uses `get_or_create` to handle existing categories
3. **Database connection**: Ensure your database is properly configured

## After Running

After the script completes:

1. Check your admin panel to see the new products
2. Verify categories are properly structured
3. Products should appear on your website under "Chitrali Products"
4. All products will be searchable and filterable by category

## Customization

To modify the script:

1. Edit `chitralhivedjango/inara/management/commands/seed_chitrali_products.py`
2. Adjust product counts in `subcategories_data`
3. Modify product names, prices, or descriptions in `product_templates`
4. Run the command again (it will skip existing products)

## Important

- **Backup your database** before running if you have existing data
- The script is idempotent - safe to run multiple times
- Existing products with same slug/SKU will be skipped

