from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=255)
    product_link = models.URLField(unique=True)
    image_urls = models.JSONField()
    retailer = models.CharField(max_length=50)
    vegan_status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return self.name