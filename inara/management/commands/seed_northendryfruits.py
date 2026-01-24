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
        # Filter out non-image URLs
        def is_valid_image_url(url):
            if not url:
                return False
            url_lower = url.lower()
            # Reject common non-image URLs
            bad_patterns = [
                "googletagmanager", "google-analytics", "facebook", "twitter",
                "instagram", "linkedin", "pinterest", "youtube", "script",
                "javascript:", "data:text", "logo", "icon", "favicon",
                "ads", "advertisement", "tracking", "analytics", "pixel",
                ".js", ".css", ".json", "api/", "/api/", "cdn-cgi",
            ]
            if any(pattern in url_lower for pattern in bad_patterns):
                return False
            # Must look like an image URL
            image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]
            if not any(ext in url_lower for ext in image_extensions):
                # Allow if it's from a CDN or image hosting domain
                image_domains = ["img", "image", "cdn", "static", "media", "assets", "photos", "pics"]
                if not any(domain in url_lower for domain in image_domains):
                    return False
            return True
        
        # Try to find product images in common patterns
        # Look for img tags with product-related classes/ids
        img_patterns = [
            r'<img[^>]+(?:class|id)=["\'][^"\']*(?:product|item|main|featured|gallery)[^"\']*["\'][^>]+src=["\']([^"\']+)["\']',
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]+(?:class|id)=["\'][^"\']*(?:product|item|main|featured|gallery)[^"\']*["\']',
        ]
        for pattern in img_patterns:
            for match in re.findall(pattern, html, flags=re.IGNORECASE):
                src = match.strip()
                if is_valid_image_url(src):
                    return urljoin(base_url, src)
        
        # Prefer srcset if available
        for match in re.findall(r'srcset=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            srcset = match.strip()
            if not srcset:
                continue
            first = srcset.split(",")[0].strip().split(" ")[0]
            if first and is_valid_image_url(first):
                return urljoin(base_url, first)
        
        # Common lazy-load attributes
        for attr in ("data-src", "data-original", "data-lazy", "data-srcset"):
            for match in re.findall(rf'{attr}=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
                src = match.strip()
                if not src:
                    continue
                if attr == "data-srcset":
                    first = src.split(",")[0].strip().split(" ")[0]
                    if first and is_valid_image_url(first):
                        return urljoin(base_url, first)
                elif is_valid_image_url(src):
                    return urljoin(base_url, src)
        
        # Fallback to plain src in img tags
        for match in re.findall(r'<img[^>]+src=["\\\']([^"\\\']+)["\\\']', html, flags=re.IGNORECASE):
            src = match.strip()
            if is_valid_image_url(src):
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
        def is_valid_image_url(url):
            if not url or not isinstance(url, str):
                return False
            url_lower = url.lower()
            bad_patterns = [
                "googletagmanager", "google-analytics", "facebook", "twitter",
                "instagram", "script", "javascript:", "data:text", "logo",
                "icon", "favicon", ".js", ".css", ".json", "api/", "/api/",
            ]
            return not any(pattern in url_lower for pattern in bad_patterns)
        
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
                        image = item.get("image")[0] if item.get("image") else ""
                    else:
                        image = item.get("image") or ""
                    url = item.get("url") or base_url
                    if not title or not image or not is_valid_image_url(image):
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
                    image = data.get("image")[0] if data.get("image") else ""
                else:
                    image = data.get("image") or ""
                offers = data.get("offers") or {}
                price = offers.get("price") if isinstance(offers, dict) else None
                if title and image and is_valid_image_url(image):
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

        self.stdout.write(f"Processing {len(products)} products...")

        for idx, product in enumerate(products, start=1):
            name = product["name"]
            category = self.infer_category(name, categories)
            if not category:
                self.stdout.write(self.style.WARNING(f"  [{idx}] Skipping {name}: No matching category"))
                continue

            image_url = product.get("image", "")
            self.stdout.write(f"  [{idx}] {name}")
            self.stdout.write(f"      Image URL: {image_url[:100]}...")
            
            image_path = self.download_image(image_url, ext_pos_id, referer=product["source"])
            if not image_path:
                self.stdout.write(self.style.ERROR(f"      ❌ Failed to download image"))
                continue
            
            self.stdout.write(self.style.SUCCESS(f"      ✓ Image saved: {image_path}"))

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
            self.stdout.write(self.style.ERROR(f"      No image URL provided"))
            return None
        
        # Normalize URL - make sure it's absolute
        if not url.startswith("http://") and not url.startswith("https://"):
            if referer:
                url = urljoin(referer, url)
            else:
                self.stdout.write(self.style.ERROR(f"      Invalid relative URL: {url}"))
                return None
        
        try:
            response = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/121.0 Safari/537.36",
                    "Referer": referer or url,
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                },
                allow_redirects=True,
                stream=True,
            )
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"      HTTP {response.status_code} for {url[:80]}"))
                return None
            
            # Read first chunk to validate it's an image
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) >= 12:
                    break
            
            # Check magic bytes
            first_bytes = content[:12]
            is_image = (
                first_bytes.startswith(b'\xff\xd8\xff') or  # JPEG
                first_bytes.startswith(b'\x89PNG\r\n\x1a\n') or  # PNG
                (first_bytes.startswith(b'RIFF') and b'WEBP' in first_bytes[:12]) or  # WEBP
                first_bytes.startswith(b'GIF87a') or first_bytes.startswith(b'GIF89a')  # GIF
            )
            
            if not is_image:
                content_type = response.headers.get("Content-Type", "").lower()
                if not any(x in content_type for x in ["image/", "jpeg", "jpg", "png", "webp", "gif"]):
                    self.stdout.write(self.style.ERROR(f"      Not an image (Content-Type: {content_type})"))
                    return None
            
            # Determine extension
            content_type = response.headers.get("Content-Type", "").lower()
            ext = ".jpg"
            if "png" in content_type or first_bytes.startswith(b'\x89PNG'):
                ext = ".png"
            elif "webp" in content_type or (b'WEBP' in first_bytes[:12]):
                ext = ".webp"
            elif "jpeg" in content_type or "jpg" in content_type or first_bytes.startswith(b'\xff\xd8\xff'):
                ext = ".jpg"
            elif "gif" in content_type or first_bytes[:6] in (b'GIF87a', b'GIF89a'):
                ext = ".gif"
            else:
                parsed_ext = os.path.splitext(url.split("?")[0])[1].lower()
                if parsed_ext in (".png", ".webp", ".jpeg", ".jpg", ".gif"):
                    ext = parsed_ext if parsed_ext != ".jpeg" else ".jpg"
            
            file_name = f"{ext_pos_id}{ext}"
            media_root = os.path.join(os.getcwd(), "media")
            target_dir = os.path.join(media_root, "item_image")
            os.makedirs(target_dir, exist_ok=True)
            file_path = os.path.join(target_dir, file_name)
            
            # Write the file
            with open(file_path, "wb") as f:
                f.write(content)  # Write first chunk
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file was written
            if not os.path.exists(file_path) or os.path.getsize(file_path) < 1024:
                self.stdout.write(self.style.ERROR(f"      File too small or not created"))
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
            
            return os.path.join("item_image", file_name)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"      Exception: {str(e)}"))
            return None

