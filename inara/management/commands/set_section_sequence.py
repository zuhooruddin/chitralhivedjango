"""
Set a homepage section sequence to a specific category.
Run: python manage.py set_section_sequence --sequence 2 --slug chitrali-dry-fruits
"""
from django.core.management.base import BaseCommand
from inara.models import Category, Individual_BoxOrder, SectionSequence


class Command(BaseCommand):
    help = "Assign a category to a homepage section sequence"

    def add_arguments(self, parser):
        parser.add_argument("--sequence", type=int, required=True, help="Section sequence number")
        parser.add_argument("--slug", type=str, required=True, help="Category slug")

    def handle(self, *args, **options):
        sequence_no = options["sequence"]
        slug = options["slug"]

        category = Category.objects.filter(slug=slug).first()
        if not category:
            self.stdout.write(self.style.ERROR(f"Category not found for slug: {slug}"))
            return

        icon_path = category.icon.name if category.icon else "category_icon/default-category-icon.jpg"
        seo_slug = category.metaUrl if category.metaUrl else category.slug

        Individual_BoxOrder.objects.update_or_create(
            sequenceNo=sequence_no,
            type="section",
            defaults={
                "category_id": category,
                "category_slug": seo_slug,
                "category_name": category.metaTitle if category.metaTitle else category.name,
                "image": icon_path,
                "parent": None,
            },
        )

        SectionSequence.objects.update_or_create(
            sequenceNo=sequence_no,
            defaults={
                "category": category.id,
                "category_slug": seo_slug,
                "name": category.name,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Section {sequence_no} set to {category.name} ({category.slug})"
            )
        )

