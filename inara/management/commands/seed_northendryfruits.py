"""
Seed Dry Fruits categories from https://www.northendryfruits.com/shop
Run: python manage.py seed_northendryfruits
"""
import json
import os
import re
import time
from decimal import Decimal
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from inara.models import Category, CategoryItem, Item, ItemGallery, ItemTags


class Command(BaseCommand):
    help = "Replace Dry Fruits products with items from northendryfruits.com"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Loading target categories..."))
        categories = self.load_categories()
        if not categories["dry_fruits"]:
            self.stdout.write(self.style.ERROR("Dry Fruits category not found. Abort."))
            return

        self.stdout.write(self.style.WARNING("Removing existing products in Dry Fruits categories..."))
        self.clear_products(categories)

        self.stdout.write(self.style.SUCCESS("Fetching products..."))
        products = self.fetch_products("https://www.northendryfruits.com/shop")

        self.stdout.write(self.style.SUCCESS(f"Seeding {len(products)} products..."))
        created = self.seed_products(products, categories)
        self.stdout.write(self.style.SUCCESS(f"Created {created} products."))

    def load_categories(self):
        dry_fruits = Category.objects.filter(name__iexact="Dry Fruits").first()
        almonds = Category.objects.filter(name__iexact="Almonds - Dry Fruits").first()
        walnuts = Category.objects.filter(name__iexact="Walnuts - Dry Fruits").first()
        apricots = Category.objects.filter(name__iexact="Apricots - Dry Fruits").first()

        return {
            "dry_fruits": dry_fruits,
            "almonds": almonds,
            "walnuts": walnuts,
            "apricots": apricots,
        }

    def clear_products(self, categories):
        category_ids = [cat.id for cat in categories.values() if cat]
        item_ids = list(
            CategoryItem.objects.filter(categoryId_id__in=category_ids).values_list("itemId_id", flat=True)
        )
        if not item_ids:
            return
        CategoryItem.objects.filter(itemId_id__in=item_ids).delete()
        ItemGallery.objects.filter(itemId_id__in=item_ids).delete()
        ItemTags.objects.filter(itemId_id__in=item_ids).delete()
        Item.objects.filter(id__in=item_ids).delete()

    def fetch_products(self, shop_url):
        products = []
        # Try Shopify-style JSON endpoints first (fast, structured)
        shopify_products = self.fetch_shopify_products(shop_url)
        if shopify_products:
            return shopify_products

        try:
            resp = requests.get(shop_url, timeout=25)
            if resp.status_code != 200:
                return products
            html = resp.text
        except Exception:
            return products

        # Try JSON-LD product listings on the shop page
        jsonld_products = self.extract_jsonld_products(html, shop_url)
        if jsonld_products:
            return jsonld_products

        product_links = self.extract_product_links(html, shop_url)
        for link in product_links:
            product = self.fetch_product_page(link, shop_url)
            if product:
                products.append(product)
            time.sleep(0.3)

        return products

    def fetch_shopify_products(self, base_url):
        products = []
        for endpoint in ("/products.json?limit=250", "/collections/all/products.json?limit=250"):
            try:
                url = urljoin(base_url, endpoint)
                resp = requests.get(url, timeout=20)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for product in data.get("products", []):
                    title = (product.get("title") or "").strip()
                    images = product.get("images") or []
                    image = images[0].get("src") if images else ""
                    variants = product.get("variants") or []
                    price = variants[0].get("price") if variants else None
                    if not title or not image:
                        continue
                    products.append(
                        {
                            "name": title,
                            "price": self.extract_price_value(price, 600),
                            "sale_price": self.extract_price_value(price, 600),
                            "image": image,
                            "source": base_url,
                        }
                    )
            except Exception:
                continue
        return products

    def extract_product_links(self, html, base_url):
        links = set()
        for match in re.findall(r'href=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            href = match.strip()
            if "/product" not in href and "/products/" not in href:
                continue
            links.add(urljoin(base_url, href))
        return list(links)

    def fetch_product_page(self, url, base_url):
        try:
            resp = requests.get(url, timeout=25)
            if resp.status_code != 200:
                return None
            html = resp.text
        except Exception:
            return None

        title = self.extract_title(html)
        image = self.extract_primary_image(html, base_url)
        if not title or not image:
            return None

        price = self.extract_price(html)
        return {
            "name": title,
            "price": price or 600,
            "sale_price": price or 600,
            "image": image,
            "source": url,
        }

    def extract_title(self, html):
        for tag in ("<h1", "<title>"):
            idx = html.lower().find(tag)
            if idx == -1:
                continue
            start = html.find(">", idx)
            if start == -1:
                continue
            end = html.lower().find("</", start)
            if end == -1:
                continue
            text = html[start + 1:end].strip()
            text = " ".join(text.split())
            if text:
                return text[:140]
        return None

    def extract_primary_image(self, html, base_url):
        for match in re.findall(r'src=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            src = match.strip()
            if not src or "logo" in src.lower() or "icon" in src.lower():
                continue
            return urljoin(base_url, src)
        return None

    def extract_price(self, html):
        for match in re.findall(r"(?:PKR|Rs\.?)\s*([0-9,]+)", html, flags=re.IGNORECASE):
            try:
                return int(match.replace(",", ""))
            except Exception:
                continue
        return None

    def extract_jsonld_products(self, html, base_url):
        products = []
        for match in re.findall(r'<script[^>]+type=["\\\']application/ld\\+json["\\\'][^>]*>(.*?)</script>', html, flags=re.IGNORECASE | re.DOTALL):
            try:
                data = json.loads(match.strip())
            except Exception:
                continue

            # Some pages provide an ItemList
            if isinstance(data, dict) and data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    if isinstance(item, dict) and "item" in item:
                        item = item["item"]
                    if not isinstance(item, dict):
                        continue
                    title = (item.get("name") or "").strip()
                    image = ""
                    if isinstance(item.get("image"), list):
                        image = item.get("image")[0]
                    else:
                        image = item.get("image") or ""
                    url = item.get("url") or base_url
                    if not title or not image:
                        continue
                    products.append(
                        {
                            "name": title,
                            "price": 600,
                            "sale_price": 600,
                            "image": urljoin(base_url, image),
                            "source": urljoin(base_url, url),
                        }
                    )

            # Single Product schema
            if isinstance(data, dict) and data.get("@type") == "Product":
                title = (data.get("name") or "").strip()
                image = ""
                if isinstance(data.get("image"), list):
                    image = data.get("image")[0]
                else:
                    image = data.get("image") or ""
                offers = data.get("offers") or {}
                price = offers.get("price") if isinstance(offers, dict) else None
                if title and image:
                    products.append(
                        {
                            "name": title,
                            "price": self.extract_price_value(price, 600),
                            "sale_price": self.extract_price_value(price, 600),
                            "image": urljoin(base_url, image),
                            "source": base_url,
                        }
                    )
        return products

    def extract_price_value(self, price, fallback):
        try:
            return int(float(str(price).replace(",", "")))
        except Exception:
            return fallback

    def seed_products(self, products, categories):
        created = 0
        ext_pos_id = 300000

        for idx, product in enumerate(products, start=1):
            name = product["name"]
            category = self.infer_category(name, categories)
            if not category:
                continue

            image_path = self.download_image(product["image"], ext_pos_id)
            if not image_path:
                continue

            slug = f"{slugify(name)}-{ext_pos_id}"
            sku = f"DRY-{ext_pos_id:06d}"

            item = Item.objects.create(
                extPosId=ext_pos_id,
                name=name,
                slug=slug,
                sku=sku,
                image=image_path,
                description=f"{name} sourced from {product['source']} and curated for Chitral Hive.",
                mrp=product["price"],
                salePrice=product["sale_price"],
                discount=0,
                stock=Decimal(200),
                stockCheckQty=Decimal(10),
                weight=Decimal("0.5"),
                appliesOnline=1,
                status=Item.ACTIVE,
                isNewArrival=1 if idx % 6 == 0 else 0,
                isFeatured=1 if idx % 11 == 0 else 0,
                manufacturer="Chitral Hive",
                metaTitle=f"{name} - Chitral Hive",
                metaDescription=name,
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

    def infer_category(self, title, categories):
        title_lower = title.lower()
        if "almond" in title_lower and categories["almonds"]:
            return categories["almonds"]
        if "walnut" in title_lower and categories["walnuts"]:
            return categories["walnuts"]
        if "apricot" in title_lower and categories["apricots"]:
            return categories["apricots"]
        return categories["dry_fruits"]

    def download_image(self, url, ext_pos_id):
        if not url:
            return None
        try:
            response = requests.get(url, timeout=30)
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

