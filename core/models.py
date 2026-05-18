from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Business(models.Model):
    name = models.CharField(max_length=200)
    owner_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True, help_text="GST Identification Number")
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)
    is_subscription_active = models.BooleanField(default=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    festival_offer_enabled = models.BooleanField(default=False, help_text="Global toggle for Festival Offers")
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

