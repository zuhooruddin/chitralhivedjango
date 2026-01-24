"""
Seed products from selected Chitrali sites after clearing existing products.
Run: python manage.py seed_products_from_sites
"""
from decimal import Decimal
import os
import random
import time
from urllib.parse import urljoin, urlparse

import requests

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from inara.models import Category, Item, CategoryItem, ItemGallery, ItemTags



class Command(BaseCommand):
    help = "Clear all products and seed products from listed Chitrali sites"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Removing existing products from target categories..."))
        categories = self.load_target_categories()
        self.clear_products(categories)

        self.stdout.write(self.style.SUCCESS("Seeding products for Dry Fruits and Honey..."))
        created = self.seed_products(categories)

        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))

    def clear_products(self, categories):
        target_category_ids = [cat.id for cat in categories.values()]
        item_ids = list(
            CategoryItem.objects.filter(categoryId__in=target_category_ids).values_list("itemId", flat=True)
        )
        if not item_ids:
            return
        CategoryItem.objects.filter(itemId__in=item_ids).delete()
        ItemGallery.objects.filter(itemId__in=item_ids).delete()
        ItemTags.objects.filter(itemId__in=item_ids).delete()
        Item.objects.filter(id__in=item_ids).delete()

    def load_target_categories(self):
        category_defs = [
            ("chitrali-dry-fruits", "Dry Fruits"),
            ("chitrali-dry-fruits-almonds", "Dry Fruits - Almonds"),
            ("chitrali-dry-fruits-walnuts", "Dry Fruits - Walnuts"),
            ("chitrali-dry-fruits-apricots", "Dry Fruits - Apricots"),
            ("chitrali-honey", "Chitrali Honey"),
            ("chitrali-honey-wild-honey", "Chitrali Honey - Wild Honey"),
            ("chitrali-honey-organic-honey", "Chitrali Honey - Organic Honey"),
            ("chitrali-honey-sidr-honey", "Chitrali Honey - Sidr Honey"),
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
        random.seed(42)
        sites = [
            {
                "name": "northendryfruits",
                "base": "https://www.northendryfruits.com/shop",
                "max": 120,
                "default_category": "dry-fruits",
            },
            {
                "name": "chitralinaturals_honey",
                "base": "https://chitralinaturals.com/product-category/honey/",
                "max": 80,
                "default_category": "chitrali-honey",
            },
            {
                "name": "shubinak_honey",
                "base": "https://www.shubinak.com/collections/honey",
                "max": 80,
                "default_category": "chitrali-honey",
            },
        ]

        products = []
        for site in sites:
            products.extend(
                self.fetch_products_from_site(
                    site["base"],
                    site["max"],
                    default_category=site["default_category"],
                )
            )

        created = 0
        ext_pos_id = 200000

        ext_pos_id = self.get_next_ext_pos_id()
        for index, product in enumerate(products, start=1):
            category = categories.get(product["category"])
            if not category:
                continue

            slug_base = slugify(product["name"])
            slug = f"{slug_base}-{ext_pos_id}"
            sku = f"CHIT-SRC-{ext_pos_id:06d}"
            if Item.objects.filter(sku=sku).exists():
                ext_pos_id += 1
                sku = f"CHIT-SRC-{ext_pos_id:06d}"

            is_new = 1 if index % 7 == 0 else 0
            is_featured = 1 if index % 13 == 0 else 0

            image_path = self.download_image(product["image"], ext_pos_id)
            if not image_path:
                continue

            item = Item.objects.create(
                extPosId=ext_pos_id,
                name=product["name"],
                slug=slug,
                sku=sku,
                image=image_path,
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
                isNewArrival=is_new,
                isFeatured=is_featured,
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

    def fetch_products_from_site(self, base_url, max_products, default_category):
        products = []
        shopify_products = self.fetch_shopify_products(base_url, max_products, default_category)
        if shopify_products:
            return shopify_products

        html_products = self.fetch_html_products(base_url, max_products, default_category)
        return html_products

    def fetch_shopify_products(self, base_url, max_products, default_category):
        products = []
        for endpoint in ("/products.json?limit=250", "/collections/all/products.json?limit=250"):
            try:
                url = urljoin(base_url, endpoint)
                resp = requests.get(url, timeout=20)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for product in data.get("products", []):
                    title = product.get("title") or ""
                    image = ""
                    images = product.get("images") or []
                    if images:
                        image = images[0].get("src") or ""
                    variants = product.get("variants") or []
                    price = None
                    if variants:
                        price = variants[0].get("price")
                    if not title or not image:
                        continue
                    products.append(
                        {
                            "name": title.strip(),
                            "category": self.infer_category(title, default_category),
                            "price": self.safe_price(price, 600),
                            "sale_price": self.safe_price(price, 550),
                            "image": image,
                            "source": base_url,
                        }
                    )
                    if len(products) >= max_products:
                        return products
            except Exception:
                continue
        return products

    def fetch_html_products(self, base_url, max_products, default_category):
        products = []
        try:
            resp = requests.get(base_url, timeout=20)
            if resp.status_code != 200:
                return products
            html = resp.text
        except Exception:
            return products

        links = self.extract_links(html, base_url)
        product_links = [link for link in links if "/product" in link or "/products/" in link]

        for link in product_links:
            if len(products) >= max_products:
                break
            product = self.fetch_product_page(link, base_url, default_category)
            if product:
                products.append(product)
            time.sleep(0.4)

        return products

    def fetch_product_page(self, url, base_url, default_category):
        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                return None
            html = resp.text
        except Exception:
            return None

        title = self.extract_title(html)
        image = self.extract_primary_image(html, base_url)
        if not title or not image:
            return None

        return {
            "name": title,
            "category": self.infer_category(title, default_category),
            "price": 700,
            "sale_price": 650,
            "image": image,
            "source": base_url,
        }

    def extract_links(self, html, base_url):
        links = set()
        for token in html.split("href="):
            if not token:
                continue
            quote = token[0]
            if quote not in ("'", '"'):
                continue
            end = token.find(quote, 1)
            if end == -1:
                continue
            href = token[1:end].strip()
            if href.startswith("javascript:") or href.startswith("#"):
                continue
            full = urljoin(base_url, href)
            links.add(full)
        return list(links)

    def extract_title(self, html):
        for tag in ("<title>", "<h1>", "<h1 "):
            idx = html.lower().find(tag)
            if idx == -1:
                continue
            if tag == "<h1 ":
                start = html.lower().find(">", idx)
            else:
                start = idx + len(tag)
            if start == -1:
                continue
            end = html.lower().find("</", start)
            if end == -1:
                continue
            text = html[start:end].strip()
            text = " ".join(text.split())
            if text:
                return text[:120]
        return None

    def extract_primary_image(self, html, base_url):
        candidates = []
        for token in html.split("src="):
            if not token:
                continue
            quote = token[0]
            if quote not in ("'", '"'):
                continue
            end = token.find(quote, 1)
            if end == -1:
                continue
            src = token[1:end].strip()
            if not src:
                continue
            if "logo" in src.lower() or "icon" in src.lower():
                continue
            full = urljoin(base_url, src)
            candidates.append(full)
        if candidates:
            return candidates[0]
        return None

    def infer_category(self, title, default_category):
        title_lower = title.lower()
        if "salajit" in title_lower or "shilajit" in title_lower:
            return default_category
        if "honey" in title_lower:
            if "sidr" in title_lower:
                return "chitrali-honey-sidr-honey"
            if "organic" in title_lower:
                return "chitrali-honey-organic-honey"
            if "wild" in title_lower:
                return "chitrali-honey-wild-honey"
            return "chitrali-honey"
        if "almond" in title_lower:
            return "chitrali-dry-fruits-almonds"
        if "walnut" in title_lower:
            return "chitrali-dry-fruits-walnuts"
        if "apricot" in title_lower:
            return "chitrali-dry-fruits-apricots"
        return default_category

    def get_next_ext_pos_id(self):
        latest = Item.objects.order_by("-extPosId").first()
        if latest and latest.extPosId:
            return latest.extPosId + 1
        return 200000

    def safe_price(self, price, fallback):
        try:
            return int(float(price))
        except Exception:
            return fallback

    def download_image(self, url, ext_pos_id):
        if not url:
            return None
        try:
            response = requests.get(url, timeout=25)
            if response.status_code != 200:
                return None
            content_type = response.headers.get("Content-Type", "").lower()
            ext = ".jpg"
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"
            elif "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            file_name = f"{ext_pos_id}{ext}"
            media_root = os.path.join(os.getcwd(), "media")
            target_dir = os.path.join(media_root, "item_image")
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return os.path.join("item_image", file_name)
        except Exception:
            return None

