document.addEventListener('DOMContentLoaded', () => {
    const productContainer = document.getElementById('product-container');
    const loadingMessage = document.getElementById('loading-message');
    const vendorFilterMessage = document.getElementById('vendor-filter-message');
    // The URL for your running Django API server
    const apiUrl = 'https://vegan-backend-1zi7.onrender.com/api/products/';

    // Helper to get vendor from query string
    function getVendorFromQuery() {
        const params = new URLSearchParams(window.location.search);
        return params.get('vendor');
    }

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(products => {
            loadingMessage.style.display = 'none'; // Hide the loading message

            const vendor = getVendorFromQuery();
            let filteredProducts = products;
            if (vendor) {
                filteredProducts = products.filter(product => {
                    // Case-insensitive match for vendor
                    return product.vendor && product.vendor.toLowerCase() === vendor.toLowerCase();
                });
                vendorFilterMessage.style.display = 'block';
                vendorFilterMessage.textContent = `Showing products for vendor: ${vendor}`;
            } else {
                vendorFilterMessage.style.display = 'none';
            }

            if (filteredProducts.length === 0) {
                productContainer.innerHTML = '<p>No products found.</p>';
                return;
            }

            productContainer.innerHTML = '';
            filteredProducts.forEach(product => {
                const card = document.createElement('div');
                card.className = 'product-card';

                // Gracefully handle missing data for price and description
                const price = product.price ? `₹${parseFloat(product.price).toFixed(2)}` : '';
                const description = product.description || 'No description available.';
                const image = product.image_url || 'https://placehold.co/600x400?text=No+Image';

                // The HTML structure for our detailed card
                card.innerHTML = `
                    <img src="${image}" alt="${product.name}" onerror="this.onerror=null;this.src='https://placehold.co/600x400?text=Image+Error';">
                    <div class="card-content">
                        <h3>${product.name}</h3>
                        <p class="product-description">${description}</p>
                        <p class="product-price">${price}</p>
                        <a href="${product.product_link}" target="_blank" class="product-link">View Product</a>
                    </div>
                `;

                productContainer.appendChild(card);
            });
        })
        .catch(error => {
            loadingMessage.style.display = 'none'; // Hide loading message on error too
            console.error('Error fetching products:', error);
            productContainer.innerHTML = '<p class="error-message">Failed to load products. Please make sure the backend server is running and check the console for details.</p>';
        });
});