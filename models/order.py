class Order:
    def __init__(self, order_id, customer_id, merchant_id, total_price, delivery_address, due_time, status='Pending'):
        self.order_id = order_id
        self.customer_id = customer_id
        self.merchant_id = merchant_id
        self.total_price = total_price
        self.delivery_address = delivery_address
        self.due_time = due_time
        self.status = status