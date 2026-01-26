"""
Bot service for generating replies to user messages.
"""
import logging
from ..models import Conversation, Message

logger = logging.getLogger(__name__)


class BotService:
    """Base bot service interface"""
    
    def generate_reply(self, conversation: Conversation, last_user_message: Message) -> str:
        """Generate a reply to the user's message"""
        raise NotImplementedError


class EchoBotService(BotService):
    """Default echo bot that responds with simple rules"""
    
    def generate_reply(self, conversation: Conversation, last_user_message: Message) -> str:
        """Generate a simple echo response with engagement rules"""
        user_text = last_user_message.text.lower()
        
        # Simple rule-based responses
        if any(word in user_text for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! 👋 I'm here to help you with your CRM needs. How can I assist you today?"
        
        elif any(word in user_text for word in ['help', 'support', 'assistance']):
            return "I can help you with:\n• Finding products and services\n• Processing orders\n• Managing deliveries\n• Answering questions about our CRM\n\nWhat would you like to know?"
        
        elif any(word in user_text for word in ['order', 'purchase', 'buy']):
            return "I can help you with orders! You can:\n• Browse our product catalog\n• Check order status\n• Process new orders\n• Track deliveries\n\nWould you like to start with browsing products?"
        
        elif any(word in user_text for word in ['delivery', 'shipping', 'track']):
            return "For delivery assistance, I can help you:\n• Track existing orders\n• Schedule deliveries\n• Update delivery information\n• Check delivery status\n\nDo you have an order number to track?"
        
        elif any(word in user_text for word in ['product', 'catalog', 'items']):
            return "I can help you explore our product catalog! You can:\n• Search for specific products\n• Browse by category\n• Check availability\n• Get product details\n\nWhat type of product are you looking for?"
        
        elif any(word in user_text for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! 😊 I'm here whenever you need assistance. Is there anything else I can help you with?"
        
        elif any(word in user_text for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! 👋 Feel free to reach out anytime you need help. Have a great day!"
        
        else:
            # Default response for unrecognized input
            return f"I understand you're asking about: '{last_user_message.text}'\n\nI'm here to help with your CRM needs. You can ask me about:\n• Products and orders\n• Delivery tracking\n• Account information\n• General support\n\nHow can I assist you?"


def generate_reply(conversation: Conversation, last_user_message: Message) -> str:
    """Generate a reply for the given conversation and message"""
    bot_service = EchoBotService()
    return bot_service.generate_reply(conversation, last_user_message)
