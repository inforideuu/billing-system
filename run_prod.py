import os
import django
from waitress import serve

if __name__ == "__main__":
    print("="*50)
    print(">>> RETAIL BILLING - ENTERPRISE SCALE SERVER <<<")
    print("Waitress WSGI Server: Capable of 1000+ concurrent loads.")
    
    # 1. Setup Django and run database migrations automatically
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
    
    # Ensure database exists on TiDB Cloud before django.setup() initializes connection
    import MySQLdb
    from pathlib import Path
    db_name = os.environ.get('DB_NAME') or 'test'
    db_user = os.environ.get('DB_USER') or '2hi2kChfmfuNZXu.root'
    db_password = os.environ.get('DB_PASSWORD') or 'H1wlE5nMhhWM4Qab'
    db_host = os.environ.get('DB_HOST') or 'gateway01.ap-southeast-1.prod.aws.tidbcloud.com'
    db_port = int(os.environ.get('DB_PORT') or '4000')
    db_ssl_ca = os.environ.get('DB_SSL_CA')
    
    if not db_ssl_ca:
        base_dir = Path(__file__).resolve().parent
        local_ca = base_dir / 'ca.pem'
        if local_ca.exists():
            db_ssl_ca = str(local_ca)
        else:
            try:
                import certifi
                db_ssl_ca = certifi.where()
            except ImportError:
                for path in [
                    '/etc/ssl/certs/ca-certificates.crt',
                    '/etc/pki/tls/certs/ca-bundle.crt',
                    '/etc/ssl/ca-bundle.pem',
                    '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',
                ]:
                    if os.path.exists(path):
                        db_ssl_ca = path
                        break
                    
    try:
        conn_params = {
            'host': db_host,
            'port': db_port,
            'user': db_user,
            'passwd': db_password,
        }
        if db_ssl_ca:
            if os.name == 'nt':
                conn_params['ssl'] = {}  # Use Windows System Trust Store (Schannel)
            else:
                conn_params['ssl'] = {'ca': db_ssl_ca}
            
        print(f"Connecting to TiDB server to ensure database '{db_name}' exists...")
        conn = MySQLdb.connect(**conn_params)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4;")
        print(f"Database '{db_name}' is ready.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database auto-creation warning: {str(e)}")

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
    from core.models import Business, UserProfile, Plan
    
    # Ensure default Plans exist
    if Plan.objects.count() == 0:
        print("Seeding plans...")
        basic = Plan.objects.create(
            name="Basic",
            price_3_months=1199.00,
            price_6_months=2199.00,
            price_year=3999.00,
            max_cashiers=2,
            description="Essential features for small shops. Includes core billing, simple inventory, and basic dashboard analytics.",
            has_festival_offers=False,
            has_batch_tracking=False,
            has_smart_insights=False,
            has_forecasting=False,
            has_dynamic_pricing=False,
            has_advanced_reports=False
        )
        standard = Plan.objects.create(
            name="Standard",
            price_3_months=2699.00,
            price_6_months=4999.00,
            price_year=8999.00,
            max_cashiers=10,
            description="Perfect for growing businesses. Adds supplier management, purchase orders, batch & expiry tracking, festival offers, and advanced reports.",
            has_festival_offers=True,
            has_batch_tracking=True,
            has_smart_insights=False,
            has_forecasting=False,
            has_dynamic_pricing=False,
            has_advanced_reports=True
        )
        premium = Plan.objects.create(
            name="Premium",
            price_3_months=5399.00,
            price_6_months=9999.00,
            price_year=17999.00,
            max_cashiers=-1,
            description="The complete intelligent store solution. Unlocks all features including Smart AI Insights, Demand Forecasting, Dynamic Auto-Pricing, and unlimited cashier accounts.",
            has_festival_offers=True,
            has_batch_tracking=True,
            has_smart_insights=True,
            has_forecasting=True,
            has_dynamic_pricing=True,
            has_advanced_reports=True
        )
        print("Plans seeded successfully!")
    else:
        premium = Plan.objects.filter(name="Premium").first()

    # Ensure default Business exists
    biz, created = Business.objects.get_or_create(
        name="Zenelait Infotech",
        defaults={
            'owner_name': 'Annamalai',
            'address': 'Chennai, Tamil Nadu',
            'phone': '9884264816',
            'is_subscription_active': True,
            'subscription_plan': premium
        }
    )
    
    if created or not biz.subscription_plan:
        from django.utils import timezone
        from datetime import timedelta
        biz.subscription_plan = premium
        biz.subscription_end_date = timezone.now() + timedelta(days=365)
        biz.save()
    
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
