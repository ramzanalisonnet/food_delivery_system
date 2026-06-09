from database.database import fetch_all, execute_query

class ProductService:
    @staticmethod
    def get_all_products():
        return fetch_all("SELECT * FROM products")

    @staticmethod
    def add_product(name, price, merchant_id):
        query = "INSERT INTO products (product_name, price, merchant_id) VALUES (?, ?, ?)"
        execute_query(query, (name, float(price), merchant_id))

    @staticmethod
    def update_product(product_id, name, price):
        query = "UPDATE products SET product_name = ?, price = ? WHERE product_id = ?"
        execute_query(query, (name, float(price), product_id))

    @staticmethod
    def delete_product(product_id):
        execute_query("DELETE FROM products WHERE product_id = ?", (product_id,))