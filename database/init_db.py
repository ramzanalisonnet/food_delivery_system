import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_connection

def initialize_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # 1. Users Table (with password hashing support)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Customer', 'Merchant', 'Courier', 'Administrator')),
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Products Table (with soft delete support)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL CHECK(price > 0),
                merchant_id INTEGER,
                is_available INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(merchant_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        ''')
        
        # 3. Orders Table (with cancellation support)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                merchant_id INTEGER,
                total_price REAL NOT NULL CHECK(total_price >= 0),
                delivery_address TEXT NOT NULL,
                due_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending' 
                    CHECK(status IN ('Pending', 'Preparing', 'Ready for Pickup', 'Delivering', 'Delivered', 'Cancelled')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES users(user_id) ON DELETE SET NULL,
                FOREIGN KEY(merchant_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        ''')
        
        # 4. Order Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(product_id) ON DELETE SET NULL
            )
        ''')
        
        # 5. Couriers Extension Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS couriers (
                courier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                is_available INTEGER DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # 6. Deliveries Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliveries (
                delivery_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                courier_id INTEGER,
                route TEXT,
                estimated_time INTEGER,
                status TEXT DEFAULT 'Assigned' 
                    CHECK(status IN ('Assigned', 'In Transit', 'Delivered', 'Failed')),
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE SET NULL,
                FOREIGN KEY(courier_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        ''')
        
        # 7. Simulated Travel Times Graph Structure Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS travel_times (
                from_location TEXT NOT NULL,
                to_location TEXT NOT NULL,
                travel_time INTEGER NOT NULL CHECK(travel_time > 0),
                PRIMARY KEY (from_location, to_location)
            )
        ''')
        
        # 8. System Audit Log Table (for admin tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
            )
        ''')
        
        conn.commit()
        print("[✔] Database schema instantiated successfully.")
        
        # Seed Basic User Records securely if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_users = [
                ('cust1', 'pass123', 'Customer'),
                ('merch1', 'pass123', 'Merchant'),
                ('cour1', 'pass123', 'Courier'),
                ('admin1', 'admin123', 'Administrator')
            ]
            cursor.executemany(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                default_users
            )
            
            # Link Courier Profile
            cursor.execute("SELECT user_id FROM users WHERE username='cour1'")
            c_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO couriers (user_id) VALUES (?)", (c_id,))
            
            # Seed Merchant Menu Items
            cursor.execute("SELECT user_id FROM users WHERE username='merch1'")
            m_id = cursor.fetchone()[0]
            default_products = [
                ('University Burger Duo', 12.99, m_id),
                ('Campus Vegan Rice Bowl', 9.50, m_id),
                ('Data Structures Espresso', 3.75, m_id),
                ('Binary Tree Cheese Pizza', 14.20, m_id)
            ]
            cursor.executemany(
                "INSERT INTO products (product_name, price, merchant_id) VALUES (?, ?, ?)", 
                default_products
            )
            
            # Seed Topological Map Metrics
            default_matrix = [
                ('R', 'A', 10), ('R', 'B', 15), ('R', 'C', 22), ('R', 'D', 30),
                ('A', 'B', 5), ('A', 'C', 12), ('B', 'C', 8), ('C', 'D', 10),
                ('D', 'E', 7), ('E', 'F', 6), ('F', 'G', 9), ('G', 'H', 4),
                ('R', 'E', 25), ('A', 'E', 18), ('B', 'F', 14), ('C', 'G', 11),
                ('D', 'H', 15), ('H', 'A', 28)
            ]
            
            # Make map bidirectional
            bidirectional_matrix = []
            for u, v, w in default_matrix:
                bidirectional_matrix.append((u, v, w))
                bidirectional_matrix.append((v, u, w))
                
            cursor.executemany(
                "INSERT OR IGNORE INTO travel_times (from_location, to_location, travel_time) VALUES (?, ?, ?)", 
                bidirectional_matrix
            )
            
            conn.commit()
            print("[✔] Mock evaluation records successfully added.")

if __name__ == '__main__':
    initialize_database()