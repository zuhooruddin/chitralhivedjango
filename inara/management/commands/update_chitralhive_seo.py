"""
Update Chitral Hive SEO fields for site, categories, and products.

Why this exists:
- Keep metaTitle/metaDescription/metaUrl consistent for the Next.js frontend
- Generate strong Pakistan-focused keyword tags for products
- Safe to run repeatedly (idempotent-ish); supports dry-run

Run:
  python manage.py update_chitralhive_seo --dry-run --limit-items 20
  python manage.py update_chitralhive_seo
"""

from __future__ import annotations

import re
from typing import Optional

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from inara.models import Category, CategoryItem, Item, SiteSettings
from inara.utils.seo_helpers import generate_pakistan_seo_keywords


def _clean_spaces(value: str) -> str:
    value = (value or "").strip()
    return re.sub(r"\s+", " ", value)


def _truncate(value: str, max_len: int) -> str:
    value = _clean_spaces(value)
    if len(value) <= max_len:
        return value
    return value[: max_len - 1].rstrip() + "…"


def build_site_meta() -> tuple[str, str]:
    title = "Chitral Hive | Buy Authentic Chitrali Products Online in Pakistan"
    desc = (
        "Shop authentic Chitrali products online in Pakistan at Chitral Hive — including pure Himalayan "
        "Shilajit (Salajeet), honey, dry fruits, herbs, and crafts from Chitral, Khyber Pakhtunkhwa. "
        "Nationwide delivery across Pakistan."
    )
    return _truncate(title, 500), desc


def build_category_meta(category_name: str) -> tuple[str, str]:
    name = _clean_spaces(category_name) or "Chitrali Products"
    title = f"{name} in Pakistan | Buy Online - Chitral Hive"
    desc = (
        f"Shop authentic {name} online in Pakistan from Chitral Hive. "
        "Original quality from Chitral with nationwide delivery across Pakistan."
    )
    return _truncate(title, 100), _truncate(desc, 500)


def build_item_meta(product_name: str, category_name: Optional[str]) -> tuple[str, str]:
    name = _clean_spaces(product_name) or "Chitrali Product"
    cat = _clean_spaces(category_name or "")
    cat_phrase = f" ({cat})" if cat and cat.lower() not in name.lower() else ""

    title = f"{name}{cat_phrase} in Pakistan | Chitral Hive"
    desc = (
        f"Buy authentic {name}{cat_phrase} online in Pakistan from Chitral Hive. "
        "Cash on delivery & nationwide delivery across Pakistan including Karachi, Lahore, Islamabad, Rawalpindi, Peshawar."
    )
    return _truncate(title, 150), _truncate(desc, 500)


class Command(BaseCommand):
    help = "Update Chitral Hive SEO for SiteSettings, Categories, and Items"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print changes without saving")
        parser.add_argument("--limit-items", type=int, default=0, help="Limit number of items (0 = all)")
        parser.add_argument("--limit-categories", type=int, default=0, help="Limit number of categories (0 = all)")
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only fill missing meta fields (do not overwrite existing non-empty values)",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        limit_items: int = options["limit_items"]
        limit_categories: int = options["limit_categories"]
        only_missing: bool = options["only_missing"]

        base_url = "https://chitralhive.com"

        self.stdout.write(self.style.SUCCESS("Updating Chitral Hive SEO…"))
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN mode (no DB writes)."))

        # 1) Site settings
        site_title, site_desc = build_site_meta()
        site_updated = 0
        site = SiteSettings.objects.order_by("id").first()
        if site:
            changed = False
            if (not only_missing) or not site.site_metatitle:
                if (site.site_metatitle or "") != site_title:
                    site.site_metatitle = site_title
                    changed = True
            if (not only_missing) or not site.site_description:
                if (site.site_description or "") != site_desc:
                    site.site_description = site_desc
                    changed = True
            if changed:
                site_updated = 1
                if not dry_run:
                    site.save(update_fields=["site_metatitle", "site_description"])
        else:
            self.stdout.write(self.style.WARNING("No SiteSettings row found; skipping site meta update."))

        # 2) Categories
        cat_qs = Category.objects.filter(status=Category.ACTIVE, appliesOnline=1).order_by("id")
        if limit_categories:
            cat_qs = cat_qs[:limit_categories]

        cat_scanned = 0
        cat_updated = 0
        for cat in cat_qs.iterator():
            cat_scanned += 1
            title, desc = build_category_meta(cat.name)
            desired_url = f"/categories/{cat.slug or cat.id}"

            changed = False
            if (not only_missing) or not cat.metaTitle:
                if (cat.metaTitle or "") != title:
                    cat.metaTitle = title
                    changed = True
            if (not only_missing) or not cat.metaDescription:
                if (cat.metaDescription or "") != desc:
                    cat.metaDescription = desc
                    changed = True
            if (not only_missing) or not cat.metaUrl:
                if (cat.metaUrl or "") != desired_url:
                    cat.metaUrl = desired_url
                    changed = True

            if changed:
                cat_updated += 1
                if not dry_run:
                    cat.save(update_fields=["metaTitle", "metaDescription", "metaUrl"])

        # 3) Items (products)
        item_qs = (
            Item.objects.filter(status=Item.ACTIVE, appliesOnline=1)
            .prefetch_related(
                Prefetch(
                    "cat_item_itemid",
                    queryset=CategoryItem.objects.select_related("categoryId")
                    .filter(status=CategoryItem.ACTIVE)
                    .order_by("id"),
                )
            )
            .order_by("id")
        )
        item_scanned = 0
        item_updated = 0
        for item in item_qs.iterator():
            if limit_items and item_scanned >= limit_items:
                break
            item_scanned += 1

            category_name = None
            rels = list(getattr(item, "cat_item_itemid").all())
            if rels and rels[0].categoryId:
                category_name = rels[0].categoryId.name

            title, desc = build_item_meta(item.name, category_name)
            desired_url = f"/product/{item.slug}"  # Next.js route

            # Store keywords in itemTag (existing field used as tags/keywords)
            # DB constraint: Item.itemTag is varchar(200) in this project.
            kw = _truncate(generate_pakistan_seo_keywords(item.name, category_name), 200)

            changed = False
            if (not only_missing) or not item.metaTitle:
                if (item.metaTitle or "") != title:
                    item.metaTitle = title
                    changed = True
            if (not only_missing) or not item.metaDescription:
                if (item.metaDescription or "") != desc:
                    item.metaDescription = desc
                    changed = True
            if (not only_missing) or not item.metaUrl:
                if (item.metaUrl or "") != desired_url:
                    item.metaUrl = desired_url
                    changed = True
            if (not only_missing) or not item.itemTag:
                if (item.itemTag or "") != kw:
                    item.itemTag = kw
                    changed = True

            if changed:
                item_updated += 1
                if not dry_run:
                    item.save(update_fields=["metaTitle", "metaDescription", "metaUrl", "itemTag"])

        self.stdout.write(
            self.style.SUCCESS(
                "Done.\n"
                f"- SiteSettings updated: {site_updated}\n"
                f"- Categories scanned: {cat_scanned}, updated: {cat_updated}\n"
                f"- Items scanned: {item_scanned}, updated: {item_updated}\n"
                f"- Base URL assumed: {base_url}"
            )
        )

