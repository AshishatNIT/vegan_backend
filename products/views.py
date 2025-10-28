from django.http import JsonResponse
from .models import Product

def product_list_api(request):
    """
    API view to fetch all products from the database.
    This now includes all the new fields from our updated model.
    """
    # We select all the fields defined in our Product model.
    # The key change is from 'image_urls' to 'image_url'.
    products = Product.objects.all().values(
        'name', 
        'product_link', 
        'description',
        'image_url', 
        'price',
        'vendor',
    )
    
    # We convert the database query result (a QuerySet) into a list and return it as JSON.
    return JsonResponse(list(products), safe=False)

