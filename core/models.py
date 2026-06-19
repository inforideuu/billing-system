from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_3_months = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_6_months = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_year = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_cashiers = models.IntegerField(default=2, help_text="Maximum allowed cashiers (-1 for unlimited)")
    description = models.TextField(blank=True, null=True)
    
    # Feature toggles
    has_festival_offers = models.BooleanField(default=False)
    has_batch_tracking = models.BooleanField(default=False)
    has_smart_insights = models.BooleanField(default=False)
    has_forecasting = models.BooleanField(default=False)
    has_dynamic_pricing = models.BooleanField(default=False)
    has_advanced_reports = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (3m: Rs. {self.price_3_months}, 6m: Rs. {self.price_6_months}, 12m: Rs. {self.price_year})"

class Business(models.Model):
    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True, help_text="GST Identification Number")
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    subscription_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name='businesses')
    is_subscription_active = models.BooleanField(default=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    festival_offer_enabled = models.BooleanField(default=False, help_text="Global toggle for Festival Offers")
    
    # Advanced Intelligent Features Configuration
    smart_insights_enabled = models.BooleanField(default=True, help_text="Toggle Smart Insights module")
    forecasting_enabled = models.BooleanField(default=True, help_text="Toggle Demand Forecasting module")
    dynamic_pricing_enabled = models.BooleanField(default=False, help_text="Toggle Dynamic Pricing system")
    batch_tracking_enabled = models.BooleanField(default=True, help_text="Toggle Batch & Expiry tracking module")
    
    # Alert and Pricing Thresholds
    low_stock_threshold = models.IntegerField(default=5, help_text="Minimum stock level for alerts")
    expiry_alert_days = models.IntegerField(default=30, help_text="Days prior to expiry for warning alerts")
    
    # Dynamic Pricing Adjustment percentages
    pricing_low_stock_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Percent price increase for low stock")
    pricing_high_demand_percent = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, help_text="Percent price increase for high demand")
    pricing_clearance_percent = models.DecimalField(max_digits=5, decimal_places=2, default=20.00, help_text="Percent price discount for near-expiry clearance")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Businesses"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('ADMIN', 'Admin (Shop Owner)'),
        ('CASHIER', 'Cashier'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CASHIER')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_role = 'SUPER_ADMIN' if instance.is_superuser else 'CASHIER'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': default_role})

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        default_role = 'SUPER_ADMIN' if instance.is_superuser else 'CASHIER'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': default_role})
    else:
        instance.profile.save()

class SubscriptionPayment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    upi_utr_number = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    duration_months = models.IntegerField(default=3, help_text="Duration purchased in months")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - {self.status} (Rs. {self.amount} for {self.duration_months}m)"

