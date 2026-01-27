"""
Seed Chitrali Honey products from shubinak.com and amaltaas.com.pk
Run: python manage.py seed_honey_products
"""
import json
import os
import re
import time
from decimal import Decimal
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from inara.models import Category, CategoryItem, Item, ItemGallery, ItemTags


class Command(BaseCommand):
    help = "Add honey products from shubinak.com and amaltaas.com.pk to Chitrali Honey category"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Loading Chitrali Honey categories..."))
        categories = self.load_categories()
        if not categories["main"]:
            self.stdout.write(self.style.ERROR("Chitrali Honey category not found. Abort."))
            return

        self.stdout.write(self.style.SUCCESS("Fetching products from sources..."))
        source_urls = [
            "https://www.shubinak.com/collections/honey",
            "https://amaltaas.com.pk/shop/honey",
            "https://shifa.zone/collections/honey",
        ]
        products = []
        for url in source_urls:
            fetched = self.fetch_products(url)
            products.extend(fetched)
            self.stdout.write(self.style.SUCCESS(f"  Found {len(fetched)} products from {url}"))

        self.stdout.write(self.style.SUCCESS(f"Seeding {len(products)} honey products..."))
        created = self.seed_products(products, categories)
        self.stdout.write(self.style.SUCCESS(f"Created {created} honey products."))

    def load_categories(self):
        main = Category.objects.filter(
            name__iexact="Chitrali Honey",
            slug="chitrali-honey"
        ).first()
        
        organic = Category.objects.filter(
            name__iexact="Chitrali Honey - Organic Honey",
            slug="chitrali-honey-organic-honey"
        ).first()
        
        sidr = Category.objects.filter(
            name__iexact="Chitrali Honey - Sidr Honey",
            slug="chitrali-honey-sidr-honey"
        ).first()
        
        wild = Category.objects.filter(
            name__iexact="Chitrali Honey - Wild Honey",
            slug="chitrali-honey-wild-honey"
        ).first()

        return {
            "main": main,
            "organic": organic,
            "sidr": sidr,
            "wild": wild,
        }

    def fetch_products(self, shop_url):
        products = []
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
        }
        
        # Try Shopify JSON first (shubinak.com uses Shopify)
        shopify_products = self.fetch_shopify_products(shop_url, headers)
        if shopify_products:
            return shopify_products

        try:
            resp = requests.get(shop_url, timeout=25, headers=headers)
            if resp.status_code != 200:
                return products
            html = resp.text
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Error fetching {shop_url}: {str(e)}"))
            return products

        # Try JSON-LD
        jsonld_products = self.extract_jsonld_products(html, shop_url)
        if jsonld_products:
            return jsonld_products

        # Extract from HTML
        html_products = self.extract_products_from_html(html, shop_url)
        return html_products

    def fetch_shopify_products(self, base_url, headers):
        products = []
        # Try collection JSON endpoint
        collection_slug = base_url.split("/collections/")[-1].split("?")[0] if "/collections/" in base_url else None
        if collection_slug:
            endpoint = f"/collections/{collection_slug}/products.json?limit=250"
        else:
            endpoint = "/products.json?limit=250"
        
        try:
            url = urljoin(base_url, endpoint)
            resp = requests.get(url, timeout=20, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                for product in data.get("products", []):
                    title = (product.get("title") or "").strip()
                    if not title or "honey" not in title.lower():
                        continue
                    images = product.get("images") or []
                    image = images[0].get("src") if images else ""
                    if image:
                        image = urljoin(base_url, image)
                    variants = product.get("variants") or []
                    price = None
                    for variant in variants:
                        if variant.get("price"):
                            price = variant.get("price")
                            break
                    if not price:
                        price = 1000  # Default
                    products.append({
                        "name": title,
                        "price": self.extract_price_value(price, 1000),
                        "sale_price": self.extract_price_value(price, 1000),
                        "image": image,
                        "source": base_url,
                    })
        except Exception:
            pass
        return products

    def extract_jsonld_products(self, html, base_url):
        products = []
        for match in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, flags=re.IGNORECASE | re.DOTALL):
            try:
                data = json.loads(match.strip())
            except Exception:
                continue

            if isinstance(data, dict) and data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    if isinstance(item, dict) and "item" in item:
                        item = item["item"]
                    if not isinstance(item, dict):
                        continue
                    title = (item.get("name") or "").strip()
                    if not title or "honey" not in title.lower():
                        continue
                    image = ""
                    if isinstance(item.get("image"), list):
                        image = item.get("image")[0] if item.get("image") else ""
                    else:
                        image = item.get("image") or ""
                    if not title or not image:
                        continue
                    products.append({
                        "name": title,
                        "price": 1000,
                        "sale_price": 1000,
                        "image": urljoin(base_url, image),
                        "source": base_url,
                    })
        return products

    def extract_products_from_html(self, html, base_url):
        products = []
        # Look for product cards/items
        # Pattern for product titles and images
        product_patterns = [
            r'<h[23][^>]*class=["\'][^"\']*product[^"\']*["\'][^>]*>(.*?)</h[23]>',
            r'<a[^>]*href=["\'][^"\']*product[^"\']*["\'][^>]*>.*?<h[23][^>]*>(.*?)</h[23]>',
        ]
        
        seen_titles = set()
        for pattern in product_patterns:
            for match in re.findall(pattern, html, flags=re.IGNORECASE | re.DOTALL):
                title = re.sub(r'<[^>]+>', '', match).strip()
                title = " ".join(title.split())
                if not title or len(title) < 5 or "honey" not in title.lower():
                    continue
                if title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                
                # Try to find image for this product
                image = self.extract_image_near_text(html, title, base_url)
                if not image:
                    continue
                
                # Extract price
                price = self.extract_price_from_html(html, title)
                
                products.append({
                    "name": title,
                    "price": price or 1000,
                    "sale_price": price or 1000,
                    "image": image,
                    "source": base_url,
                })
        
        return products

    def extract_image_near_text(self, html, title, base_url):
        # Find image near the product title
        title_clean = re.escape(title[:30])
        pattern = rf'{title_clean}.*?<img[^>]+src=["\']([^"\']+)["\']'
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            src = match.group(1)
            if self.is_valid_image_url(src):
                return urljoin(base_url, src)
        
        # Try data-src or other lazy load attributes
        for attr in ("data-src", "data-original", "data-lazy-src"):
            pattern = rf'{title_clean}.*?<img[^>]+{attr}=["\']([^"\']+)["\']'
            match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
            if match:
                src = match.group(1)
                if self.is_valid_image_url(src):
                    return urljoin(base_url, src)
        
        return None

    def extract_price_from_html(self, html, title):
        # Look for price near the title
        title_clean = re.escape(title[:30])
        # Try PKR/Rs patterns
        pattern = rf'{title_clean}.*?(?:PKR|Rs\.?)\s*([0-9,]+)'
        match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
        if match:
            try:
                return int(match.group(1).replace(",", ""))
            except Exception:
                pass
        return None

    def is_valid_image_url(self, url):
        if not url:
            return False
        url_lower = url.lower()
        bad_patterns = [
            "googletagmanager", "google-analytics", "facebook", "twitter",
            "instagram", "script", "javascript:", "data:text", "logo",
            "icon", "favicon", ".js", ".css", ".json", "api/", "/api/",
        ]
        if any(pattern in url_lower for pattern in bad_patterns):
            return False
        image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"]
        if any(ext in url_lower for ext in image_extensions):
            return True
        image_domains = ["img", "image", "cdn", "static", "media", "assets", "photos", "pics"]
        return any(domain in url_lower for domain in image_domains)

    def extract_price_value(self, price, fallback):
        try:
            return int(float(str(price).replace(",", "")))
        except Exception:
            return fallback

    def seed_products(self, products, categories):
        created = 0
        # Find the highest extPosId starting with 400000 to avoid conflicts
        max_ext_pos = Item.objects.filter(extPosId__gte=400000).aggregate(
            max_id=models.Max('extPosId')
        )['max_id'] or 399999
        ext_pos_id = max_ext_pos + 1

        self.stdout.write(f"Processing {len(products)} products...")
        self.stdout.write(f"Starting extPosId from: {ext_pos_id}")

        for idx, product in enumerate(products, start=1):
            name = product["name"]
            self.stdout.write(f"  [{idx}] {name}")
            
            # Check if product already exists by name or slug
            slug_base = slugify(name)
            if Item.objects.filter(name__iexact=name).exists():
                self.stdout.write(self.style.WARNING(f"      ⚠ Already exists (by name), skipping"))
                continue

            image_url = product.get("image", "")
            self.stdout.write(f"      Image URL: {image_url[:80]}...")
            
            image_path = self.download_image(image_url, ext_pos_id, referer=product["source"])
            if not image_path:
                self.stdout.write(self.style.ERROR(f"      ❌ Failed to download image"))
                continue
            
            self.stdout.write(self.style.SUCCESS(f"      ✓ Image saved: {image_path}"))

            # Ensure unique slug and SKU
            slug = f"{slug_base}-{ext_pos_id}"
            sku = f"HNY-{ext_pos_id:06d}"
            
            # Check if SKU or slug already exists and find next available
            while Item.objects.filter(sku=sku).exists() or Item.objects.filter(slug=slug).exists():
                ext_pos_id += 1
                slug = f"{slug_base}-{ext_pos_id}"
                sku = f"HNY-{ext_pos_id:06d}"

            # Determine which subcategory to use
            subcategory = self.infer_subcategory(name, categories)
            category_name = subcategory.name if subcategory else (categories["main"].name if categories["main"] else "Chitrali Honey")
            
            # Generate SEO-friendly description
            description = self.generate_seo_description(name, category_name)

            try:
                item = Item.objects.create(
                    extPosId=ext_pos_id,
                    name=name,
                    slug=slug,
                    sku=sku,
                    image=image_path,
                    description=description,
                    mrp=product["price"],
                    salePrice=product["sale_price"],
                    discount=0,
                    stock=Decimal(200),
                    stockCheckQty=Decimal(10),
                    weight=Decimal("0.5"),
                    appliesOnline=1,
                    status=Item.ACTIVE,
                    isNewArrival=1 if idx % 5 == 0 else 0,
                    isFeatured=1 if idx % 8 == 0 else 0,
                    manufacturer="Chitral Hive",
                    metaTitle=f"{name} - Buy Online in Pakistan | Chitral Hive",
                    metaDescription=description[:150] if len(description) > 150 else description,
                    timestamp=timezone.now(),
                )

                # Link to main category
                if categories["main"]:
                    CategoryItem.objects.create(
                        categoryId=categories["main"],
                        itemId=item,
                        level=2,
                        status=CategoryItem.ACTIVE,
                    )
                    self.stdout.write(f"      ✓ Linked to: {categories['main'].name}")

                # Link to subcategory if found
                if subcategory:
                    CategoryItem.objects.create(
                        categoryId=subcategory,
                        itemId=item,
                        level=2,
                        status=CategoryItem.ACTIVE,
                    )
                    self.stdout.write(f"      ✓ Linked to: {subcategory.name}")

                created += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"      ❌ Error creating product: {str(e)}"))
            finally:
                ext_pos_id += 1

        return created

    def infer_subcategory(self, product_name, categories):
        """Infer which subcategory a product belongs to based on its name"""
        name_lower = product_name.lower()
        
        # Check for Sidr honey
        if "sidr" in name_lower and categories["sidr"]:
            return categories["sidr"]
        
        # Check for Wild honey
        if "wild" in name_lower and categories["wild"]:
            return categories["wild"]
        
        # Check for Organic honey
        if "organic" in name_lower and categories["organic"]:
            return categories["organic"]
        
        # Default: return None (will only link to main category)
        return None

    def generate_seo_description(self, product_name, category_name):
        """Generate SEO-friendly description for honey products"""
        description = f"{product_name} - Premium {category_name} from Chitral Hive. "
        description += "Discover authentic Chitrali honey sourced from the pristine mountains of Chitral, Pakistan. "
        description += "Our organic honey is pure, natural, and packed with health benefits. "
        description += "Perfect for daily consumption, natural remedies, and culinary uses. "
        description += f"Buy {product_name} online in Pakistan with free shipping on orders over Rs. 2000. "
        description += "100% authentic Chitrali products delivered to your doorstep. "
        description += "Shop now at Chitral Hive - Your trusted source for premium Chitrali honey and organic products."
        
        return description

    def download_image(self, url, ext_pos_id, referer=None):
        if not url:
            return None
        
        if not url.startswith("http://") and not url.startswith("https://"):
            if referer:
                url = urljoin(referer, url)
            else:
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
                return None
            
            # Read first chunk to validate
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) >= 12:
                    break
            
            first_bytes = content[:12]
            is_image = (
                first_bytes.startswith(b'\xff\xd8\xff') or
                first_bytes.startswith(b'\x89PNG\r\n\x1a\n') or
                (first_bytes.startswith(b'RIFF') and b'WEBP' in first_bytes[:12]) or
                first_bytes.startswith(b'GIF87a') or first_bytes.startswith(b'GIF89a')
            )
            
            if not is_image:
                content_type = response.headers.get("Content-Type", "").lower()
                if not any(x in content_type for x in ["image/", "jpeg", "jpg", "png", "webp", "gif"]):
                    return None
            
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
            
            with open(file_path, "wb") as f:
                f.write(content)
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if not os.path.exists(file_path) or os.path.getsize(file_path) < 1024:
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
            
            return os.path.join("item_image", file_name)
        except Exception:
            return None

