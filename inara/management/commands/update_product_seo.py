"""
Update product SEO fields (description, metaTitle, metaDescription) for Chitral Hive.

Run:
  python manage.py update_product_seo
  python manage.py update_product_seo --dry-run --limit 20
  python manage.py update_product_seo --only-missing
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from inara.models import CategoryItem, Item


def _clean_text(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"\s+", " ", value)
    return value


def _truncate(value: str, max_len: int) -> str:
    value = _clean_text(value)
    if len(value) <= max_len:
        return value
    return value[: max_len - 1].rstrip() + "…"


def _keyword_pack(category_name: Optional[str], product_name: str) -> str:
    name = (category_name or "").lower()
    if "salajit" in name or "shilajit" in name:
        return "pure salajit, shilajit, himalayan, original, authentic"
    if "dry" in name or "fruit" in name:
        return "dry fruits, premium quality, fresh, healthy snack"
    if "honey" in name:
        return "organic honey, pure, raw honey, mountain honey"
    if "nuts" in name:
        return "nuts, premium nuts, healthy fats, protein"
    if "spice" in name or "herb" in name:
        return "spices, herbs, organic, natural"
    if "oil" in name:
        return "cold pressed oil, natural oil, pure"
    if "wool" in name:
        return "handmade, traditional, wool products, chitral"
    if "pickle" in name:
        return "homemade pickles, traditional taste, spicy"
    if "jam" in name or "preserve" in name:
        return "jams, preserves, homemade, natural"
    if "seed" in name:
        return "seeds, organic seeds, healthy"
    return f"{product_name}, chitral, pakistan, buy online"


@dataclass(frozen=True)
class SeoPayload:
    description: str
    meta_title: str
    meta_description: str


def build_seo(product_name: str, category_name: Optional[str]) -> SeoPayload:
    product_name = _clean_text(product_name)
    category_name = _clean_text(category_name or "")

    keywords = _keyword_pack(category_name or None, product_name)
    category_phrase = f" in {category_name}" if category_name else ""

    meta_title = _truncate(
        f"{product_name}{category_phrase} | Buy Online in Pakistan - Chitral Hive",
        150,
    )

    meta_description = _truncate(
        f"Buy {product_name}{category_phrase} online from Chitral Hive. "
        f"Authentic Chitrali quality, safe packaging, nationwide delivery across Pakistan.",
        300,
    )

    # Keep description human-friendly and within 2000 chars.
    description = (
        f"{product_name}{category_phrase} from Chitral Hive.\n\n"
        f"Why you’ll love it:\n"
        f"- Authentic Chitrali quality\n"
        f"- Carefully packed for freshness\n"
        f"- Fast delivery across Pakistan\n\n"
        f"How to use:\n"
        f"- Enjoy daily as needed, or add to your recipes\n\n"
        f"Order now from Chitral Hive and enjoy genuine taste from Chitral."
    )
    description = _truncate(description, 2000)

    return SeoPayload(
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
    )


class Command(BaseCommand):
    help = "Update Item description/metaTitle/metaDescription with friendly SEO content"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Print changes without saving")
        parser.add_argument("--limit", type=int, default=0, help="Limit number of items processed (0 = all)")
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only update items missing description/meta fields",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        limit: int = options["limit"]
        only_missing: bool = options["only_missing"]

        qs = (
            Item.objects.all()
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

        updated = 0
        scanned = 0

        for item in qs.iterator():
            if limit and scanned >= limit:
                break
            scanned += 1

            # Primary category (first active link)
            category_name = None
            try:
                rels = list(getattr(item, "cat_item_itemid").all())
                if rels:
                    category_name = rels[0].categoryId.name if rels[0].categoryId else None
            except Exception:
                category_name = None

            if only_missing:
                if item.description and item.metaTitle and item.metaDescription:
                    continue

            seo = build_seo(item.name, category_name)

            changed = (
                (item.description or "") != seo.description
                or (item.metaTitle or "") != seo.meta_title
                or (item.metaDescription or "") != seo.meta_description
            )

            if not changed:
                continue

            if dry_run:
                self.stdout.write(
                    f"[DRY-RUN] {item.id} {item.name} -> "
                    f"metaTitle='{seo.meta_title}' metaDescription='{seo.meta_description[:80]}...'"
                )
            else:
                item.description = seo.description
                item.metaTitle = seo.meta_title
                item.metaDescription = seo.meta_description
                item.save(update_fields=["description", "metaTitle", "metaDescription"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Scanned: {scanned}, Updated: {updated}, Dry-run: {dry_run}"))


