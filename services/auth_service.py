from database.database import fetch_one, execute_query

class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        user_row = fetch_one(query, (username, password))
        return user_row

    @staticmethod
    def register_user(username, password, role):
        if not username or not password or not role:
            return False, "All evaluation input blocks must be populated."
        
        try:
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            execute_query(query, (username, password, role))
            return True, "User created successfully."
        except Exception:
            return False, "Operation error. Username may already exist."