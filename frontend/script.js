document.addEventListener('DOMContentLoaded', () => {
    const productContainer = document.getElementById('product-container');
    const loadingMessage = document.getElementById('loading-message');
    // The URL for your running Django API server
    const apiUrl = 'http://127.0.0.1:8000/api/products/';

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(products => {
            loadingMessage.style.display = 'none'; // Hide the loading message

            if (products.length === 0) {
                productContainer.innerHTML = '<p>No products found.</p>';
                return;
            }

            products.forEach(product => {
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