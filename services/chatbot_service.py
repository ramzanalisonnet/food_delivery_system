import re

class ChatbotService:
    def __init__(self):
        # Predefined rule dictionary
        self.rules = {
            r'.*(where|status).*order.*': "Your order is currently being processed and routed according to topological efficiency variables.",
            r'.*how long|time|eta.*': "The standard delivery window targets between 15 to 30 minutes, based on dispatch distances.",
            r'.*cancel.*order.*': "Orders can be canceled only if the merchant has not yet updated the state to 'Preparing'.",
            r'.*refund.*': "Refund evaluations are escalated directly to system administrators for review.",
            r'.*(hello|hi|hey).*': "Greetings! How can I assist you with your system order tracking today?"
        }

    def process_message(self, message):
        msg_lower = message.lower()
        for pattern, response in self.rules.items():
            if re.match(pattern, msg_lower):
                return response
        return "I apologize, but I didn't quite catch that. Could you please rephrase your request regarding order tracking, times, or refund processes?"