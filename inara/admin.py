from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "category", "is_featured", "published_at", "updated_at")
    list_filter = ("status", "is_featured", "category")
    search_fields = ("title", "slug", "excerpt", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
# Register your models here.

