from django.http import JsonResponse
from .models import Product
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def category_list_api(request):
    """
    New Endpoint: Returns a list of all unique categories.
    Used for the sidebar so we don't have to download all products.
    """
    # Get unique categories, exclude nulls, sort alphabetically
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    # Filter out empty strings or None values
    valid_categories = [c for c in categories if c]
    
    return JsonResponse(valid_categories, safe=False)

def product_list_api(request):
    """
    Main Endpoint: Returns products with SERVER-SIDE Filtering and Pagination.
    """
    # 1. Start with all products, ordered by name (essential for pagination stability)
    products_queryset = Product.objects.all().order_by('name', 'id')

    # 2. Filtering Logic: Apply filters BEFORE slicing the page
    vendor = request.GET.get('vendor')
    category = request.GET.get('category')

    if vendor:
        # Case-insensitive match
        products_queryset = products_queryset.filter(vendor__iexact=vendor)
    
    if category:
        # Case-insensitive match
        products_queryset = products_queryset.filter(category__iexact=category)

    # 3. Select only the fields we need (Optimization)
    data = products_queryset.values(
        'name', 
        'product_link', 
        # 'description',
        'image_url', 
        'price',
        'vendor',
        'vegan_status',
        'category'
    )

    # 4. Pagination Logic
    page_number = request.GET.get('page', 1)
    per_page = 20 # Load 20 items at a time
    
    paginator = Paginator(data, per_page)

    try:
        products_page = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, return empty results
        return JsonResponse({
            'results': [],
            'has_next': False,
            'total_pages': paginator.num_pages,
            'current_page': int(page_number)
        })

    # Return the "Package" of data
    return JsonResponse({
        'results': list(products_page.object_list),
        'has_next': products_page.has_next(),
        'total_pages': paginator.num_pages,
        'current_page': products_page.number
    })