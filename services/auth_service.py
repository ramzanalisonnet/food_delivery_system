from database.database import fetch_one, execute_query
import hashlib

class AuthService:
    @staticmethod
    def _hash_password(password):
        """Hash password using SHA-256 (consider bcrypt for production)."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user with username and password."""
        # For backward compatibility with plain text passwords in seed data
        query = "SELECT * FROM users WHERE username = ? AND (password = ? OR password = ?)"
        hashed_pw = AuthService._hash_password(password)
        user_row = fetch_one(query, (username, password, hashed_pw))
        return user_row

    @staticmethod
    def register_user(username, password, role):
        """Register a new user."""
        if not username or not password or not role:
            return False, "All evaluation input blocks must be populated."
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        
        if role not in ['Customer', 'Merchant', 'Courier', 'Administrator']:
            return False, "Invalid role specified."
        
        try:
            # Check if username exists
            existing = fetch_one("SELECT user_id FROM users WHERE username = ?", (username,))
            if existing:
                return False, "Username already exists."
            
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            cursor = execute_query(query, (username, password, role))
            
            # Create courier profile if needed
            if role == 'Courier':
                user_id = cursor.lastrowid
                execute_query("INSERT INTO couriers (user_id) VALUES (?)", (user_id,))
            
            return True, "User created successfully."
        except Exception as e:
            return False, f"Operation error: {str(e)}"