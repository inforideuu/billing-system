import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
django.setup()

from core.models import Business
from inventory.models import Product, Batch, Category

def seed_batches():
    print("Seeding sample products & batches...")
    
    # Fetch first active business
    business = Business.objects.first()
    if not business:
        print("No business found! Run ensure_demo_shop.py first.")
        return
        
    print(f"Using business: {business.name}")
    
    # Configure business for excellent demo state
    business.smart_insights_enabled = True
    business.forecasting_enabled = True
    business.dynamic_pricing_enabled = True
    business.low_stock_threshold = 10
    business.expiry_alert_days = 30
    business.save()
    print("Configured business thresholds for interactive demonstration.")

    # Create dummy category
    category, _ = Category.objects.get_or_create(
        business=business,
        name="Electronics"
    )

    # Ensure physical products exist
    products = Product.objects.filter(business=business, item_type='PRODUCT')
    if not products.exists():
        print("No physical products found! Proactively seeding default physical products...")
        Product.objects.create(
            business=business,
            category=category,
            sku="MOU-G101",
            name="Super Gaming Mouse",
            price=1200.00,
            gst_rate=18.00,
            item_type="PRODUCT",
            stock_quantity=38
        )
        Product.objects.create(
            business=business,
            category=category,
            sku="KEY-M202",
            name="Ultra Mechanical Keyboard",
            price=3500.00,
            gst_rate=18.00,
            item_type="PRODUCT",
            stock_quantity=38
        )
        products = Product.objects.filter(business=business, item_type='PRODUCT')

    today = date.today()
    
    for product in products:
        print(f"Seeding batches for product: {product.name}")
        
        # Clear existing batches
        product.batches.all().delete()
        
        # 1. Expired Batch (Expired 2 days ago)
        Batch.objects.create(
            business=business,
            product=product,
            batch_number=f"EXP-{product.sku}-99",
            manufacture_date=today - timedelta(days=120),
            expiry_date=today - timedelta(days=2),
            stock_quantity=5,
            initial_quantity=15
        )
        
        # 2. Expiring Soon Batch (Expires in 12 days)
        Batch.objects.create(
            business=business,
            product=product,
            batch_number=f"CLR-{product.sku}-50",
            manufacture_date=today - timedelta(days=90),
            expiry_date=today + timedelta(days=12),
            stock_quantity=8,
            initial_quantity=20
        )
        
        # 3. Healthy Batch (Expires in 360 days)
        Batch.objects.create(
            business=business,
            product=product,
            batch_number=f"HLT-{product.sku}-11",
            manufacture_date=today - timedelta(days=10),
            expiry_date=today + timedelta(days=360),
            stock_quantity=25,
            initial_quantity=30
        )
        
        # Sync product stock quantity!
        product.stock_quantity = 38
        product.save()
        
    print("Products & Batches successfully seeded!")

if __name__ == '__main__':
    seed_batches()
