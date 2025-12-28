from django.db import models

class Product(models.Model):
    # The unique URL, this is our primary way of identifying a product.
    product_link = models.URLField(max_length=1024, unique=True, db_index=True)
    
    # The name of the product.
    name = models.CharField(max_length=255)
    
    # A longer text field for the description, can be left blank.
    # description = models.TextField(blank=True, null=True)
    
    # A field for a single, primary image URL.
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    
    # The best field for storing money values to avoid rounding errors.
    # It can store numbers up to 99999.99. Can be left blank.
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    # --- The Vendor Field ---
    vendor = models.CharField(max_length=255, blank=True, null=True)
    
    # --- The Vegan Status Field ---
    # Using choices makes data entry consistent.
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('VEGAN', 'Vegan'),
        ('NON_VEGAN', 'Not Vegan'),
        ('UNSURE', 'Unsure'),
    ]
    vegan_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    # --- Product Category Field ---
    category = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

# --- NEW: Product Import Model for Admin Dashboard ---
class ProductImport(models.Model):
    # This stores the actual CSV file
    csv_file = models.FileField(upload_to='product_imports/')
    
    # Keeps track of when you uploaded it
    date_added = models.DateTimeField(auto_now_add=True)
    
    # Shows if it worked or failed
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Stores the success message or the specific error (e.g., "Missing column 'price'")
    log_message = models.TextField(blank=True)

    def __str__(self):
        return f"Import on {self.date_added.strftime('%Y-%m-%d %H:%M')}"