"""
Django management command to seed ChitralHive categories, subcategories, products, and bundles with SEO-friendly URLs
Run: python manage.py seed_chitralhive_seo
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from inara.models import Category, Item, CategoryItem, Bundle, BundleItem
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seed ChitralHive categories, subcategories, products, and bundles with SEO-friendly URLs'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to seed ChitralHive data with SEO optimization...'))
        
        # Create main categories with SEO
        categories = self.create_categories_with_seo()
        
        # Create products with SEO
        products_created = self.create_products_with_seo(categories)
        
        # Create bundles with SEO
        bundles_created = self.create_bundles_with_seo(categories)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Successfully created:\n'
            f'   - Categories: {len(categories)}\n'
            f'   - Products: {products_created}\n'
            f'   - Bundles: {bundles_created}\n'
            f'All with SEO-friendly URLs!'
        ))

    def create_categories_with_seo(self):
        """Create ChitralHive categories and subcategories with SEO-friendly URLs"""
        categories = {}
        
        # Create main categories (parentId=None) that will show on home page
        # Each category is a main category so it appears in navigation
        subcategories_data = [
            {
                'name': 'Dry Fruits',
                'slug': 'chitrali-dry-fruits',
                'description': 'Premium Chitrali dry fruits including almonds, walnuts, apricots, raisins, dates, and more. Naturally dried, rich in nutrients, perfect for healthy snacking.',
                'metaTitle': 'Chitrali Dry Fruits - Premium Dried Fruits Online | ChitralHive',
                'metaDescription': 'Buy premium Chitrali dry fruits online. Natural almonds, walnuts, apricots, dates, and more. Rich in vitamins and minerals. Free shipping available.',
                'products_count': 600,
            },
            {
                'name': 'Salajit',
                'slug': 'chitrali-salajit',
                'description': 'Pure Chitrali Salajit (Shilajit) - Natural mineral pitch with traditional health benefits. Rich in fulvic acid and 84+ minerals from pristine Chitral mountains.',
                'metaTitle': 'Pure Chitrali Salajit (Shilajit) - Natural Mineral Pitch | ChitralHive',
                'metaDescription': 'Buy authentic Chitrali Salajit online. Pure Shilajit resin, powder, and capsules. Rich in minerals and fulvic acid. Traditional health benefits.',
                'products_count': 200,
            },
            {
                'name': 'Chitrali Herbs',
                'slug': 'chitrali-herbs',
                'description': 'Traditional Chitrali herbs and medicinal plants. Organic, hand-picked herbs preserved naturally for culinary and traditional medicinal use.',
                'metaTitle': 'Chitrali Herbs - Traditional Medicinal Herbs Online | ChitralHive',
                'metaDescription': 'Shop traditional Chitrali herbs online. Organic mint, thyme, basil, sage, and more. Hand-picked and naturally preserved. Perfect for cooking and remedies.',
                'products_count': 300,
            },
            {
                'name': 'Chitrali Honey',
                'slug': 'chitrali-honey',
                'description': 'Pure organic Chitrali honey from mountain wildflowers. Raw, unfiltered, and unpasteurized honey preserving all natural enzymes and nutrients.',
                'metaTitle': 'Pure Chitrali Honey - Organic Mountain Honey Online | ChitralHive',
                'metaDescription': 'Buy pure Chitrali honey online. Organic, raw, unfiltered mountain honey. Rich in natural enzymes. Available in various sizes. Free shipping.',
                'products_count': 150,
            },
            {
                'name': 'Chitrali Nuts',
                'slug': 'chitrali-nuts',
                'description': 'Fresh Chitrali nuts including walnuts, almonds, pine nuts, hazelnuts, and more. Naturally grown, rich in healthy fats, protein, and essential nutrients.',
                'metaTitle': 'Chitrali Nuts - Fresh Premium Nuts Online | ChitralHive',
                'metaDescription': 'Shop fresh Chitrali nuts online. Premium walnuts, almonds, pine nuts, and more. Rich in healthy fats and protein. Natural, no chemicals.',
                'products_count': 250,
            },
            {
                'name': 'Chitrali Spices',
                'slug': 'chitrali-spices',
                'description': 'Authentic Chitrali spices and seasonings. Traditional spices sun-dried and ground to preserve natural flavors and aromas. Essential for Chitrali cuisine.',
                'metaTitle': 'Chitrali Spices - Authentic Traditional Spices Online | ChitralHive',
                'metaDescription': 'Buy authentic Chitrali spices online. Traditional cumin, coriander, turmeric, cardamom, and more. Sun-dried and naturally ground. Perfect for cooking.',
                'products_count': 200,
            },
            {
                'name': 'Chitrali Apricots',
                'slug': 'chitrali-apricots',
                'description': 'Sweet and nutritious Chitrali apricots - dried and fresh. Rich in fiber, vitamins A and C. No added sugar, pure Chitrali quality from famous orchards.',
                'metaTitle': 'Chitrali Apricots - Sweet Dried Apricots Online | ChitralHive',
                'metaDescription': 'Shop Chitrali apricots online. Sweet dried apricots, halves, whole, and preserves. Rich in fiber and vitamins. No added sugar. Free shipping.',
                'products_count': 150,
            },
            {
                'name': 'Chitrali Grains',
                'slug': 'chitrali-grains',
                'description': 'Organic Chitrali grains and cereals. Naturally grown whole grains rich in fiber and essential nutrients. Perfect for healthy cooking and traditional recipes.',
                'metaTitle': 'Chitrali Grains - Organic Whole Grains Online | ChitralHive',
                'metaDescription': 'Buy organic Chitrali grains online. Whole wheat, barley, oats, quinoa, and more. Rich in fiber and nutrients. Perfect for healthy cooking.',
                'products_count': 150,
            },
            {
                'name': 'Chitrali Oils',
                'slug': 'chitrali-oils',
                'description': 'Pure Chitrali cold-pressed oils including walnut oil, apricot kernel oil, almond oil, and more. Natural, unrefined oils rich in healthy fats and nutrients.',
                'metaTitle': 'Chitrali Oils - Pure Cold-Pressed Oils Online | ChitralHive',
                'metaDescription': 'Buy pure Chitrali oils online. Cold-pressed walnut oil, apricot kernel oil, almond oil. Natural, unrefined, rich in healthy fats. Free shipping.',
                'products_count': 100,
            },
            {
                'name': 'Chitrali Tea',
                'slug': 'chitrali-tea',
                'description': 'Premium Chitrali tea blends including green tea, herbal tea, and traditional Chitrali tea. Natural, organic tea leaves from mountain regions.',
                'metaTitle': 'Chitrali Tea - Premium Tea Blends Online | ChitralHive',
                'metaDescription': 'Shop premium Chitrali tea online. Green tea, herbal tea, traditional blends. Natural, organic tea leaves. Rich in antioxidants. Free shipping.',
                'products_count': 80,
            },
            {
                'name': 'Chitrali Jams & Preserves',
                'slug': 'chitrali-jams-preserves',
                'description': 'Natural Chitrali jams and preserves made from fresh fruits. Apricot jam, mulberry jam, apple preserve, and more. No artificial preservatives.',
                'metaTitle': 'Chitrali Jams & Preserves - Natural Fruit Preserves Online | ChitralHive',
                'metaDescription': 'Buy natural Chitrali jams and preserves online. Apricot jam, mulberry jam, apple preserve. Made from fresh fruits, no artificial preservatives.',
                'products_count': 60,
            },
            {
                'name': 'Chitrali Seeds',
                'slug': 'chitrali-seeds',
                'description': 'Premium Chitrali seeds including pumpkin seeds, sunflower seeds, chia seeds, flax seeds, and more. Rich in protein, fiber, and healthy fats.',
                'metaTitle': 'Chitrali Seeds - Premium Seeds Online | ChitralHive',
                'metaDescription': 'Shop premium Chitrali seeds online. Pumpkin seeds, sunflower seeds, chia seeds, flax seeds. Rich in protein and healthy fats. Natural quality.',
                'products_count': 120,
            },
            {
                'name': 'Chitrali Pickles',
                'slug': 'chitrali-pickles',
                'description': 'Traditional Chitrali pickles made with authentic recipes. Mango pickle, lemon pickle, mixed vegetable pickle, and more. Preserved naturally.',
                'metaTitle': 'Chitrali Pickles - Traditional Pickles Online | ChitralHive',
                'metaDescription': 'Buy traditional Chitrali pickles online. Mango pickle, lemon pickle, mixed vegetable pickle. Authentic recipes, naturally preserved. Free shipping.',
                'products_count': 70,
            },
            {
                'name': 'Chitrali Rice & Pulses',
                'slug': 'chitrali-rice-pulses',
                'description': 'Organic Chitrali rice and pulses. Basmati rice, brown rice, lentils, chickpeas, kidney beans, and more. Naturally grown, rich in protein and fiber.',
                'metaTitle': 'Chitrali Rice & Pulses - Organic Rice and Lentils Online | ChitralHive',
                'metaDescription': 'Shop organic Chitrali rice and pulses online. Basmati rice, brown rice, lentils, chickpeas. Rich in protein and fiber. Natural, organic quality.',
                'products_count': 100,
            },
            {
                'name': 'Chitrali Medicinal Plants',
                'slug': 'chitrali-medicinal-plants',
                'description': 'Traditional Chitrali medicinal plants and herbs. Used in traditional medicine for centuries. Organic, hand-picked, naturally preserved.',
                'metaTitle': 'Chitrali Medicinal Plants - Traditional Herbs Online | ChitralHive',
                'metaDescription': 'Buy traditional Chitrali medicinal plants online. Organic, hand-picked herbs used in traditional medicine. Naturally preserved. Free shipping.',
                'products_count': 90,
            },
            {
                'name': 'Chitrali Wool Products',
                'slug': 'chitrali-wool-products',
                'description': 'Authentic Chitrali wool products including shawls, blankets, caps, and traditional woolen items. Handwoven, natural wool from Chitral sheep.',
                'metaTitle': 'Chitrali Wool Products - Handwoven Wool Items Online | ChitralHive',
                'metaDescription': 'Shop authentic Chitrali wool products online. Shawls, blankets, caps, traditional items. Handwoven, natural wool. Traditional craftsmanship.',
                'products_count': 50,
            },
            {
                'name': 'Chitrali Traditional Foods',
                'slug': 'chitrali-traditional-foods',
                'description': 'Authentic Chitrali traditional foods and ready-to-eat items. Prepared using traditional recipes and methods. Natural ingredients, no preservatives.',
                'metaTitle': 'Chitrali Traditional Foods - Authentic Ready-to-Eat Items | ChitralHive',
                'metaDescription': 'Buy authentic Chitrali traditional foods online. Ready-to-eat items prepared with traditional recipes. Natural ingredients, no preservatives.',
                'products_count': 40,
            },
        ]
        
        for idx, subcat_data in enumerate(subcategories_data, start=1):
            # Create as main category (parentId=None) so it shows on home page
            subcat, created = Category.objects.get_or_create(
                slug=subcat_data['slug'],
                defaults={
                    'name': subcat_data['name'],
                    'description': subcat_data['description'],
                    'parentId': None,  # Main category - will show on home page
                    'isBrand': False,  # Required for getNavCategories
                    'status': Category.ACTIVE,
                    'appliesOnline': 1,
                    'showAtHome': 1,  # Show on home page
                    'priority': idx,
                    'posType': Category.INTERNAL,
                    'metaUrl': f'/categories/{subcat_data["slug"]}',
                    'metaTitle': subcat_data['metaTitle'],
                    'metaDescription': subcat_data['metaDescription'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created main category: {subcat.name}'))
            else:
                # Update existing category to ensure it's set as main category
                subcat.parentId = None
                subcat.isBrand = False
                subcat.showAtHome = 1
                subcat.status = Category.ACTIVE
                subcat.save()
                self.stdout.write(self.style.SUCCESS(f'Updated category: {subcat.name}'))
            
            categories[subcat_data['slug']] = {
                'category': subcat,
                'products_count': subcat_data['products_count']
            }
        
        return categories

    def create_products_with_seo(self, categories):
        """Create ChitralHive products with SEO-friendly URLs and metadata"""
        products_created = 0
        
        # Product data templates
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
            'chitrali-oils': {
                'names': [
                    'Chitrali Walnut Oil', 'Chitrali Apricot Kernel Oil', 'Chitrali Almond Oil',
                    'Chitrali Olive Oil', 'Chitrali Sesame Oil', 'Chitrali Sunflower Oil',
                    'Chitrali Mustard Oil', 'Chitrali Coconut Oil', 'Chitrali Flaxseed Oil',
                ],
                'weights': ['250ml', '500ml', '1L', '2L', '5L'],
                'price_range': (800, 6000),
            },
            'chitrali-tea': {
                'names': [
                    'Chitrali Green Tea', 'Chitrali Herbal Tea', 'Chitrali Black Tea',
                    'Chitrali Mint Tea', 'Chitrali Chamomile Tea', 'Chitrali Jasmine Tea',
                    'Chitrali Traditional Tea', 'Chitrali Mountain Tea', 'Chitrali Organic Tea',
                ],
                'weights': ['50g', '100g', '250g', '500g', '1kg'],
                'price_range': (400, 3000),
            },
            'chitrali-jams-preserves': {
                'names': [
                    'Chitrali Apricot Jam', 'Chitrali Mulberry Jam', 'Chitrali Apple Preserve',
                    'Chitrali Peach Jam', 'Chitrali Strawberry Jam', 'Chitrali Mixed Fruit Jam',
                    'Chitrali Grape Preserve', 'Chitrali Fig Jam',
                ],
                'weights': ['250g', '500g', '1kg', '2kg'],
                'price_range': (500, 2500),
            },
            'chitrali-seeds': {
                'names': [
                    'Chitrali Pumpkin Seeds', 'Chitrali Sunflower Seeds', 'Chitrali Chia Seeds',
                    'Chitrali Flax Seeds', 'Chitrali Sesame Seeds', 'Chitrali Poppy Seeds',
                    'Chitrali Fennel Seeds', 'Chitrali Cumin Seeds', 'Chitrali Mustard Seeds',
                ],
                'weights': ['100g', '250g', '500g', '1kg', '2kg'],
                'price_range': (300, 2500),
            },
            'chitrali-pickles': {
                'names': [
                    'Chitrali Mango Pickle', 'Chitrali Lemon Pickle', 'Chitrali Mixed Vegetable Pickle',
                    'Chitrali Chili Pickle', 'Chitrali Garlic Pickle', 'Chitrali Carrot Pickle',
                    'Chitrali Turnip Pickle', 'Chitrali Cauliflower Pickle',
                ],
                'weights': ['250g', '500g', '1kg', '2kg'],
                'price_range': (400, 2000),
            },
            'chitrali-rice-pulses': {
                'names': [
                    'Chitrali Basmati Rice', 'Chitrali Brown Rice', 'Chitrali Red Rice',
                    'Chitrali Lentils', 'Chitrali Chickpeas', 'Chitrali Kidney Beans',
                    'Chitrali Black Beans', 'Chitrali Mung Beans', 'Chitrali Split Peas',
                ],
                'weights': ['500g', '1kg', '2kg', '5kg', '10kg'],
                'price_range': (300, 3000),
            },
            'chitrali-medicinal-plants': {
                'names': [
                    'Chitrali Neem Leaves', 'Chitrali Aloe Vera', 'Chitrali Turmeric Root',
                    'Chitrali Ginger Root', 'Chitrali Garlic Bulbs', 'Chitrali Fenugreek Seeds',
                    'Chitrali Cumin Seeds', 'Chitrali Fennel Seeds', 'Chitrali Coriander Seeds',
                ],
                'weights': ['50g', '100g', '250g', '500g', '1kg'],
                'price_range': (200, 2000),
            },
            'chitrali-wool-products': {
                'names': [
                    'Chitrali Wool Shawl', 'Chitrali Wool Blanket', 'Chitrali Wool Cap',
                    'Chitrali Wool Scarf', 'Chitrali Wool Socks', 'Chitrali Wool Gloves',
                    'Chitrali Wool Sweater', 'Chitrali Wool Shawl Traditional',
                ],
                'weights': ['1 piece', 'Set of 2', 'Set of 3'],
                'price_range': (1500, 8000),
            },
            'chitrali-traditional-foods': {
                'names': [
                    'Chitrali Chapshuro', 'Chitrali Shish Kebab', 'Chitrali Mantu',
                    'Chitrali Qorma', 'Chitrali Pulao', 'Chitrali Bread',
                    'Chitrali Traditional Soup', 'Chitrali Rice Dish',
                ],
                'weights': ['250g', '500g', '1kg', '2kg'],
                'price_range': (600, 4000),
            },
        }
        
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
                    base_name = random.choice(template['names'])
                    weight = random.choice(template['weights'])
                    product_name = f"{base_name} - {weight}"
                    
                    # Generate SEO-friendly slug
                    base_slug = slugify(base_name)
                    weight_slug = slugify(weight)
                    slug = f"{base_slug}-{weight_slug}-{ext_pos_id}"
                    
                    # Generate SKU
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
                    
                    # Generate SEO-friendly URL
                    meta_url = f"/products/{slug}"
                    
                    # Create product with SEO
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
                        metaUrl=meta_url,
                        metaTitle=f"{product_name} - Buy Online | ChitralHive",
                        metaDescription=f"{description[:150]}... Buy {product_name} online from ChitralHive. Premium quality, free shipping available.",
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

    def create_bundles_with_seo(self, categories):
        """Create ChitralHive bundles with SEO-friendly URLs"""
        bundles_created = 0
        
        # Bundle templates
        bundle_templates = [
            {
                'name': 'Chitrali Dry Fruits Combo Pack',
                'description': 'Premium assortment of Chitrali dry fruits including almonds, walnuts, apricots, dates, and raisins. Perfect gift pack.',
                'bundle_type': Bundle.PRODUCT,
                'category_slug': 'chitrali-dry-fruits',
                'price_range': (2000, 5000),
            },
            {
                'name': 'Chitrali Wellness Bundle',
                'description': 'Complete wellness package with Chitrali Salajit, Honey, and Herbs. Natural health benefits in one bundle.',
                'bundle_type': Bundle.PRODUCT,
                'category_slug': 'chitrali-salajit',
                'price_range': (3000, 8000),
            },
            {
                'name': 'Chitrali Spice Collection',
                'description': 'Authentic Chitrali spices collection including cumin, coriander, turmeric, cardamom, and more. Essential for Chitrali cuisine.',
                'bundle_type': Bundle.PRODUCT,
                'category_slug': 'chitrali-spices',
                'price_range': (1500, 4000),
            },
            {
                'name': 'Chitrali Nut Mix Premium',
                'description': 'Premium mix of Chitrali nuts including walnuts, almonds, pine nuts, and hazelnuts. Rich in healthy fats and protein.',
                'bundle_type': Bundle.PRODUCT,
                'category_slug': 'chitrali-nuts',
                'price_range': (2500, 6000),
            },
            {
                'name': 'Chitrali Honey & Herbs Gift Set',
                'description': 'Perfect gift set with pure Chitrali honey and traditional herbs. Organic and natural.',
                'bundle_type': Bundle.PRODUCT,
                'category_slug': 'chitrali-honey',
                'price_range': (2000, 5000),
            },
        ]
        
        ext_pos_id = 200000
        
        for bundle_data in bundle_templates:
            try:
                # Generate SEO-friendly slug
                slug = slugify(bundle_data['name'])
                sku = f"CHIT-BUNDLE-{ext_pos_id:06d}"
                
                # Check if bundle already exists
                if Bundle.objects.filter(slug=slug).exists() or Bundle.objects.filter(sku=sku).exists():
                    ext_pos_id += 1
                    continue
                
                # Get category
                category = categories.get(bundle_data['category_slug'], {}).get('category')
                
                # Generate prices
                min_price, max_price = bundle_data['price_range']
                mrp = random.randint(min_price, max_price)
                discount = random.choice([10, 15, 20, 25])
                sale_price = int(mrp * (1 - discount / 100))
                
                # Generate SEO URL
                meta_url = f"/bundles/{slug}"
                
                # Create bundle
                bundle = Bundle.objects.create(
                    name=bundle_data['name'],
                    slug=slug,
                    sku=sku,
                    description=bundle_data['description'],
                    mrp=mrp,
                    salePrice=sale_price,
                    bundleType=bundle_data['bundle_type'],
                    categoryId=category,
                    showAtHome=1,
                    priority=random.randint(1, 10),
                    status=Bundle.ACTIVE,
                    metaUrl=meta_url,
                    metaTitle=f"{bundle_data['name']} - Buy Online | ChitralHive",
                    metaDescription=f"{bundle_data['description']} Buy {bundle_data['name']} online from ChitralHive. Premium quality, special bundle discount available.",
                )
                
                # Add items to bundle (get random products from category)
                if category:
                    category_items = Item.objects.filter(
                        categoryitem__categoryId=category,
                        status=Item.ACTIVE
                    )[:random.randint(3, 6)]
                    
                    for item in category_items:
                        BundleItem.objects.create(
                            bundleId=bundle,
                            itemId=item,
                            quantity=random.randint(1, 3),
                            priority=random.randint(1, 10),
                            status=BundleItem.ACTIVE,
                        )
                
                bundles_created += 1
                ext_pos_id += 1
                
                self.stdout.write(self.style.SUCCESS(f'Created bundle: {bundle.name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating bundle: {str(e)}'))
                ext_pos_id += 1
                continue
        
        return bundles_created

    def generate_description(self, category_slug, product_name, weight):
        """Generate SEO-friendly product description"""
        descriptions = {
            'chitrali-dry-fruits': f"Premium {product_name} sourced directly from Chitral's mountain regions. "
                                  f"These naturally dried fruits are rich in vitamins, minerals, and antioxidants. "
                                  f"Perfect for snacking, cooking, or as a healthy addition to your diet. "
                                  f"100% natural, no preservatives added. Available in {weight} pack.",
            
            'chitrali-salajit': f"Pure {product_name} extracted from the pristine mountains of Chitral. "
                               f"Salajit (Shilajit) is a natural mineral pitch known for its traditional health benefits. "
                               f"Rich in fulvic acid and over 84 minerals. Authentic Chitrali quality guaranteed. "
                               f"Available in {weight} pack.",
            
            'chitrali-herbs': f"Traditional {product_name} grown in Chitral's fertile valleys. "
                             f"These organic herbs are hand-picked and carefully dried to preserve their natural properties. "
                             f"Perfect for culinary use and traditional remedies. Available in {weight} pack.",
            
            'chitrali-honey': f"Pure {product_name} collected from Chitral's wildflower meadows. "
                             f"This organic honey is raw, unfiltered, and unpasteurized, preserving all natural enzymes and nutrients. "
                             f"Rich flavor with natural sweetness. Available in {weight} jar.",
            
            'chitrali-nuts': f"Fresh {product_name} from Chitral's orchards. "
                            f"These premium nuts are naturally grown without chemicals, rich in healthy fats, protein, and essential nutrients. "
                            f"Perfect for snacking or cooking. Available in {weight} pack.",
            
            'chitrali-spices': f"Authentic {product_name} from Chitral. "
                              f"These traditional spices are sun-dried and ground to preserve their natural flavors and aromas. "
                              f"Essential for Chitrali cuisine. Available in {weight} pack.",
            
            'chitrali-apricots': f"Sweet {product_name} from Chitral's famous apricot orchards. "
                                f"These naturally dried apricots are rich in fiber, vitamins A and C. "
                                f"No added sugar, pure Chitrali quality. Available in {weight} pack.",
            
            'chitrali-grains': f"Organic {product_name} grown in Chitral's fertile soil. "
                              f"These whole grains are naturally grown, rich in fiber and essential nutrients. "
                              f"Perfect for healthy cooking and traditional Chitrali recipes. Available in {weight} pack.",
            
            'chitrali-oils': f"Pure {product_name} cold-pressed from Chitral's finest sources. "
                            f"Natural, unrefined oil rich in healthy fats and nutrients. "
                            f"Perfect for cooking and traditional use. Available in {weight} bottle.",
            
            'chitrali-tea': f"Premium {product_name} from Chitral's mountain regions. "
                           f"Natural, organic tea leaves rich in antioxidants. "
                           f"Traditional brewing methods preserved. Available in {weight} pack.",
            
            'chitrali-jams-preserves': f"Natural {product_name} made from fresh Chitrali fruits. "
                                       f"No artificial preservatives, pure fruit goodness. "
                                       f"Perfect for breakfast and desserts. Available in {weight} jar.",
            
            'chitrali-seeds': f"Premium {product_name} from Chitral. "
                             f"Rich in protein, fiber, and healthy fats. "
                             f"Natural, no chemicals. Perfect for snacking and cooking. Available in {weight} pack.",
            
            'chitrali-pickles': f"Traditional {product_name} made with authentic Chitrali recipes. "
                               f"Naturally preserved, full of flavor. "
                               f"Perfect accompaniment to meals. Available in {weight} jar.",
            
            'chitrali-rice-pulses': f"Organic {product_name} from Chitral's farms. "
                                   f"Naturally grown, rich in protein and fiber. "
                                   f"Perfect for healthy cooking. Available in {weight} pack.",
            
            'chitrali-medicinal-plants': f"Traditional {product_name} from Chitral. "
                                         f"Used in traditional medicine for centuries. "
                                         f"Organic, hand-picked, naturally preserved. Available in {weight} pack.",
            
            'chitrali-wool-products': f"Authentic {product_name} handwoven in Chitral. "
                                      f"Natural wool from Chitral sheep, traditional craftsmanship. "
                                      f"Warm and durable. Available as {weight}.",
            
            'chitrali-traditional-foods': f"Authentic {product_name} prepared with traditional Chitrali recipes. "
                                         f"Natural ingredients, no preservatives. "
                                         f"Ready-to-eat traditional delicacy. Available in {weight} pack.",
        }
        
        return descriptions.get(category_slug, f"Premium {product_name} from Chitral. Authentic quality, natural ingredients. Available in {weight} pack.")

