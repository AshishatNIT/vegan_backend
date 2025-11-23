from django.urls import path
from .views import product_list_api, category_list_api # Import the new view

# This list defines the URL patterns for the 'products' app.
urlpatterns = [
    # When the URL is empty (relative to the path defined in the main urls.py),
    # call the product_list_api function.
    # The main API for products (supports ?page=2&category=Snacks)
    path('', product_list_api, name='product_list_api'),
    
    # The new API just for the sidebar categories
    path('categories/', category_list_api, name='category_list_api'),
]