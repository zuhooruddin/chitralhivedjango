"""
Seed products from selected Chitrali sites after clearing existing products.
Run: python manage.py seed_products_from_sites
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from inara.models import Category, Item, CategoryItem, ItemGallery, ItemTags


class Command(BaseCommand):
    help = "Clear all products and seed products from listed Chitrali sites"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Removing existing products..."))
        self.clear_products()

        self.stdout.write(self.style.SUCCESS("Loading existing categories..."))
        categories = self.load_categories()

        self.stdout.write(self.style.SUCCESS("Seeding products..."))
        created = self.seed_products(categories)

        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))

    def clear_products(self):
        CategoryItem.objects.all().delete()
        ItemGallery.objects.all().delete()
        ItemTags.objects.all().delete()
        Item.objects.all().delete()

    def load_categories(self):
        category_defs = [
            ("chitrali-oils", "Chitrali Oils"),
            ("chitrali-spices", "Chitrali Spices"),
            ("salajit", "Salajit"),
            ("chitrali-honey", "Chitrali Honey"),
            ("chitrali-nuts", "Chitrali Nuts"),
            ("dry-fruits", "Dry Fruits"),
            ("chitrali-traditional-foods", "Chitrali Traditional Foods"),
            ("chitrali-pickles", "Chitrali Pickles"),
            ("chitrali-wool-products", "Chitrali Wool Products"),
            ("chitrali-apricots", "Chitrali Apricots"),
        ]

        categories = {}
        for slug, name in category_defs:
            category = Category.objects.filter(slug=slug).first()
            if not category:
                category = Category.objects.filter(name=name).first()
            if not category:
                self.stdout.write(
                    self.style.WARNING(
                        f"Missing category: {name} (slug: {slug}). Skipping products for it."
                    )
                )
                continue
            categories[slug] = category

        return categories

    def seed_products(self, categories):
        products = [
            {
                "name": "Organic Chia Seeds",
                "category": "dry-fruits",
                "price": 399,
                "sale_price": 349,
                "image": "item_image/dummy_1rF5WS1.jpg",
                "source": "https://chitralorganic.com/",
            },
            {
                "name": "Pure Chitrali Salajit Resin",
                "category": "salajit",
                "price": 1299,
                "sale_price": 1199,
                "image": "item_image/dummy_2k7K5FL.jpg",
                "source": "https://chitralorganic.com/",
            },
            {
                "name": "Moringa Leaf Powder",
                "category": "chitrali-spices",
                "price": 275,
                "sale_price": 249,
                "image": "item_image/dummy_3BGAE2O.jpg",
                "source": "https://chitralorganic.com/",
            },
            {
                "name": "Organic Honeydew Melon Seeds",
                "category": "dry-fruits",
                "price": 549,
                "sale_price": 499,
                "image": "item_image/dummy_6G76VWq.jpg",
                "source": "https://chitralorganic.com/collections/all",
            },
            {
                "name": "Premium Saffron Threads",
                "category": "chitrali-spices",
                "price": 799,
                "sale_price": 749,
                "image": "item_image/dummy_8OzJkgG.jpg",
                "source": "https://chitralorganic.com/collections/all",
            },
            {
                "name": "Chitrali Herbal Tea Mix",
                "category": "chitrali-traditional-foods",
                "price": 450,
                "sale_price": 399,
                "image": "item_image/dummy_8RohhOz.jpg",
                "source": "https://chitralherbs.com/",
            },
            {
                "name": "Dry Mint Leaves",
                "category": "chitrali-spices",
                "price": 220,
                "sale_price": 199,
                "image": "item_image/dummy_aiIXWsn.jpg",
                "source": "https://chitralherbs.com/",
            },
            {
                "name": "Handmade Pakol Cap",
                "category": "chitrali-wool-products",
                "price": 1200,
                "sale_price": 999,
                "image": "item_image/Chitrali_Pakol_cap.png",
                "source": "https://chitralhouse.com/",
            },
            {
                "name": "Chitrali Wool Shawl",
                "category": "chitrali-wool-products",
                "price": 2800,
                "sale_price": 2499,
                "image": "item_image/dummy_AjvDSMY.jpg",
                "source": "https://chitralhouse.com/",
            },
            {
                "name": "Cold-Pressed Walnut Oil",
                "category": "chitrali-oils",
                "price": 1500,
                "sale_price": 1399,
                "image": "item_image/dummy_D9NcGGX.jpg",
                "source": "https://chitralbazar.com/",
            },
            {
                "name": "Spicy Chitrali Pickle",
                "category": "chitrali-pickles",
                "price": 650,
                "sale_price": 599,
                "image": "item_image/dummy_EVXwBrB.jpg",
                "source": "https://chitralbazar.com/",
            },
            {
                "name": "Woolen Socks (Pair)",
                "category": "chitrali-wool-products",
                "price": 650,
                "sale_price": 549,
                "image": "item_image/dummy_Fl9iQpT.jpg",
                "source": "https://chitralwool.com/",
            },
            {
                "name": "Chitrali Wool Gloves",
                "category": "chitrali-wool-products",
                "price": 750,
                "sale_price": 649,
                "image": "item_image/dummy_JpjaCOh.jpg",
                "source": "https://chitralwool.com/",
            },
            {
                "name": "Raw Mountain Honey",
                "category": "chitrali-honey",
                "price": 900,
                "sale_price": 849,
                "image": "item_image/honey-pure-natural-500x500.png",
                "source": "https://chitralshop.com/",
            },
            {
                "name": "Sun-Dried Apricots",
                "category": "chitrali-apricots",
                "price": 750,
                "sale_price": 699,
                "image": "item_image/dummy_KdJF56N.jpg",
                "source": "https://chitralshop.com/",
            },
            {
                "name": "Chitrali Mixed Nuts",
                "category": "chitrali-nuts",
                "price": 1100,
                "sale_price": 999,
                "image": "item_image/dummy_KsTse29.jpg",
                "source": "https://chitralshop.com/",
            },
        ]

        created = 0
        ext_pos_id = 200000

        for product in products:
            category = categories.get(product["category"])
            if not category:
                continue

            slug_base = slugify(product["name"])
            slug = f"{slug_base}-{ext_pos_id}"
            sku = f"CHIT-SRC-{ext_pos_id:06d}"

            item = Item.objects.create(
                extPosId=ext_pos_id,
                name=product["name"],
                slug=slug,
                sku=sku,
                image=product["image"],
                description=(
                    f"{product['name']} sourced from {product['source']} "
                    f"and curated for Chitral Hive."
                ),
                mrp=product["price"],
                salePrice=product["sale_price"],
                discount=max(product["price"] - product["sale_price"], 0),
                stock=Decimal(200),
                stockCheckQty=Decimal(10),
                weight=Decimal("0.5"),
                appliesOnline=1,
                status=Item.ACTIVE,
                manufacturer="Chitral Hive",
                metaTitle=f"{product['name']} - Chitral Hive",
                metaDescription=product["name"],
                timestamp=timezone.now(),
            )

            CategoryItem.objects.create(
                categoryId=category,
                itemId=item,
                level=2,
                status=CategoryItem.ACTIVE,
            )

            created += 1
            ext_pos_id += 1

        return created

