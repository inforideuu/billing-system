import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Business
from inventory.models import Product
from billing.models import Invoice, InvoiceItem, Customer
from django.utils import timezone

def create_slow_mover():
    # 1. Get first active business and user
    user = User.objects.first()
    business = Business.objects.first()
    
    if not business or not user:
        print("No business or user found.")
        return
        
    # 2. Create the Slow Moving Test Product
    product, created = Product.objects.get_or_create(
        sku="SLOW-TEST-001",
        business=business,
        defaults={
            'name': "Premium Slow-Moving Gadget",
            'price': 499.00,
            'gst_rate': 18.0,
            'item_type': 'PRODUCT',
            'stock_quantity': 50, # Has plenty of stock
        }
    )
    
    if not created:
        print("Test product already exists. Resetting its invoices for slow mover test.")
        InvoiceItem.objects.filter(product=product).delete()

    # 3. Create a Customer
    customer, _ = Customer.objects.get_or_create(
        business=business, 
        name="Test Customer"
    )

    # 4. Create an Invoice exactly 5 days ago (within 30 days)
    past_date = timezone.now() - timedelta(days=5)
    
    invoice = Invoice.objects.create(
        business=business,
        user=user,
        customer=customer,
        total_amount=product.price,
        gst_amount=product.price * (product.gst_rate / 100),
        cgst_amount=(product.price * (product.gst_rate / 100)) / 2,
        sgst_amount=(product.price * (product.gst_rate / 100)) / 2,
        payment_method="CASH",
        status="PAID",
    )
    # Manually override auto_now_add
    Invoice.objects.filter(id=invoice.id).update(date=past_date)

    # 5. Create an InvoiceItem with exactly 1 quantity (Makes it a slow mover: 0 < units <= 2)
    InvoiceItem.objects.create(
        invoice=invoice,
        product=product,
        quantity=1,
        unit_price=product.price,
        original_unit_price=product.price,
        total_price=product.price,
        gst_rate=product.gst_rate
    )
    
    print(f"Successfully created slow-moving test product '{product.name}' with 1 sale 5 days ago.")

if __name__ == '__main__':
    create_slow_mover()
