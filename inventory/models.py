from django.db import models

class Category(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    hsn_code = models.CharField(max_length=20, blank=True, null=True, help_text="HSN/SAC Code for GST")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="GST percentage (e.g., 18.00)")
    stock_quantity = models.IntegerField(default=0)
    min_stock_level = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    ITEM_TYPE_CHOICES = [
        ('PRODUCT', 'Product'),
        ('SERVICE', 'Service'),
    ]
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES, default='PRODUCT')
    
    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        if self.item_type == 'SERVICE':
            return False
        return self.stock_quantity <= self.min_stock_level

class Supplier(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True, related_name='suppliers')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    gstin = models.CharField(max_length=15, blank=True, null=True, help_text="Supplier GST Number")
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Purchase(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True, related_name='purchases')
    PAYMENT_CHOICES = [('CASH', 'Cash'), ('UPI', 'UPI / Card'), ('CREDIT', 'Credit')]
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='CASH')
    invoice_number = models.CharField(max_length=50, blank=True, null=True, help_text="Supplier Reference Invoice #")
    
    def __str__(self):
        return f"PUR-{self.id} - {self.supplier.name if self.supplier else 'Unknown'}"

class Batch(models.Model):
    business = models.ForeignKey('core.Business', on_delete=models.CASCADE, null=True, blank=True, related_name='batches')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=50)
    manufacture_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    stock_quantity = models.IntegerField(default=0)
    initial_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product.name} (Batch: {self.batch_number}) - Stock: {self.stock_quantity}"

    @property
    def is_expired(self):
        from datetime import date
        return self.expiry_date <= date.today()

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_items')
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.product.item_type == 'PRODUCT':
            self.product.stock_quantity += int(self.quantity)
            self.product.save()
            # If batch is associated, let's sync batch stock!
            if self.batch:
                self.batch.stock_quantity += int(self.quantity)
                self.batch.save()
            
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
