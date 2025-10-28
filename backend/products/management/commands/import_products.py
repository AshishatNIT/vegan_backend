import csv
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Imports products from the master CSV file into the database.'

    def handle(self, *args, **options):
        # The path to your new, clean, master CSV file.
        # This assumes it's in a 'data' folder at the project root.
        master_csv_path = '../data/all_vegan_products_with_vendor.csv'
        
        self.stdout.write(self.style.SUCCESS('Starting import from master CSV...'))

        with open(master_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Use .get() to avoid errors if a column is missing in a row
                Product.objects.update_or_create(
                    product_link=row.get('product_url'),
                    defaults={
                        'name': row.get('Product Name'),
                        'description': row.get('Description'),
                        'image_url': row.get('Image'),
                        # Convert price to a number, handle cases where it's empty
                        'price': (row.get('Product Price')) if row.get('Product Price') else None,
                        # This assumes you have a 'vegan_status' column, defaults to PENDING otherwise
                        # 'vegan_status': row.get('Vegan Status', 'PENDING'),
                        'product_link': row.get('Product URL'),
                        'vendor': row.get('Vendor'),
                    }
                )

        self.stdout.write(self.style.SUCCESS('Master CSV import finished!'))
