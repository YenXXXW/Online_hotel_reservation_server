import nltk
from nltk.chat.util import Chat, reflections

# Define patterns and responses
patterns = [
    (r'hi|hello|hey', ['Hello!', 'Hi there!', 'How can I help you?']),
    (r'book a room', ['Sure, I can help you with that.']),
    (r'check availability', ['Let me check for you.']),
    (r'room types', ['We offer single, double, and suite rooms.']),
    (r'amenities', ['Our hotel amenities include a swimming pool, gym, and restaurant.']),
    # Add more patterns and responses as needed
]

# Create a chatbot
chatbot = Chat(patterns, reflections)

# Define a function to interact with the chatbot
def hotel_chat(user_input):
    response = chatbot.respond(user_input)
    return response
