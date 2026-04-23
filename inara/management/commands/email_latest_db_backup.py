import os
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import EmailMessage


class Command(BaseCommand):
    help = "Create latest PostgreSQL backup and email it as attachment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            type=str,
            default="",
            help="Recipient email. Defaults to ORDER_ALERT_EMAILS or EMAIL_HOST_USER",
        )
        parser.add_argument(
            "--keep-local",
            action="store_true",
            help="Keep backup file on disk after emailing",
        )

    def _resolve_recipients(self, to_arg):
        if to_arg.strip():
            return [to_arg.strip()]
        env_value = os.environ.get("ORDER_ALERT_EMAILS", "").strip()
        if env_value:
            return [email.strip() for email in env_value.split(",") if email.strip()]
        return [settings.EMAIL_HOST_USER]

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if db.get("ENGINE") != "django.db.backends.postgresql":
            raise CommandError("This command currently supports PostgreSQL only.")

        recipients = self._resolve_recipients(options["to"])
        if not recipients:
            raise CommandError("No recipient email found.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(settings.BASE_DIR) / "sys" / "db_backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"{db['NAME']}_{timestamp}.sql"

        env = os.environ.copy()
        if db.get("PASSWORD"):
            env["PGPASSWORD"] = db["PASSWORD"]

        command = [
            "pg_dump",
            "-h",
            str(db.get("HOST", "localhost")),
            "-p",
            str(db.get("PORT", "5432")),
            "-U",
            str(db.get("USER")),
            "-d",
            str(db.get("NAME")),
            "-f",
            str(backup_file),
        ]

        self.stdout.write("Creating PostgreSQL backup...")
        dump_result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if dump_result.returncode != 0:
            raise CommandError(
                "pg_dump failed:\n"
                f"{dump_result.stderr.strip() or dump_result.stdout.strip()}"
            )

        self.stdout.write(f"Backup created: {backup_file}")
        email = EmailMessage(
            subject=f"Latest DB Backup - {db['NAME']} - {timestamp}",
            body=(
                f"Attached is the latest database backup.\n\n"
                f"Database: {db['NAME']}\n"
                f"Generated: {timestamp}\n"
                f"Server: {db.get('HOST', 'localhost')}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        email.attach_file(str(backup_file))
        email.send(fail_silently=False)

        self.stdout.write(self.style.SUCCESS(f"Backup emailed to: {', '.join(recipients)}"))

        if not options["keep_local"]:
            backup_file.unlink(missing_ok=True)
            self.stdout.write("Local backup file deleted.")
