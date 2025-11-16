import csv
from django.core.management.base import BaseCommand
from django.db import connection
from io import StringIO
from products.models import Product


class Command(BaseCommand):
    help = 'Imports products from the master CSV file into the database.'

    def handle(self, *args, **options):
        master_csv_path = 'data/big_basket.csv'
        
        self.stdout.write(self.style.SUCCESS('Starting import from master CSV...'))
        
        # Read CSV and prepare data for COPY (without header)
        data_buffer = StringIO()
        row_count = 0
        skipped_count = 0
        
        with open(master_csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Write data rows ONLY (no header) - using same column mappings as your original code
            for row in reader:
                # Skip rows with missing product_url (required field)
                product_url = row.get('Product_URL', '').strip()
                if not product_url:
                    skipped_count += 1
                    continue
                
                data_buffer.write('\t'.join([
                    product_url,
                    row.get('clean_Product_Name', '').strip(),
                    row.get('clean_Product_Description', '').strip(),
                    row.get('Product_Image', '').strip(),
                    row.get('Vegan', 'PENDING').strip(),
                    row.get('Vendor', '').strip(),
                    row.get('Product_SubCategory', '').strip()
                ]) + '\n')
                row_count += 1
        
        # Use COPY for bulk insert
        data_buffer.seek(0)
        cursor = connection.cursor()
        try:
            cursor.copy_from(
                data_buffer,
                'products_product',
                columns=('product_link', 'name', 'description', 'image_url', 
                        'vegan_status', 'vendor', 'category'),
                null=''
            )
            connection.commit()
            self.stdout.write(self.style.SUCCESS(f'Master CSV import finished! Imported {row_count} rows. Skipped {skipped_count} rows with missing product_url.'))
        except Exception as e:
            connection.rollback()
            self.stdout.write(self.style.ERROR(f'Error during import: {e}'))
        finally:
            cursor.close()