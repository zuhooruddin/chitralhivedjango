from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from inara.models import User


class Command(BaseCommand):
    help = 'Create or update super admin user'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@chitralhive.com',
            help='Email address for the super admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='xuhoor77',
            help='Password for the super admin user'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Super Admin',
            help='Name for the super admin user'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']

        try:
            # Check if user exists
            user = User.objects.filter(email=email).first()
            
            if user:
                self.stdout.write(self.style.WARNING(f'User with email {email} already exists.'))
                self.stdout.write(f'Current role: {user.get_role_display()} (role={user.role})')
                self.stdout.write(f'Current status: {user.get_status_display()} (status={user.status})')
                
                # Update user to super admin if not already
                if user.role != User.SUPER_ADMIN:
                    self.stdout.write(self.style.WARNING(f'Updating user role from {user.get_role_display()} to SUPER_ADMIN'))
                    user.role = User.SUPER_ADMIN
                    user.status = User.ACTIVE
                    user.is_active = True
                    user.is_staff = True
                    user.is_superuser = True
                
                # Update password
                user.password = make_password(password)
                user.username = email
                if name:
                    user.name = name
                
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated user {email} to SUPER_ADMIN with new password'))
            else:
                # Create new super admin user
                user = User.objects.create(
                    email=email,
                    username=email,
                    password=make_password(password),
                    name=name,
                    role=User.SUPER_ADMIN,
                    status=User.ACTIVE,
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created super admin user: {email}'))
            
            # Display user info
            self.stdout.write(self.style.SUCCESS('\nUser Details:'))
            self.stdout.write(f'  Email: {user.email}')
            self.stdout.write(f'  Username: {user.username}')
            self.stdout.write(f'  Name: {user.name}')
            self.stdout.write(f'  Role: {user.get_role_display()} (role={user.role})')
            self.stdout.write(f'  Status: {user.get_status_display()} (status={user.status})')
            self.stdout.write(f'  Is Active: {user.is_active}')
            self.stdout.write(f'  Is Staff: {user.is_staff}')
            self.stdout.write(f'  Is Superuser: {user.is_superuser}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            import traceback
            traceback.print_exc()

















