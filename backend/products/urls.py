from django.urls import path
from .views import product_list_api

# This list defines the URL patterns for the 'products' app.
urlpatterns = [
    # When the URL is empty (relative to the path defined in the main urls.py),
    # call the product_list_api function.
    path('', product_list_api, name='product-list-api'),
]
