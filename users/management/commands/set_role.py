from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Set user role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('role', type=str, help='Role to assign (admin/moderator/user)')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        role = kwargs['role']
        user = User.objects.get(username=username)
        user.role = role
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Role for {username} set to {role}'))
