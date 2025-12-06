"""
SEO Helper utilities for ChitralHive
Auto-generates SEO-friendly URLs, meta titles, and descriptions
"""
from django.utils.text import slugify


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


def generate_meta_title(name, model_type='product', brand='ChitralHive'):
    """
    Generate SEO-friendly meta title
    
    Args:
        name: Product/Category/Bundle name
        model_type: Type of model
        brand: Brand name
    
    Returns:
        SEO-optimized meta title
    """
    if model_type == 'category':
        return f"{name} - Shop Online | {brand}"
    elif model_type == 'product':
        return f"{name} - Buy Online | {brand}"
    elif model_type == 'bundle':
        return f"{name} - Special Bundle | {brand}"
    else:
        return f"{name} | {brand}"


def generate_meta_description(description, name, model_type='product'):
    """
    Generate SEO-friendly meta description
    
    Args:
        description: Base description
        name: Product/Category/Bundle name
        model_type: Type of model
    
    Returns:
        SEO-optimized meta description (max 160 characters)
    """
    if model_type == 'category':
        prefix = f"Shop {name} online"
    elif model_type == 'product':
        prefix = f"Buy {name} online"
    elif model_type == 'bundle':
        prefix = f"Get {name} - Special bundle offer"
    else:
        prefix = f"{name} available online"
    
    # Combine prefix with description, limit to 160 chars
    full_desc = f"{prefix}. {description}"
    if len(full_desc) > 160:
        full_desc = full_desc[:157] + "..."
    
    return full_desc


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

