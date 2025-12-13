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
    
    keywords = [
        f"{product_name} Pakistan",
        f"{product_name} online Pakistan",
        f"buy {product_name} Pakistan",
        f"{product_name} price in Pakistan",
        "Chitrali products Pakistan",
        "Chitrali products online",
        "buy Chitrali products Pakistan",
    ]
    
    # Add city-specific keywords
    for city in ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Peshawar']:
        keywords.append(f"buy {product_name} in {city}")
    
    if category_name:
        keywords.append(f"{category_name} Pakistan")
        keywords.append(f"{category_name} online Pakistan")
    
    # Add general Pakistan keywords
    keywords.extend([
        "online shopping Pakistan",
        "Pakistan delivery",
        "free shipping Pakistan",
        "Chitral Hive Pakistan"
    ])
    
    return ", ".join(keywords)


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

