import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "retail_billing.settings")
django.setup()

from django.contrib.auth.models import User

username = 'demo_user'
password = 'demo_password'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email='admin@example.com', password=password)
    print(f"Superuser '{username}' created successfully on PostgreSQL.")
else:
    print(f"Superuser '{username}' already exists on PostgreSQL.")
