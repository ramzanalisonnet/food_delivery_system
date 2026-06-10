from database.database import fetch_all, fetch_one, execute_query

class UserService:
    @staticmethod
    def get_all_users():
        """Get all users for admin management."""
        return fetch_all("""
            SELECT u.*, 
                   CASE WHEN c.courier_id IS NOT NULL THEN 1 ELSE 0 END as is_courier
            FROM users u 
            LEFT JOIN couriers c ON u.user_id = c.user_id 
            ORDER BY u.user_id
        """)

    @staticmethod
    def get_user_by_id(user_id):
        return fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))

    @staticmethod
    def update_user(user_id, username=None, role=None, is_active=None):
        """Update user details."""
        user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not user:
            return False, "User not found"
        
        updates = []
        params = []
        
        if username:
            # Check if username is taken by another user
            existing = fetch_one("SELECT user_id FROM users WHERE username = ? AND user_id != ?", (username, user_id))
            if existing:
                return False, "Username already taken"
            updates.append("username = ?")
            params.append(username)
        
        if role and role in ['Customer', 'Merchant', 'Courier', 'Administrator']:
            updates.append("role = ?")
            params.append(role)
            
            # Handle courier profile
            if role == 'Courier':
                existing_courier = fetch_one("SELECT * FROM couriers WHERE user_id = ?", (user_id,))
                if not existing_courier:
                    execute_query("INSERT INTO couriers (user_id) VALUES (?)", (user_id,))
            else:
                execute_query("DELETE FROM couriers WHERE user_id = ?", (user_id,))
        
        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)
        
        if updates:
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"
            execute_query(query, params)
            
            execute_query(
                "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
                (None, 'UPDATE_USER', 'users', user_id, f"Updated fields: {', '.join(updates)}")
            )
        
        return True, "User updated successfully"

    @staticmethod
    def delete_user(user_id):
        """Delete a user and all related records."""
        user = fetch_one("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if not user:
            return False, "User not found"
        
        # Delete related records
        execute_query("DELETE FROM couriers WHERE user_id = ?", (user_id,))
        execute_query("DELETE FROM deliveries WHERE courier_id = ?", (user_id,))
        execute_query("DELETE FROM order_items WHERE order_id IN (SELECT order_id FROM orders WHERE customer_id = ? OR merchant_id = ?)", (user_id, user_id))
        execute_query("DELETE FROM orders WHERE customer_id = ? OR merchant_id = ?", (user_id, user_id))
        execute_query("DELETE FROM products WHERE merchant_id = ?", (user_id,))
        execute_query("DELETE FROM audit_log WHERE user_id = ?", (user_id,))
        execute_query("DELETE FROM users WHERE user_id = ?", (user_id,))
        
        execute_query(
            "INSERT INTO audit_log (user_id, action, entity_type, entity_id, details) VALUES (?, ?, ?, ?, ?)",
            (None, 'DELETE_USER', 'users', user_id, f"User {user['username']} permanently deleted")
        )
        
        return True, "User deleted successfully"

    @staticmethod
    def get_user_statistics():
        """Get user statistics for admin dashboard."""
        stats = {}
        stats['total_users'] = fetch_one("SELECT COUNT(*) as cnt FROM users")['cnt']
        stats['active_users'] = fetch_one("SELECT COUNT(*) as cnt FROM users WHERE is_active = 1")['cnt']
        stats['customers'] = fetch_one("SELECT COUNT(*) as cnt FROM users WHERE role = 'Customer'")['cnt']
        stats['merchants'] = fetch_one("SELECT COUNT(*) as cnt FROM users WHERE role = 'Merchant'")['cnt']
        stats['couriers'] = fetch_one("SELECT COUNT(*) as cnt FROM users WHERE role = 'Courier'")['cnt']
        stats['admins'] = fetch_one("SELECT COUNT(*) as cnt FROM users WHERE role = 'Administrator'")['cnt']
        return stats

    @staticmethod
    def get_couriers():
        """Get all courier users with their availability status."""
        return fetch_all("""
            SELECT u.*, c.is_available, c.courier_id
            FROM users u 
            JOIN couriers c ON u.user_id = c.user_id 
            WHERE u.is_active = 1
            ORDER BY u.user_id
        """)

    @staticmethod
    def toggle_courier_availability(courier_id, is_available):
        """Toggle courier availability status."""
        execute_query("UPDATE couriers SET is_available = ? WHERE courier_id = ?", (1 if is_available else 0, courier_id))