"""
Django management command to seed 2000 Chitrali products
Run: python manage.py seed_chitrali_products
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from inara.models import Category, Item, CategoryItem
import random
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed 2000 Chitrali products with categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed Chitrali products...'))
        
        # Create main categories
        categories = self.create_categories()
        
        # Create 2000 products
        products_created = self.create_products(categories)
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {products_created} Chitrali products!'
        ))

    def create_categories(self):
        """Create Chitrali product categories"""
        categories = {}
        
        # Main Chitrali Products category
        main_cat, created = Category.objects.get_or_create(
            slug='chitrali-products',
            defaults={
                'name': 'Chitrali Products',
                'description': 'Authentic Chitrali products including dry fruits, salajit, herbs, and more',
                'status': Category.ACTIVE,
                'appliesOnline': 1,
                'showAtHome': 1,
                'priority': 1,
                'posType': Category.INTERNAL,
            }
        )
        categories['main'] = main_cat
        
        # Subcategories
        subcategories_data = [
            {
                'name': 'Dry Fruits',
                'slug': 'chitrali-dry-fruits',
                'description': 'Premium Chitrali dry fruits including almonds, walnuts, apricots, and more',
                'products_count': 600,
            },
            {
                'name': 'Salajit',
                'slug': 'chitrali-salajit',
                'description': 'Pure Chitrali Salajit (Shilajit) - Natural mineral pitch with health benefits',
                'products_count': 200,
            },
            {
                'name': 'Chitrali Herbs',
                'slug': 'chitrali-herbs',
                'description': 'Traditional Chitrali herbs and medicinal plants',
                'products_count': 300,
            },
            {
                'name': 'Chitrali Honey',
                'slug': 'chitrali-honey',
                'description': 'Pure organic Chitrali honey from mountain flowers',
                'products_count': 150,
            },
            {
                'name': 'Chitrali Nuts',
                'slug': 'chitrali-nuts',
                'description': 'Fresh Chitrali nuts including walnuts, almonds, and pine nuts',
                'products_count': 250,
            },
            {
                'name': 'Chitrali Spices',
                'slug': 'chitrali-spices',
                'description': 'Authentic Chitrali spices and seasonings',
                'products_count': 200,
            },
            {
                'name': 'Chitrali Apricots',
                'slug': 'chitrali-apricots',
                'description': 'Sweet and nutritious Chitrali apricots - dried and fresh',
                'products_count': 150,
            },
            {
                'name': 'Chitrali Grains',
                'slug': 'chitrali-grains',
                'description': 'Organic Chitrali grains and cereals',
                'products_count': 150,
            },
        ]
        
        for subcat_data in subcategories_data:
            subcat, created = Category.objects.get_or_create(
                slug=subcat_data['slug'],
                defaults={
                    'name': subcat_data['name'],
                    'description': subcat_data['description'],
                    'parentId': main_cat,
                    'status': Category.ACTIVE,
                    'appliesOnline': 1,
                    'showAtHome': 1,
                    'priority': 2,
                    'posType': Category.INTERNAL,
                }
            )
            categories[subcat_data['slug']] = {
                'category': subcat,
                'products_count': subcat_data['products_count']
            }
        
        return categories

    def create_products(self, categories):
        """Create 2000 Chitrali products"""
        products_created = 0
        
        # Product data templates for each category
        product_templates = {
            'chitrali-dry-fruits': {
                'names': [
                    'Chitrali Almonds', 'Chitrali Walnuts', 'Chitrali Apricots', 'Chitrali Raisins',
                    'Chitrali Dates', 'Chitrali Figs', 'Chitrali Pistachios', 'Chitrali Cashews',
                    'Chitrali Pine Nuts', 'Chitrali Hazelnuts', 'Chitrali Prunes', 'Chitrali Cranberries',
                    'Chitrali Dried Apricots', 'Chitrali Dried Peaches', 'Chitrali Dried Plums',
                ],
                'weights': ['100g', '250g', '500g', '1kg', '2kg', '5kg'],
                'price_range': (500, 5000),
            },
            'chitrali-salajit': {
                'names': [
                    'Pure Chitrali Salajit', 'Chitrali Shilajit Resin', 'Premium Chitrali Salajit',
                    'Organic Chitrali Salajit', 'Raw Chitrali Salajit', 'Purified Chitrali Salajit',
                    'Chitrali Salajit Powder', 'Chitrali Salajit Capsules', 'Chitrali Salajit Extract',
                    'Mountain Chitrali Salajit',
                ],
                'weights': ['10g', '25g', '50g', '100g', '250g', '500g'],
                'price_range': (1000, 10000),
            },
            'chitrali-herbs': {
                'names': [
                    'Chitrali Mint', 'Chitrali Thyme', 'Chitrali Basil', 'Chitrali Oregano',
                    'Chitrali Sage', 'Chitrali Rosemary', 'Chitrali Chamomile', 'Chitrali Lavender',
                    'Chitrali Eucalyptus', 'Chitrali Calendula', 'Chitrali Nettle', 'Chitrali Dandelion',
                ],
                'weights': ['50g', '100g', '250g', '500g', '1kg'],
                'price_range': (300, 3000),
            },
            'chitrali-honey': {
                'names': [
                    'Pure Chitrali Honey', 'Organic Chitrali Honey', 'Wild Chitrali Honey',
                    'Mountain Chitrali Honey', 'Chitrali Acacia Honey', 'Chitrali Forest Honey',
                    'Raw Chitrali Honey', 'Chitrali Sidr Honey', 'Chitrali Spring Honey',
                ],
                'weights': ['250g', '500g', '1kg', '2kg', '5kg'],
                'price_range': (800, 8000),
            },
            'chitrali-nuts': {
                'names': [
                    'Chitrali Walnuts', 'Chitrali Almonds', 'Chitrali Pine Nuts', 'Chitrali Hazelnuts',
                    'Chitrali Pistachios', 'Chitrali Cashews', 'Chitrali Pecans', 'Chitrali Macadamia',
                    'Chitrali Brazil Nuts', 'Chitrali Chestnuts',
                ],
                'weights': ['100g', '250g', '500g', '1kg', '2kg'],
                'price_range': (600, 6000),
            },
            'chitrali-spices': {
                'names': [
                    'Chitrali Cumin', 'Chitrali Coriander', 'Chitrali Turmeric', 'Chitrali Red Chili',
                    'Chitrali Black Pepper', 'Chitrali Cardamom', 'Chitrali Cinnamon', 'Chitrali Cloves',
                    'Chitrali Nutmeg', 'Chitrali Fenugreek', 'Chitrali Mustard Seeds', 'Chitrali Fennel',
                ],
                'weights': ['50g', '100g', '250g', '500g', '1kg'],
                'price_range': (200, 2000),
            },
            'chitrali-apricots': {
                'names': [
                    'Chitrali Dried Apricots', 'Sweet Chitrali Apricots', 'Organic Chitrali Apricots',
                    'Chitrali Apricot Halves', 'Chitrali Apricot Whole', 'Chitrali Apricot Pulp',
                    'Chitrali Apricot Jam', 'Chitrali Apricot Preserve',
                ],
                'weights': ['250g', '500g', '1kg', '2kg', '5kg'],
                'price_range': (400, 4000),
            },
            'chitrali-grains': {
                'names': [
                    'Chitrali Wheat', 'Chitrali Barley', 'Chitrali Oats', 'Chitrali Millet',
                    'Chitrali Quinoa', 'Chitrali Buckwheat', 'Chitrali Rice', 'Chitrali Corn',
                ],
                'weights': ['500g', '1kg', '2kg', '5kg', '10kg'],
                'price_range': (300, 3000),
            },
        }
        
        # Start extPosId from a high number to avoid conflicts
        ext_pos_id = 100000
        
        for category_slug, category_info in categories.items():
            if category_slug == 'main':
                continue
                
            category = category_info['category']
            products_count = category_info['products_count']
            template = product_templates.get(category_slug, {
                'names': ['Chitrali Product'],
                'weights': ['100g', '250g', '500g', '1kg'],
                'price_range': (500, 5000),
            })
            
            for i in range(products_count):
                try:
                    # Generate product name
                    base_name = random.choice(template['names'])
                    weight = random.choice(template['weights'])
                    product_name = f"{base_name} - {weight}"
                    
                    # Generate unique slug and SKU
                    base_slug = slugify(base_name)
                    weight_slug = weight.lower().replace(' ', '-')
                    slug = f"{base_slug}-{weight_slug}-{ext_pos_id}"
                    # Create category prefix for SKU
                    cat_prefix = category_slug.replace('chitrali-', '').replace('-', '')[:3].upper()
                    sku = f"CHIT-{cat_prefix}-{ext_pos_id:06d}"
                    
                    # Check if product already exists
                    if Item.objects.filter(slug=slug).exists() or Item.objects.filter(sku=sku).exists():
                        ext_pos_id += 1
                        continue
                    
                    # Generate prices
                    min_price, max_price = template['price_range']
                    mrp = random.randint(min_price, max_price)
                    discount = random.choice([0, 5, 10, 15, 20, 25])
                    sale_price = int(mrp * (1 - discount / 100))
                    
                    # Generate description
                    description = self.generate_description(category_slug, base_name, weight)
                    
                    # Create product
                    product = Item.objects.create(
                        extPosId=ext_pos_id,
                        name=product_name,
                        slug=slug,
                        sku=sku,
                        description=description,
                        mrp=mrp,
                        salePrice=sale_price,
                        discount=discount,
                        stock=Decimal(random.randint(10, 1000)),
                        stockCheckQty=Decimal(random.randint(5, 100)),
                        weight=Decimal(random.uniform(0.1, 5.0)),
                        appliesOnline=1,
                        status=Item.ACTIVE,
                        isNewArrival=random.choice([0, 1]),
                        isFeatured=random.choice([0, 1]) if i % 10 == 0 else 0,
                        manufacturer='Chitral Hive',
                        metaTitle=f"{product_name} - Chitral Hive",
                        metaDescription=description[:150],
                        timestamp=timezone.now(),
                    )
                    
                    # Link product to category
                    CategoryItem.objects.create(
                        categoryId=category,
                        itemId=product,
                        level=2,
                        status=CategoryItem.ACTIVE,
                    )
                    
                    products_created += 1
                    ext_pos_id += 1
                    
                    if products_created % 100 == 0:
                        self.stdout.write(f'Created {products_created} products...')
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating product: {str(e)}'))
                    ext_pos_id += 1
                    continue
        
        return products_created

    def generate_description(self, category_slug, product_name, weight):
        """Generate product description"""
        descriptions = {
            'chitrali-dry-fruits': f"Premium {product_name} sourced directly from Chitral's mountain regions. "
                                  f"These naturally dried fruits are rich in vitamins, minerals, and antioxidants. "
                                  f"Perfect for snacking, cooking, or as a healthy addition to your diet. "
                                  f"100% natural, no preservatives added.",
            
            'chitrali-salajit': f"Pure {product_name} extracted from the pristine mountains of Chitral. "
                               f"Salajit (Shilajit) is a natural mineral pitch known for its traditional health benefits. "
                               f"Rich in fulvic acid and over 84 minerals. Authentic Chitrali quality guaranteed.",
            
            'chitrali-herbs': f"Traditional {product_name} grown in Chitral's fertile valleys. "
                             f"These organic herbs are hand-picked and carefully dried to preserve their natural properties. "
                             f"Perfect for culinary use and traditional remedies.",
            
            'chitrali-honey': f"Pure {product_name} collected from Chitral's wildflower meadows. "
                             f"This organic honey is raw, unfiltered, and unpasteurized, preserving all natural enzymes and nutrients. "
                             f"Rich flavor with natural sweetness.",
            
            'chitrali-nuts': f"Fresh {product_name} from Chitral's orchards. "
                            f"These premium nuts are naturally grown without chemicals, rich in healthy fats, protein, and essential nutrients. "
                            f"Perfect for snacking or cooking.",
            
            'chitrali-spices': f"Authentic {product_name} from Chitral. "
                              f"These traditional spices are sun-dried and ground to preserve their natural flavors and aromas. "
                              f"Essential for Chitrali cuisine.",
            
            'chitrali-apricots': f"Sweet {product_name} from Chitral's famous apricot orchards. "
                                f"These naturally dried apricots are rich in fiber, vitamins A and C. "
                                f"No added sugar, pure Chitrali quality.",
            
            'chitrali-grains': f"Organic {product_name} grown in Chitral's fertile soil. "
                              f"These whole grains are naturally grown, rich in fiber and essential nutrients. "
                              f"Perfect for healthy cooking and traditional Chitrali recipes.",
        }
        
        return descriptions.get(category_slug, f"Premium {product_name} from Chitral. Authentic quality, natural ingredients.")

