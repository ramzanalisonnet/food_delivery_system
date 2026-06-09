from database.database import execute_query, fetch_all, fetch_one

class OrderService:
    @staticmethod
    def create_order(customer_id, merchant_id, total_price, address, due_time, items):
        """Creates an order record along with its constituent items."""
        order_query = """INSERT INTO orders (customer_id, merchant_id, total_price, delivery_address, due_time, status)
                         VALUES (?, ?, ?, ?, ?, 'Pending')"""
        cursor = execute_query(order_query, (customer_id, merchant_id, total_price, address, due_time))
        order_id = cursor.lastrowid
        
        items_query = "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)"
        for prod_id, qty in items.items():
            execute_query(items_query, (order_id, prod_id, qty))
        return order_id

    @staticmethod
    def get_customer_orders(customer_id):
        return fetch_all("SELECT * FROM orders WHERE customer_id = ? ORDER BY order_id DESC", (customer_id,))

    @staticmethod
    def get_merchant_orders(merchant_id):
        return fetch_all("SELECT * FROM orders WHERE merchant_id = ? ORDER BY order_id DESC", (merchant_id,))

    @staticmethod
    def get_all_orders():
        return fetch_all("SELECT * FROM orders ORDER BY order_id DESC")

    @staticmethod
    def update_order_status(order_id, status):
        execute_query("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))