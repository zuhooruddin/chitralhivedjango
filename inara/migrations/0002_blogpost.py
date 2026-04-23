from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inara", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("excerpt", models.TextField(max_length=600)),
                ("content", models.TextField()),
                ("featured_image", models.ImageField(blank=True, null=True, upload_to="blog_images/")),
                ("author_name", models.CharField(default="Chitral Hive", max_length=120)),
                ("category", models.CharField(blank=True, max_length=100, null=True)),
                ("tags", models.CharField(blank=True, max_length=500, null=True)),
                ("meta_title", models.CharField(blank=True, max_length=160, null=True)),
                ("meta_description", models.CharField(blank=True, max_length=320, null=True)),
                ("is_featured", models.BooleanField(default=False)),
                (
                    "status",
                    models.IntegerField(
                        choices=[(1, "DRAFT"), (2, "PUBLISHED"), (3, "ARCHIVED")],
                        default=1,
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_blog_posts",
                        to="inara.user",
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="updated_blog_posts",
                        to="inara.user",
                    ),
                ),
            ],
            options={
                "db_table": "blog_post",
                "ordering": ["-published_at", "-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="blogpost",
            index=models.Index(fields=["slug"], name="blog_slug_idx"),
        ),
        migrations.AddIndex(
            model_name="blogpost",
            index=models.Index(fields=["status"], name="blog_status_idx"),
        ),
        migrations.AddIndex(
            model_name="blogpost",
            index=models.Index(fields=["published_at"], name="blog_pub_idx"),
        ),
    ]
