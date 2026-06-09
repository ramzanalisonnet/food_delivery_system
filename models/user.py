class User:
    def __init__(self, user_id, username, role):
        self.user_id = user_id
        self.username = username
        self.role = role

class Customer(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'Customer')

class Merchant(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'Merchant')

class Courier(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'Courier')

class Admin(User):
    def __init__(self, user_id, username):
        super().__init__(user_id, username, 'Administrator')