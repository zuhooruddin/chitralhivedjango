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
        source_urls = [
            "https://www.northendryfruits.com/shop",
            "https://store26725.store.link/",
        ]
        products = []
        for url in source_urls:
            products.extend(self.fetch_products(url))

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
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
        }
        # Try Shopify-style JSON endpoints first (fast, structured)
        shopify_products = self.fetch_shopify_products(shop_url, headers)
        if shopify_products:
            return shopify_products

        # Try WooCommerce/WordPress Store API
        wc_products = self.fetch_woocommerce_products(shop_url, headers)
        if wc_products:
            return wc_products

        try:
            resp = requests.get(shop_url, timeout=25, headers=headers)
            if resp.status_code != 200:
                return products
            html = resp.text
        except Exception:
            return products

        # Try JSON-LD product listings on the shop page
        jsonld_products = self.extract_jsonld_products(html, shop_url)
        if jsonld_products:
            return jsonld_products

        embedded_products = self.extract_embedded_products(html, shop_url)
        if embedded_products:
            return embedded_products

        sitemap_products = self.fetch_products_from_sitemap(shop_url, headers=headers)
        if sitemap_products:
            return sitemap_products

        product_links = self.extract_product_links(html, shop_url)
        for link in product_links:
            product = self.fetch_product_page(link, shop_url, headers=headers)
            if product:
                products.append(product)
            time.sleep(0.3)

        return products

    def fetch_woocommerce_products(self, base_url, headers):
        products = []
        endpoints = [
            "/wp-json/wc/store/products",
            "/wp-json/wc/store/products?per_page=100",
            "/wp-json/wc/store/products?page=1&per_page=100",
            "/wp-json/wc/store/v1/products",
            "/wp-json/wc/store/v1/products?per_page=100",
        ]
        for endpoint in endpoints:
            try:
                url = urljoin(base_url, endpoint)
                resp = requests.get(url, timeout=20, headers=headers)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                if not isinstance(data, list):
                    continue
                for product in data:
                    title = (product.get("name") or "").strip()
                    images = product.get("images") or []
                    image = images[0].get("src") if images else ""
                    if image:
                        image = urljoin(base_url, image)
                    price = product.get("prices", {}).get("price") or product.get("price")
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

    def fetch_shopify_products(self, base_url, headers):
        products = []
        for endpoint in ("/products.json?limit=250", "/collections/all/products.json?limit=250"):
            try:
                url = urljoin(base_url, endpoint)
                resp = requests.get(url, timeout=20, headers=headers)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for product in data.get("products", []):
                    title = (product.get("title") or "").strip()
                    images = product.get("images") or []
                    image = images[0].get("src") if images else ""
                    if image:
                        image = urljoin(base_url, image)
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

    def fetch_product_page(self, url, base_url, headers=None):
        try:
            resp = requests.get(url, timeout=25, headers=headers)
            if resp.status_code != 200:
                return None
            html = resp.text
        except Exception:
            return None

        title = self.extract_title(html)
        image = self.extract_primary_image(html, base_url) or self.extract_meta_image(html, base_url)
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
        # Prefer srcset if available
        for match in re.findall(r'srcset=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            srcset = match.strip()
            if not srcset:
                continue
            first = srcset.split(",")[0].strip().split(" ")[0]
            if first:
                return urljoin(base_url, first)
        # Common lazy-load attributes
        for attr in ("data-src", "data-original", "data-lazy", "data-srcset"):
            for match in re.findall(rf'{attr}=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
                src = match.strip()
                if not src:
                    continue
                if attr == "data-srcset":
                    first = src.split(",")[0].strip().split(" ")[0]
                    if first:
                        return urljoin(base_url, first)
                return urljoin(base_url, src)
        # Fallback to plain src
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

    def extract_meta_image(self, html, base_url):
        for match in re.findall(r'property=["\\\']og:image["\\\']\\s+content=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            return urljoin(base_url, match.strip())
        for match in re.findall(r'name=["\\\']twitter:image["\\\']\\s+content=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            return urljoin(base_url, match.strip())
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

    def extract_embedded_products(self, html, base_url):
        products = []
        script_matches = re.findall(
            r"<script[^>]*>(.*?)</script>", html, flags=re.IGNORECASE | re.DOTALL
        )
        for script in script_matches:
            if "product" not in script.lower() or "image" not in script.lower():
                continue
            for blob in re.findall(r"\{.*?\}", script, flags=re.DOTALL):
                try:
                    data = json.loads(blob)
                except Exception:
                    continue
                name = (data.get("name") or "").strip()
                image = ""
                if isinstance(data.get("image"), list):
                    image = data.get("image")[0]
                else:
                    image = data.get("image") or ""
                if not name or not image:
                    continue
                products.append(
                    {
                        "name": name,
                        "price": 600,
                        "sale_price": 600,
                        "image": urljoin(base_url, image),
                        "source": base_url,
                    }
                )
        return products

    def fetch_products_from_sitemap(self, base_url, headers=None):
        products = []
        sitemap_urls = [
            urljoin(base_url, "/sitemap.xml"),
            urljoin(base_url, "/sitemap_index.xml"),
            urljoin(base_url, "/product-sitemap.xml"),
        ]
        product_links = set()
        for sitemap in sitemap_urls:
            try:
                resp = requests.get(sitemap, timeout=20, headers=headers)
                if resp.status_code != 200:
                    continue
                xml = resp.text
            except Exception:
                continue
            for match in re.findall(r"<loc>(.*?)</loc>", xml, flags=re.IGNORECASE):
                url = match.strip()
                if "/product" in url or "/products/" in url:
                    product_links.add(url)
        for link in list(product_links)[:80]:
            product = self.fetch_product_page(link, base_url, headers=headers)
            if product:
                products.append(product)
            time.sleep(0.2)
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

            image_path = self.download_image(product["image"], ext_pos_id, referer=product["source"])
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

    def download_image(self, url, ext_pos_id, referer=None):
        if not url:
            return None
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/121.0 Safari/537.36",
                    "Referer": referer or url,
                },
                allow_redirects=True,
            )
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
            else:
                parsed_ext = os.path.splitext(url.split("?")[0])[1].lower()
                if parsed_ext in (".png", ".webp", ".jpeg", ".jpg"):
                    ext = parsed_ext if parsed_ext != ".jpeg" else ".jpg"
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

