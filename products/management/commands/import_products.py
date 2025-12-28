import csv
from django.core.management.base import BaseCommand
from django.db import connection
from io import StringIO
from products.models import Product

class Command(BaseCommand):
    help = 'Imports products from the master CSV file into the database using bulk COPY.'

    def handle(self, *args, **options):
        # Keep your specific file path
        master_csv_path = 'data/data_final_cleaned_v1.csv'
        
        self.stdout.write(self.style.SUCCESS('Starting import from master CSV...'))
        
        # Read CSV and prepare data for COPY (without header)
        data_buffer = StringIO()
        row_count = 0
        skipped_count = 0
        
        try:
            with open(master_csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    # 1. Validation: Skip rows with missing product_url
                    product_url = row.get('Product_URL', '').strip()
                    if not product_url:
                        skipped_count += 1
                        continue
                    
                    # 2. Translation Logic: Fix the Vegan Status
                    # This converts "Yes" -> "VEGAN", "No" -> "NON_VEGAN"
                    raw_status = row.get('Vegan', '').strip().lower()
                    final_status = 'PENDING' # Default
                    
                    if raw_status in ['yes', 'vegan', 'true']:
                        final_status = 'VEGAN'
                    elif raw_status in ['no', 'not vegan', 'non-vegan', 'false']:
                        final_status = 'NON_VEGAN'
                    elif raw_status in ['unsure', 'maybe']:
                        final_status = 'UNSURE'

                    # 3. Prepare the row for the buffer
                    # Note: We must clean newlines/tabs from text fields to avoid breaking the COPY command
                    name = row.get('clean_Product_Name', '').strip().replace('\t', ' ').replace('\n', ' ')
                    image = row.get('Product_Image', '').strip()
                    vendor = row.get('Vendor', '').strip()
                    category = row.get('Product_SubCategory', '').strip()

                    # Write to buffer using tab delimiter
                    data_buffer.write('\t'.join([
                        product_url,
                        name,
                        image,
                        final_status, # Use our translated status
                        vendor,
                        category
                    ]) + '\n')
                    row_count += 1
            
            # 4. Perform the Bulk Insert
            data_buffer.seek(0)
            cursor = connection.cursor()
            
            # Note: This matches the columns you provided in your old script.
            # Make sure your DB table actually has these columns.
            cursor.copy_from(
                data_buffer,
                'products_product',
                columns=('product_link', 'name', 'image_url', 
                        'vegan_status', 'vendor', 'category'),
                null=''
            )
            connection.commit()
            self.stdout.write(self.style.SUCCESS(f'Master CSV import finished! Imported {row_count} rows. Skipped {skipped_count} rows.'))
            
        except FileNotFoundError:
             self.stdout.write(self.style.ERROR(f'File not found: {master_csv_path}'))
        except Exception as e:
            connection.rollback()
            self.stdout.write(self.style.ERROR(f'Error during import: {e}'))
        finally:
            if 'cursor' in locals():
                cursor.close()