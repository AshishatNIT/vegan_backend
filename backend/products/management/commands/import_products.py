# backend/products/management/commands/import_products.py
import csv
from django.core.management.base import BaseCommand
from products.models import Product

# This is the main class for the command
class Command(BaseCommand):
    help = 'Imports products from specified CSV files into the database.'

    # This handle() method is what runs when you call the command
    def handle(self, *args, **options):
        
        # =================================================================
        #  ACTION REQUIRED: CUSTOMIZE THIS SECTION FOR YOUR FILES!
        # =================================================================
        
        # 1. Update this list with the names of YOUR csv files.
        #    Make sure these files are in your 'data' folder.
        csv_files = [
            'swiggy_products_with_images.csv', 
            # 'Zepto.csv'
            # Add more file names here if you have them, e.g., 'Instamart.csv'
        ]

        # 2. Update the mappings. For each file, tell the script which
        #    CSV column header corresponds to your database field.
        header_mappings = {
            'swiggy_products_with_images.csv': {'name': 'Product Name', 'link': 'Product Name', 'price': 'Price', 'box_contents': 'Box Contents', 'pack_size': 'Pack Size', 'health_benefits': 'Health Benefits', 'storage_tip': 'Storage Tip', 'images': 'Images'},
            # 'Zepto.csv': {'name': 'item_title', 'link': 'product_url', 'images': 'pictures'}
            # If you had 'Instamart.csv', you'd add a new line for it here.
        }
        # =================================================================
        
        # --- The rest of the script runs automatically ---

        self.stdout.write(self.style.SUCCESS('Starting product import process...'))

        for file_name in csv_files:
            self.stdout.write(f'--> Processing file: {file_name}')
            
            # Get the correct mapping for the current file
            mapping = header_mappings.get(file_name)
            if not mapping:
                self.stdout.write(self.style.ERROR(f'  - Mapping not found for {file_name}. Skipping.'))
                continue
            
            # Get the retailer name from the filename (e.g., 'Blinkit')
            retailer_name = file_name.split('.')[0]

            try:
                # Assuming your 'data' folder is one level up from the 'backend' folder
                with open(f'../data/{file_name}', 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        # Use update_or_create to prevent duplicates
                        Product.objects.update_or_create(
                            product_link=row[mapping['link']],
                            defaults={
                                'name': row[mapping['name']],
                                'image_urls': row[mapping['images']].split(','), # Assumes images are comma-separated
                                'retailer': retailer_name,
                            }
                        )
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'  - ERROR: {file_name} not found in the /data/ folder.'))
            except KeyError as e:
                self.stdout.write(self.style.ERROR(f'  - ERROR: A column header in your mapping was not found in {file_name}. Missing header: {e}'))

        self.stdout.write(self.style.SUCCESS('Product import process finished!'))