import re
from services.order_service import OrderService

class ChatbotService:
    def __init__(self, user_id=None):
        self.user_id = user_id
        self.rules = [
            # Order status queries
            (r'.*\b(where|status|track|tracking)\b.*\border\b.*', self._handle_order_status),
            (r'.*\border\b.*\b(where|status|track|tracking)\b.*', self._handle_order_status),
            
            # Time/ETA queries
            (r'.*\b(how long|time|eta|estimate|arrive|delivery)\b.*', self._handle_eta),
            
            # Cancel order
            (r'.*\bcancel\b.*\border\b.*', self._handle_cancel),
            
            # Refund queries
            (r'.*\brefund\b.*', self._handle_refund),
            
            # Price/menu queries
            (r'.*\b(price|cost|menu|how much)\b.*', self._handle_pricing),
            
            # Greetings
            (r'.*\b(hello|hi|hey|good morning|good evening)\b.*', self._handle_greeting),
            
            # Help
            (r'.*\b(help|what can you do|commands)\b.*', self._handle_help),
            
            # Thank you
            (r'.*\b(thanks|thank you|thx)\b.*', self._handle_thanks),
        ]

    def _handle_order_status(self, message):
        if self.user_id:
            orders = OrderService.get_customer_orders(self.user_id)
            if orders:
                latest = orders[0]
                return f"Your latest order (#{latest['order_id']}) is currently '{latest['status']}'. It will be delivered to Node {latest['delivery_address']} by {latest['due_time']}."
        return "Your order is currently being processed and routed according to topological efficiency variables."

    def _handle_eta(self, message):
        return "The standard delivery window targets between 15 to 30 minutes, based on dispatch distances from the restaurant to your delivery node."

    def _handle_cancel(self, message):
        if self.user_id:
            orders = OrderService.get_customer_orders(self.user_id)
            pending_orders = [o for o in orders if o['status'] in ['Pending', 'Preparing']]
            if pending_orders:
                order_ids = ', '.join([f"#{o['order_id']}" for o in pending_orders])
                return f"You have cancellable orders: {order_ids}. To cancel, please use the main dashboard or contact support. Orders in 'Preparing' state may be cancelled, but once 'Ready for Pickup', cancellation is not available."
        return "Orders can be canceled only if the merchant has not yet updated the state to 'Preparing' or 'Ready for Pickup'."

    def _handle_refund(self, message):
        return "Refund evaluations are escalated directly to system administrators for review. Please provide your order ID and reason for refund, and an admin will process your request within 24 hours."

    def _handle_pricing(self, message):
        return "Our menu items range from $3.75 to $14.20. You can browse the full menu on your dashboard. All prices include delivery routing optimization!"

    def _handle_greeting(self, message):
        return "Greetings! How can I assist you with your system order tracking today? You can ask about order status, delivery times, cancellations, or refunds."

    def _handle_help(self, message):
        return (
            "🤖 I can help you with:\n"
            "• Order status tracking\n"
            "• Delivery time estimates\n"
            "• Order cancellation requests\n"
            "• Refund inquiries\n"
            "• Menu and pricing information\n\n"
            "Just type your question and I'll assist you!"
        )

    def _handle_thanks(self, message):
        return "You're welcome! Is there anything else I can help you with?"

    def process_message(self, message):
        """Process user message and return appropriate response."""
        msg_lower = message.lower().strip()
        
        for pattern, handler in self.rules:
            if re.search(pattern, msg_lower):
                if callable(handler):
                    return handler(msg_lower)
                return handler
        
        return "I apologize, but I didn't quite catch that. Could you please rephrase your request? You can ask about order tracking, delivery times, cancellations, refunds, or type 'help' for available commands."