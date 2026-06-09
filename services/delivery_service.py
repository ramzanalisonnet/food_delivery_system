from database.database import fetch_all, execute_query

class DeliveryService:
    @staticmethod
    def get_available_orders():
        return fetch_all("SELECT * FROM orders WHERE status = 'Ready for Pickup'")

    @staticmethod
    def assign_delivery(order_id, courier_id, route, est_time):
        execute_query("UPDATE orders SET status = 'Delivering' WHERE order_id = ?", (order_id,))
        query = "INSERT INTO deliveries (order_id, courier_id, route, estimated_time, status) VALUES (?, ?, ?, ?, 'Assigned')"
        execute_query(query, (order_id, courier_id, route, est_time))

    @staticmethod
    def get_courier_active_deliveries(courier_id):
        query = """SELECT d.*, o.delivery_address, o.due_time FROM deliveries d 
                   JOIN orders o ON d.order_id = o.order_id 
                   WHERE d.courier_id = ? AND d.status != 'Delivered'"""
        return fetch_all(query, (courier_id,))

    @staticmethod
    def complete_delivery(delivery_id, order_id):
        execute_query("UPDATE deliveries SET status = 'Delivered' WHERE delivery_id = ?", (delivery_id,))
        execute_query("UPDATE orders SET status = 'Delivered' WHERE order_id = ?", (order_id,))