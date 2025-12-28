import csv
from io import StringIO
from django.contrib import admin
from django.db import connection, transaction
from django.utils.html import format_html
from .models import Product, ProductImport

# --- 1. Product Admin (View your products) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'vegan_status', 'category', 'price')
    list_filter = ('vegan_status', 'vendor', 'category')
    search_fields = ('name', 'description')

# --- 2. Product Import Admin (The Upload Dashboard) ---
@admin.register(ProductImport)
class ProductImportAdmin(admin.ModelAdmin):
    list_display = ('date_added', 'status_colored', 'log_message_short')
    readonly_fields = ('status', 'log_message', 'date_added')
    
    # Hide the "Add" button if we are viewing a list, but keep it available logic-wise
    def has_add_permission(self, request):
        return True

    def save_model(self, request, obj, form, change):
        """
        Triggered when the user clicks 'Save' on the upload form.
        """
        # 1. Save the file record to the database first
        super().save_model(request, obj, form, change)
        
        # 2. Run the Import Logic
        try:
            self.process_import(obj)
            obj.status = 'SUCCESS'
            obj.log_message = "Import completed successfully."
        except Exception as e:
            obj.status = 'FAILED'
            obj.log_message = f"Error: {str(e)}"
        
        # 3. Save the final status
        obj.save()

    def process_import(self, import_obj):
        """
        Reads the CSV, Validates, Cleans, and Bulk Inserts into DB.
        """
        csv_path = import_obj.csv_file.path
        
        # Buffer to hold clean data for Postgres COPY
        data_buffer = StringIO()
        
        # Open the uploaded CSV
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # --- A. VALIDATION: Check Headers ---
            # We expect these columns (case-insensitive check)
            required_cols = ['product_url', 'product_name']
            headers = [h.lower() for h in reader.fieldnames] if reader.fieldnames else []
            
            for req in required_cols:
                # We check if 'product_url' or 'Product URL' etc exists
                if not any(req in h for h in headers):
                    raise ValueError(f"Missing required column: {req}. Found: {headers}")

            # --- B. PROCESSING: Read & Clean Rows ---
            for row in reader:
                # 1. Map CSV columns to DB fields
                # Adjust these keys to match your CSV headers exactly!
                p_link = row.get('Product_URL') or row.get('Product URL') or ''
                p_name = row.get('clean_Product_Name') or row.get('Product Name') or ''
                p_image = row.get('Product_Image') or row.get('Image') or ''
                p_vendor = row.get('Vendor') or ''
                p_cat = row.get('Product_SubCategory') or row.get('Category') or ''
                
                # 2. Clean Status (Yes/No -> VEGAN/NON_VEGAN)
                raw_status = row.get('Vegan') or row.get('Vegan Status') or ''
                p_status = 'PENDING'
                
                check = raw_status.strip().lower()
                if check in ['yes', 'vegan', 'true']:
                    p_status = 'VEGAN'
                elif check in ['no', 'non_vegan', 'non-vegan', 'false']:
                    p_status = 'NON_VEGAN'
                elif check in ['unsure', 'maybe']:
                    p_status = 'UNSURE'

                # 3. Validation: Skip rows without a link or name
                if not p_link or not p_name:
                    continue

                # 4. Write to Buffer (Tab-separated for COPY command)
                # Remove tabs/newlines from content to prevent breaking the format
                def clean(val): return str(val).replace('\t', ' ').replace('\n', ' ').strip()
                
                line = f"{clean(p_link)}\t{clean(p_name)}\t{clean(p_image)}\t{p_status}\t{clean(p_vendor)}\t{clean(p_cat)}\n"
                data_buffer.write(line)

        # --- C. DATABASE TRANSACTION (The Atomic Swap) ---
        data_buffer.seek(0) # Rewind buffer to start
        
        with transaction.atomic():
            cursor = connection.cursor()
            
            # 1. Wipe the table (Refresh Strategy)
            cursor.execute("TRUNCATE TABLE products_product RESTART IDENTITY CASCADE;")
            
            # 2. Pour new data in
            cursor.copy_from(
                data_buffer,
                'products_product',
                columns=('product_link', 'name', 'image_url', 'vegan_status', 'vendor', 'category'),
                null=''
            )

    # --- UI Helpers ---
    def status_colored(self, obj):
        colors = {'SUCCESS': 'green', 'FAILED': 'red', 'PENDING': 'orange'}
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.status
        )
    status_colored.short_description = 'Status'

    def log_message_short(self, obj):
        return (obj.log_message[:75] + '...') if len(obj.log_message) > 75 else obj.log_message
    log_message_short.short_description = 'Log'