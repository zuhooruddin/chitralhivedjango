"""
Management command to create a migration for database indexes.
Run: python manage.py create_indexes_migration
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Creates a migration for the new database indexes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating migration for database indexes...'))
        try:
            call_command('makemigrations', 'inara', verbosity=1)
            self.stdout.write(self.style.SUCCESS('Migration created successfully!'))
            self.stdout.write(self.style.WARNING('Run: python manage.py migrate to apply the indexes'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating migration: {str(e)}'))

