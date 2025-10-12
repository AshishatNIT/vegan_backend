README: Website & Database Update Workflow
This guide details the step-by-step process for updating the website whenever the database schema (i.e., the columns in the Product table) is changed. Following these steps ensures that the backend and frontend remain perfectly in sync.

philosophy: The API is a Contract
Think of your API as a contract between your backend (the data provider) and your frontend (the data displayer).

The Backend Says: "I promise to provide data with these specific fields: name, product_link, description, image_url, and price."

The Frontend Says: "Okay, I will build my display expecting to receive those exact fields."

If you change the columns in the database, the backend has changed the terms of the contract. This workflow is the process of updating both sides to agree on the new terms.

🔄 The 3-Phase Update Workflow
When you decide to add, remove, or rename a column, follow these three phases in order.

### Phase 1: Update the Backend (The Data Source)
Goal: Change the database structure and update the API "contract."

Modify the Model (The Blueprint)

File: backend/products/models.py

Action: Edit the Product class to add, remove, or rename fields. This file is the single source of truth for your data structure.

Example: Changing description to be mandatory.

class Product(models.Model):
    # ... other fields
    description = models.TextField() # Was TextField(null=True, blank=True)
    # ... other fields

Run Migrations (Apply the Changes)

Action: In your backend terminal, run these two commands in order.

Step A: Create the migration file. This command compares your new models.py to the database and writes a "plan" for the changes.

python manage.py makemigrations

Step B: Apply the migration. This command executes the plan and alters your live PostgreSQL database.

python manage.py migrate

Update the API View (Fulfill the New Contract)

File: backend/products/views.py

Action: Modify the .values(...) list to match your new model fields exactly. This ensures the JSON data sent from the API adheres to the new contract.

Example: If you added a brand field to the model, you must also add it here.

# backend/products/views.py
def product_list_api(request):
    products = Product.objects.all().values(
        'name', 
        'product_link', 
        'description',
        'image_url', 
        'price',
        'brand' # <-- Added the new field
    )
    return JsonResponse(list(products), safe=False)

### Phase 2: Update the Frontend (The Data Display)
Goal: Teach the website how to understand and display the new data from the API.

Update the JavaScript Logic (Build the New HTML)

File: frontend/script.js

Action: Inside the products.forEach(...) loop, access the new fields from the product object and use them to build your HTML string.

Example: Displaying the new brand field.

// frontend/script.js
card.innerHTML = `
    <img src="${image}" alt="${product.name}">
    <div class="card-content">
        <p class="product-brand">${product.brand || ''}</p> <!-- Display the new brand -->
        <h3>${product.name}</h3>
        <p class="product-description">${description}</p>
        <p class="product-price">${price}</p>
        <a href="${product.product_link}" target="_blank" class="product-link">View Product</a>
    </div>
`;

Update the CSS (Style the New Elements)

File: frontend/style.css

Action: If you added new HTML elements in the previous step (like .product-brand), add corresponding styles to make them look good.

Example:

/* frontend/style.css */
.product-brand {
  font-size: 0.8rem;
  color: var(--text-light-color);
  font-weight: bold;
  margin-bottom: 0.25rem;
}

### Phase 3: Verify the Changes
Goal: Ensure everything is working together correctly.

Run the Server: Make sure your Django server is running from the backend folder: python manage.py runserver.

Hard Refresh the Browser: Open your frontend/index.html file in the browser and press Ctrl+Shift+R (or Cmd+Shift+R on Mac) to bypass the cache and load the latest CSS and JavaScript files.

Inspect: Check that your new fields are appearing correctly on the product cards.

🚨 Common Errors & Troubleshooting
Error: 500 Server Error on the website.

Cause: This almost always means there is a mismatch between your models.py file and your views.py file. The API view is trying to access a field that no longer exists in the model.

Solution: Double-check that every field listed in .values(...) in views.py is spelled exactly the same as it is in your Product model in models.py.