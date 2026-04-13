"""
SEO Helper utilities for ChitralHive
Auto-generates SEO-friendly URLs, meta titles, and descriptions
Optimized for Pakistan-wide SEO for Chitrali products
"""
from django.utils.text import slugify

# Pakistan-wide SEO keywords for Chitrali products
PAKISTAN_CITIES = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar', 'Quetta', 'Faisalabad', 'Multan', 'Hyderabad', 'Gujranwala']
PAKISTAN_SEO_KEYWORDS = [
    'Pakistan', 'online shopping Pakistan', 'buy online Pakistan', 
    'delivery Pakistan', 'Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 
    'Peshawar', 'Quetta', 'Faisalabad', 'Multan', 'Hyderabad', 'Gujranwala',
    'PKR', 'Pakistani', 'Pakistan delivery', 'free shipping Pakistan'
]

# High-intent clusters (keep short; we’ll mix + dedupe for each product)
KEYWORD_CLUSTERS = {
    "general": [
        "buy online Pakistan",
        "price in Pakistan",
        "original",
        "pure",
        "authentic",
        "cash on delivery",
        "home delivery",
        "nationwide delivery",
    ],
    "shilajit": [
        "Shilajit Pakistan",
        "Salajeet Pakistan",
        "Silajit Pakistan",
        "سلاجیت",
        "Himalayan Shilajit",
        "pure shilajit resin",
        "original salajeet",
        "shilajit price in Pakistan",
    ],
    "honey": [
        "pure honey Pakistan",
        "raw honey",
        "organic honey",
        "wild honey",
        "mountain honey",
        "honey price in Pakistan",
    ],
    "dry_fruits": [
        "dry fruits Pakistan",
        "dry fruits price in Pakistan",
        "premium dry fruits",
        "mixed dry fruits",
    ],
    "herbs": [
        "herbal products Pakistan",
        "natural herbs",
        "organic herbs",
        "herbs price in Pakistan",
    ],
    "crafts": [
        "handicrafts Pakistan",
        "Chitrali handicrafts",
        "handmade products Pakistan",
        "traditional Chitrali items",
    ],
}


def generate_seo_url(model_type, slug, parent_slug=None):
    """
    Generate SEO-friendly URL based on model type
    
    Args:
        model_type: 'category', 'product', or 'bundle'
        slug: The slug of the item
        parent_slug: Optional parent slug for nested URLs
    
    Returns:
        SEO-friendly URL string
    """
    if model_type == 'category':
        if parent_slug:
            return f"/categories/{parent_slug}/{slug}"
        return f"/categories/{slug}"
    elif model_type == 'product':
        return f"/products/{slug}"
    elif model_type == 'bundle':
        return f"/bundles/{slug}"
    else:
        return f"/{slug}"


def generate_meta_title(name, model_type='product', brand='ChitralHive', include_pakistan=True):
    """
    Generate SEO-friendly meta title with Pakistan-wide focus
    
    Args:
        name: Product/Category/Bundle name
        model_type: Type of model
        brand: Brand name
        include_pakistan: Whether to include Pakistan in title
    
    Returns:
        SEO-optimized meta title
    """
    pakistan_suffix = " | Pakistan" if include_pakistan else ""
    
    if model_type == 'category':
        return f"{name} - Shop Online in Pakistan{pakistan_suffix} | {brand}"
    elif model_type == 'product':
        return f"{name} - Buy Online in Pakistan{pakistan_suffix} | {brand}"
    elif model_type == 'bundle':
        return f"{name} - Special Bundle{pakistan_suffix} | {brand}"
    else:
        return f"{name}{pakistan_suffix} | {brand}"


def generate_meta_description(description, name, model_type='product', include_pakistan=True):
    """
    Generate SEO-friendly meta description with Pakistan-wide focus
    
    Args:
        description: Base description
        name: Product/Category/Bundle name
        model_type: Type of model
        include_pakistan: Whether to include Pakistan in description
    
    Returns:
        SEO-optimized meta description (max 160 characters)
    """
    if model_type == 'category':
        prefix = f"Shop {name} online in Pakistan"
    elif model_type == 'product':
        prefix = f"Buy {name} online in Pakistan"
    elif model_type == 'bundle':
        prefix = f"Get {name} - Special bundle offer in Pakistan"
    else:
        prefix = f"{name} available online in Pakistan"
    
    # Add Pakistan-wide delivery info
    if include_pakistan:
        pakistan_info = " Free delivery across Pakistan including Karachi, Lahore, Islamabad, Rawalpindi, Peshawar, and all major cities."
    else:
        pakistan_info = ""
    
    # Combine prefix with description, limit to 160 chars
    full_desc = f"{prefix}. {description}{pakistan_info}"
    if len(full_desc) > 160:
        # Truncate description first, then add Pakistan info if space allows
        available_space = 160 - len(prefix) - len(pakistan_info) - 3  # 3 for "..."
        if available_space > 0:
            truncated_desc = description[:available_space] + "..."
            full_desc = f"{prefix}. {truncated_desc}{pakistan_info}"
        else:
            full_desc = f"{prefix}. {description[:157-len(pakistan_info)]}...{pakistan_info}"
    
    return full_desc


def generate_pakistan_seo_keywords(product_name, category_name=None):
    """
    Generate Pakistan-wide SEO keywords for Chitrali products
    
    Args:
        product_name: Name of the product
        category_name: Optional category name
    
    Returns:
        Comma-separated SEO keywords string
    """
    
    name = (product_name or "").strip()
    cat = (category_name or "").strip()
    lower = f"{name} {cat}".lower()

    if any(k in lower for k in ["shilajit", "salajeet", "salajit", "silajit", "sila jit", "سلاجیت"]):
        bucket = "shilajit"
    elif any(k in lower for k in ["honey", "shehad", "شہد"]):
        bucket = "honey"
    elif any(k in lower for k in ["dry fruit", "dryfruit", "nuts", "badam", "pista", "akhrot", "kishmish"]):
        bucket = "dry_fruits"
    elif any(k in lower for k in ["herb", "herbal", "ajwain", "kalonji", "saunf"]):
        bucket = "herbs"
    elif any(k in lower for k in ["craft", "shawl", "topi", "handmade", "handicraft"]):
        bucket = "crafts"
    else:
        bucket = "general"

    keywords = []

    # Product + commercial intents
    if name:
        keywords.extend([
            f"{name} Pakistan",
            f"buy {name} online Pakistan",
            f"{name} price in Pakistan",
        ])

    # Category intents
    if cat:
        keywords.extend([
            f"{cat} Pakistan",
            f"buy {cat} online Pakistan",
        ])

    # High intent cluster + general
    keywords.extend(KEYWORD_CLUSTERS.get(bucket, []))
    if bucket != "general":
        keywords.extend(KEYWORD_CLUSTERS["general"])

    # City modifiers (keep top 5 to avoid spam)
    for city in ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar']:
        if name:
            keywords.append(f"buy {name} in {city}")

    # Brand anchors
    keywords.extend(["Chitral Hive", "Chitral Hive Pakistan", "Chitrali products Pakistan"])

    # Dedupe (case-insensitive) and cap length
    seen = set()
    out = []
    for k in keywords:
        k = (k or "").strip()
        if not k:
            continue
        key = k.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(k)
        if len(out) >= 28:
            break

    return ", ".join(out)


def generate_seo_slug(name, existing_slug=None, model_instance=None):
    """
    Generate SEO-friendly slug from name
    
    Args:
        name: The name to slugify
        existing_slug: Optional existing slug to check uniqueness
        model_instance: Optional model instance to check against
    
    Returns:
        Unique SEO-friendly slug
    """
    base_slug = slugify(name)
    
    # If slug already exists and is different, append number
    if model_instance:
        Model = model_instance.__class__
        counter = 1
        slug = base_slug
        while Model.objects.filter(slug=slug).exclude(pk=model_instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug
    
    return base_slug

