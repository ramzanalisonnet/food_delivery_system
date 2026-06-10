from database.database import fetch_all, fetch_one, execute_query

class ProductService:
    @staticmethod
    def get_all_products():
        """Get all available products."""
        return fetch_all("SELECT * FROM products WHERE is_available = 1")

    @staticmethod
    def get_all_products_admin():
        """Get all products including unavailable ones (for admin)."""
        return fetch_all("SELECT p.*, u.username as merchant_name FROM products p LEFT JOIN users u ON p.merchant_id = u.user_id ORDER BY p.product_id")

    @staticmethod
    def get_product_by_id(product_id):
        return fetch_one("SELECT * FROM products WHERE product_id = ?", (product_id,))

    @staticmethod
    def get_merchant_products(merchant_id):
        return fetch_all("SELECT * FROM products WHERE merchant_id = ? AND is_available = 1", (merchant_id,))

    @staticmethod
    def add_product(name, price, merchant_id):
        """Add a new product to the catalog."""
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        
        try:
            price_float = float(price)
            if price_float <= 0:
                raise ValueError("Price must be positive")
        except (TypeError, ValueError):
            raise ValueError("Invalid price format")
        
        query = "INSERT INTO products (product_name, price, merchant_id) VALUES (?, ?, ?)"
        execute_query(query, (name.strip(), price_float, merchant_id))
        
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (merchant_id, 'ADD_PRODUCT', 'products', None, f"Added product: {name} at ${price_float:.2f}")
        )

    @staticmethod
    def update_product(product_id, name, price):
        """Update an existing product."""
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        
        try:
            price_float = float(price)
            if price_float <= 0:
                raise ValueError("Price must be positive")
        except (TypeError, ValueError):
            raise ValueError("Invalid price format")
        
        query = "UPDATE products SET product_name = ?, price = ? WHERE product_id = ?"
        execute_query(query, (name.strip(), price_float, product_id))

    @staticmethod
    def delete_product(product_id):
        """Soft delete a product (mark as unavailable)."""
        execute_query("UPDATE products SET is_available = 0 WHERE product_id = ?", (product_id,))
        
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (None, 'DELETE_PRODUCT', 'products', product_id, "Product soft-deleted")
        )

    @staticmethod
    def hard_delete_product(product_id):
        """Permanently delete a product (admin only)."""
        execute_query("DELETE FROM order_items WHERE product_id = ?", (product_id,))
        execute_query("DELETE FROM products WHERE product_id = ?", (product_id,))

    @staticmethod
    def restore_product(product_id):
        """Restore a soft-deleted product."""
        execute_query("UPDATE products SET is_available = 1 WHERE product_id = ?", (product_id,))