import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
django.setup()

from inventory.models import Product, Batch
from core.models import Business

def seed_alert_data():
    business = Business.objects.first()
    if not business:
        print("No business found!")
        return

    # Enable batch tracking if it isn't
    business.batch_tracking_enabled = True
    business.save()

    print(f"Low Stock Threshold: {business.low_stock_threshold}")
    print(f"Expiry Alert Days: {business.expiry_alert_days}")

    # 1. Create a Low Stock Product
    low_stock_qty = max(1, business.low_stock_threshold - 2)
    p_low, _ = Product.objects.get_or_create(
        sku='TEST-LOW-001',
        business=business,
        defaults={
            'name': 'Extremely Rare Coffee Beans',
            'price': 1500.00,
            'item_type': 'PRODUCT',
            'stock_quantity': low_stock_qty
        }
    )
    p_low.stock_quantity = low_stock_qty
    p_low.save()
    print(f"Created Low Stock Product: {p_low.name} with {p_low.stock_quantity} units.")

    # 2. Create an Expiring Product with Batches
    p_exp, _ = Product.objects.get_or_create(
        sku='TEST-EXP-001',
        business=business,
        defaults={
            'name': 'Organic Fresh Milk',
            'price': 60.00,
            'item_type': 'PRODUCT',
            'stock_quantity': 50
        }
    )
    p_exp.stock_quantity = 50
    p_exp.save()

    # Expiring soon batch (within alert days)
    days_soon = max(1, business.expiry_alert_days - 2)
    Batch.objects.get_or_create(
        product=p_exp,
        business=business,
        batch_number='BATCH-EXP-01',
        defaults={
            'expiry_date': date.today() + timedelta(days=days_soon),
            'stock_quantity': 25,
            'cost_price': 40.00
        }
    )
    
    # Already expired batch
    Batch.objects.get_or_create(
        product=p_exp,
        business=business,
        batch_number='BATCH-EXP-02',
        defaults={
            'expiry_date': date.today() - timedelta(days=5),
            'stock_quantity': 25,
            'cost_price': 40.00
        }
    )
    print(f"Created Expiring/Expired Batches for: {p_exp.name}.")
    
    print("Test data injection complete!")

if __name__ == '__main__':
    seed_alert_data()
