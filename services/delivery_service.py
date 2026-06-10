from database.database import fetch_all, fetch_one, execute_query
from datetime import datetime

class DeliveryService:
    @staticmethod
    def get_available_orders():
        return fetch_all("SELECT * FROM orders WHERE status = 'Ready for Pickup'")

    @staticmethod
    def assign_delivery(order_id, courier_id, route, est_time):
        execute_query("UPDATE orders SET status = 'Delivering' WHERE order_id = ?", (order_id,))
        execute_query(
            "INSERT INTO deliveries (order_id, courier_id, route, estimated_time, status) VALUES (?, ?, ?, ?, 'Assigned')",
            (order_id, courier_id, route, est_time)
        )
        execute_query("UPDATE couriers SET is_available = 0 WHERE user_id = ?", (courier_id,))

    @staticmethod
    def get_courier_active_deliveries(courier_id):
        query = """SELECT d.*, o.delivery_address, o.due_time FROM deliveries d 
                   JOIN orders o ON d.order_id = o.order_id 
                   WHERE d.courier_id = ? AND d.status != 'Delivered'"""
        return fetch_all(query, (courier_id,))

    @staticmethod
    def complete_delivery(delivery_id, order_id):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execute_query("UPDATE deliveries SET status = 'Delivered', completed_at = ? WHERE delivery_id = ?", (now, delivery_id))
        execute_query("UPDATE orders SET status = 'Delivered' WHERE order_id = ?", (order_id,))
        
        # Free up the courier
        delivery = fetch_one("SELECT courier_id FROM deliveries WHERE delivery_id = ?", (delivery_id,))
        if delivery:
            execute_query("UPDATE couriers SET is_available = 1 WHERE user_id = ?", (delivery['courier_id'],))

    @staticmethod
    def get_all_deliveries():
        """Get all deliveries for admin tracking."""
        return fetch_all("""
            SELECT d.*, o.delivery_address, o.due_time, u.username as courier_name
            FROM deliveries d 
            JOIN orders o ON d.order_id = o.order_id 
            LEFT JOIN users u ON d.courier_id = u.user_id
            ORDER BY d.delivery_id DESC
        """)