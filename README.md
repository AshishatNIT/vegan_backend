Vegan Product Finder - Project README
This document provides a complete guide to setting up, managing, and running the Vegan Product Finder project. The project is designed to scrape product data, clean it, store it in a PostgreSQL database, and display it on a simple, responsive website.

🚀 Project Workflow Overview
The core of this project is a robust data pipeline. Instead of importing messy data directly, we follow a clean, repeatable process:

Clean & Merge Data: Use a Jupyter Notebook to combine multiple raw CSV files into a single, clean master_products.csv.

Update Database Schema: Modify the Django model to define the exact columns we want in our database.

Refresh Database: Run a single command (refresh_products) to automatically delete all old data and import the fresh, clean data from the master CSV.

📂 Project Structure
vegan_checker/
├── backend/                # Django project
│   ├── config/             # Main project settings & URLs
│   ├── products/           # Django app for managing products
│   │   ├── migrations/
│   │   └── management/     # Holds our custom data scripts
│   │       └── commands/
│   │           ├── import_products.py
│   │           └── refresh_products.py
│   ├── manage.py
│   └── venv/
├── data/                   # For raw and master CSV files
│   └── master_products.csv
├── frontend/               # All website files
│   ├── index.html
│   ├── script.js
│   └── style.css
└── notebooks/              # Jupyter Notebooks for data cleaning
    └── Data_Cleaning.ipynb

🛠️ Step 1: Initial Project Setup (One-Time)
Follow these steps to set up the project for the first time.

Clone the Repository & Set Up Backend:

# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install django psycopg2-binary dj-database-url pandas jupyter django-cors-headers

Set Up PostgreSQL Database:

Create a free PostgreSQL database on a service like Render.com.

After creation, find and copy the "External Database URL".

Configure Django Settings (backend/config/settings.py):

Open the settings file and connect your database by replacing the DATABASES section:

import dj_database_url
DATABASES = {
    'default': dj_database_url.parse('YOUR_RENDER_DATABASE_URL_HERE')
}

Add your apps and CORS configuration:

INSTALLED_APPS = [
    # ... other apps
    'products',
    'corsheaders',
]

MIDDLEWARE = [
    # ... other middleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... other middleware
]

# Allow requests from the browser when opening the HTML file directly
CORS_ALLOWED_ORIGINS = [
    "null",
]

🔄 Step 2: The Data Management Workflow (Repeat As Needed)
This is the main workflow you will use whenever you have new data.

### Part A: Clean and Merge Your Raw Data
Use the provided Jupyter Notebook to process your source CSV files.

Place Raw Data: Put your raw CSV files (e.g., Blinkit.csv, swiggy.csv) into the /data/ folder.

Run Jupyter Notebook:

From the project root folder (vegan_checker/), start Jupyter:

jupyter notebook

Open notebooks/Data_Cleaning.ipynb in your browser.

Update the file paths and column mappings in the notebook to match your raw files.

Run all the cells in the notebook. This will generate a clean master_products.csv file in your /data/ folder with the following headers: Product URL, Product Name, Description, Image, Product Price.

### Part B: Update the Database Schema (Only if Columns Change)
You only need to do this if you decide to add, remove, or change a column.

Edit the Model (backend/products/models.py): Update the class to reflect your desired table structure.

# backend/products/models.py
from django.db import models

class Product(models.Model):
    product_link = models.URLField(unique=True, max_length=500)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    price = models.FloatField(null=True, blank=True)
    vegan_status = models.CharField(max_length=20, default='PENDING')

    def __str__(self):
        return self.name

Run Migrations: These commands update your live database to match your model file.

# From the /backend/ folder:
python manage.py makemigrations
python manage.py migrate

### Part C: Refresh the Database with a Single Command
This is the final and most common step. It safely clears all old data and loads the new master_products.csv.

Ensure Helper Scripts are Correct:

The import_products.py script is designed to read your master_products.csv.

# backend/products/management/commands/import_products.py
import csv
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Imports products from the master CSV file.'
    def handle(self, *args, **options):
        # ... (full code from our previous discussion) ...

The refresh_products.py script automates the whole process.

# backend/products/management/commands/refresh_products.py
from django.core.management.base import BaseCommand
from django.core.management import call_command
from products.models import Product

class Command(BaseCommand):
    help = 'Deletes all existing products and re-imports them.'
    def handle(self, *args, **options):
        # ... (full code from our previous discussion) ...

Run the Refresh Command:

# From the /backend/ folder:
python manage.py refresh_products

▶️ Step 3: Running the Application
Start the Backend Server:

# From the /backend/ folder:
python manage.py runserver

Your API is now live at http://127.0.0.1:8000/.

View the Frontend:

Navigate to the /frontend/ folder in your file explorer.

Double-click index.html to open it in your browser.

🔌 API Endpoint Reference
The frontend fetches data from a single API endpoint.

URL: /api/products/

Method: GET

Returns: A JSON array of all products in the database.

API Code (backend/products/views.py):

from django.http import JsonResponse
from .models import Product

def product_list_api(request):
    products = Product.objects.all().values(
        'name', 'product_link', 'description', 'image_url', 'price'
    )
    return JsonResponse(list(products), safe=False)
