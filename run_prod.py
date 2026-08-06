import os
import django
from waitress import serve

if __name__ == "__main__":
    print("="*50)
    print(">>> RETAIL BILLING - ENTERPRISE SCALE SERVER <<<")
    print("Waitress WSGI Server: Capable of 1000+ concurrent loads.")
    
    # 1. Setup Django and run database migrations automatically
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
    django.setup()
    
    print("Checking database state...")
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            # Check if django_migrations exists
            cursor.execute("SHOW TABLES LIKE 'django_migrations'")
            migrations_exists = cursor.fetchone()
            
            # If django_migrations does not exist, but other tables do, clear the dirty database state
            if not migrations_exists:
                print("django_migrations table not found. Cleaning up potential dirty database state...")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("SHOW TABLES;")
                tables = [row[0] for row in cursor.fetchall()]
                for table in tables:
                    cursor.execute(f"DROP TABLE IF EXISTS `{table}`")
                    print(f"Dropped conflicting table: {table}")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    except Exception as db_err:
        print(f"Database pre-check warning: {str(db_err)}")
        
    print("Running database migrations...")
    from django.core.management import call_command
    call_command('migrate', no_input=True)
    
    # 2. Automatically create default Business and Admin User if none exists
    from django.contrib.auth.models import User
    from core.models import Business, UserProfile
    
    # Ensure default Business exists
    biz, created = Business.objects.get_or_create(
        name="Zenelait Infotech",
        defaults={
            'owner_name': 'Annamalai',
            'address': 'Chennai, Tamil Nadu',
            'phone': '9884264816',
            'is_subscription_active': True
        }
    )
    
    # Ensure super admin 'demo_user' exists in production database
    if not User.objects.filter(username='demo_user').exists():
        print("Initializing super admin 'demo_user'...")
        user = User.objects.create_superuser(
            username='demo_user',
            email='demo_user@zenelait.com',
            password='demo_password'
        )
        profile = user.profile
        profile.role = 'SUPER_ADMIN'
        profile.business = biz
        profile.save()
        print("Super admin 'demo_user' created successfully!")
        
    # Ensure super admin 'admin' exists in production database
    if not User.objects.filter(username='admin').exists():
        print("Initializing super admin 'admin'...")
        user = User.objects.create_superuser(
            username='admin',
            email='admin@zenelait.com',
            password='admin@123'
        )
        profile = user.profile
        profile.role = 'SUPER_ADMIN'
        profile.business = biz
        profile.save()
        print("Super admin 'admin' created successfully!")

    from retail_billing.wsgi import application
    
    # Read port from cloud environment, default to 8000
    port = int(os.environ.get('PORT', 8000))
    print(f"Running on http://0.0.0.0:{port}")
    print("Press Ctrl+C to stop.")
    print("="*50)
    
    # Configuration suitable for heavy concurrency (threads=100+)
    serve(application, host='0.0.0.0', port=port, threads=120, connection_limit=1000)
