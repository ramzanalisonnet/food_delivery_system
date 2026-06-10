from database.database import execute_query, fetch_all, fetch_one
from datetime import datetime

class OrderService:
    @staticmethod
    def create_order(customer_id, merchant_id, total_price, address, due_time, items):
        """Creates an order record along with its constituent items."""
        # Validate inputs
        if not items or total_price <= 0:
            raise ValueError("Invalid order: must have items and positive total")
        
        if not address or address not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            raise ValueError("Invalid delivery address")
        
        order_query = """INSERT INTO orders (customer_id, merchant_id, total_price, delivery_address, due_time, status)
                         VALUES (?, ?, ?, ?, ?, 'Pending')"""
        cursor = execute_query(order_query, (customer_id, merchant_id, total_price, address, due_time))
        order_id = cursor.lastrowid
        
        items_query = "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)"
        for prod_id, qty in items.items():
            if qty > 0:
                execute_query(items_query, (order_id, prod_id, qty))
        
        # Log the action
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (customer_id, 'CREATE_ORDER', 'orders', order_id, f"Order created with {len(items)} items, total: ${total_price:.2f}")
        )
        
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
    def get_order_by_id(order_id):
        return fetch_one("SELECT * FROM orders WHERE order_id = ?", (order_id,))

    @staticmethod
    def update_order_status(order_id, status):
        valid_statuses = ['Pending', 'Preparing', 'Ready for Pickup', 'Delivering', 'Delivered', 'Cancelled']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        execute_query("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        
        # If cancelled, update delivery if exists
        if status == 'Cancelled':
            execute_query(
                "UPDATE deliveries SET status = 'Failed' WHERE order_id = ? AND status != 'Delivered'",
                (order_id,)
            )

    @staticmethod
    def cancel_order(order_id, customer_id=None):
        """Cancel an order if it's still in Pending or Preparing state."""
        order = fetch_one("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        if not order:
            return False, "Order not found"
        
        if customer_id and order['customer_id'] != customer_id:
            return False, "Unauthorized to cancel this order"
        
        if order['status'] in ['Delivering', 'Delivered', 'Cancelled']:
            return False, f"Cannot cancel order in '{order['status']}' status"
        
        execute_query("UPDATE orders SET status = 'Cancelled' WHERE order_id = ?", (order_id,))
        execute_query(
            "UPDATE deliveries SET status = 'Failed' WHERE order_id = ? AND status != 'Delivered'",
            (order_id,)
        )
        
        # Log the action
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (customer_id, 'CANCEL_ORDER', 'orders', order_id, f"Order cancelled from status: {order['status']}")
        )
        
        return True, "Order cancelled successfully"

    @staticmethod
    def delete_order(order_id):
        """Admin function to completely remove an order."""
        # Delete related records first due to foreign keys
        execute_query("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        execute_query("DELETE FROM deliveries WHERE order_id = ?", (order_id,))
        execute_query("DELETE FROM orders WHERE order_id = ?", (order_id,))
        
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (None, 'DELETE_ORDER', 'orders', order_id, "Order permanently deleted by admin")
        )

    @staticmethod
    def get_order_items(order_id):
        """Get all items for a specific order with product details."""
        query = """
            SELECT oi.*, p.product_name, p.price 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.product_id 
            WHERE oi.order_id = ?
        """
        return fetch_all(query, (order_id,))