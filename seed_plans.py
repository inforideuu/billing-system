import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retail_billing.settings')
django.setup()

from core.models import Plan, Business
from django.utils import timezone
from datetime import timedelta

def seed_plans():
    print("Clearing old plans...")
    Plan.objects.all().delete()
    
    print("Seeding new duration-based plans...")
    
    # 1. Basic Plan
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
    print("Created 'Basic' Plan.")

    # 2. Standard Plan
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
    print("Created 'Standard' Plan.")

    # 3. Premium Plan
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
    print("Created 'Premium' Plan.")

    # Update existing businesses with no plan
    for business in Business.objects.all():
        if not business.subscription_plan:
            business.subscription_plan = premium  # Set existing shops to Premium by default so they don't lose access
            # Ensure they have a subscription end date (e.g. 30 days from now) if none is set
            if not business.subscription_end_date:
                business.subscription_end_date = timezone.now() + timedelta(days=30)
            business.save()
            print(f"Assigned default 'Premium' plan to business '{business.name}'.")

    print("Plan seeding complete.")

if __name__ == "__main__":
    seed_plans()
