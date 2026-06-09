import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import get_connection

def initialize_database():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Customer', 'Merchant', 'Courier', 'Administrator'))
            )
        ''')
        
        # 2. Products Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                merchant_id INTEGER,
                FOREIGN KEY(merchant_id) REFERENCES users(user_id)
            )
        ''')
        
        # 3. Orders Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                merchant_id INTEGER,
                total_price REAL NOT NULL,
                delivery_address TEXT NOT NULL,
                due_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                FOREIGN KEY(customer_id) REFERENCES users(user_id),
                FOREIGN KEY(merchant_id) REFERENCES users(user_id)
            )
        ''')
        
        # 4. Order Items Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
        ''')
        
        # 5. Couriers Extension Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS couriers (
                courier_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                FOREIGN KEY(user_id) REFERENCES users(user_id)
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
                status TEXT DEFAULT 'Assigned',
                FOREIGN KEY(order_id) REFERENCES orders(order_id),
                FOREIGN KEY(courier_id) REFERENCES users(user_id)
            )
        ''')
        
        # 7. Simulated Travel Times Graph Structure Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS travel_times (
                from_location TEXT NOT NULL,
                to_location TEXT NOT NULL,
                travel_time INTEGER NOT NULL,
                PRIMARY KEY (from_location, to_location)
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
                ('admin1', 'pass123', 'Administrator')
            ]
            cursor.executemany("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", default_users)
            
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
            cursor.executemany("INSERT INTO products (product_name, price, merchant_id) VALUES (?, ?, ?)", default_products)
            
            # Seed Topological Map Metrics
            # Map Structure: Restaurant 'R', Delivery points 'A' through 'H'
            default_matrix = [
                ('R', 'A', 10), ('R', 'B', 15), ('R', 'C', 22), ('R', 'D', 30),
                ('A', 'B', 5), ('A', 'C', 12), ('B', 'C', 8), ('C', 'D', 10),
                ('D', 'E', 7), ('E', 'F', 6), ('F', 'G', 9), ('G', 'H', 4),
                ('R', 'E', 25), ('A', 'E', 18), ('B', 'F', 14), ('C', 'G', 11),
                ('D', 'H', 15), ('H', 'A', 28)
            ]
            
            # Make map bidirectional across structural layout
            bidirectional_matrix = []
            for u, v, w in default_matrix:
                bidirectional_matrix.append((u, v, w))
                bidirectional_matrix.append((v, u, w))
                
            cursor.executemany("INSERT OR IGNORE INTO travel_times (from_location, to_location, travel_time) VALUES (?, ?, ?)", bidirectional_matrix)
            
            conn.commit()
            print("[✔] Mock evaluation records successfully added.")

if __name__ == '__main__':
    initialize_database()