class ChatBot:

    def __init__(self, name):
        self.name = name

    def respond(self, message):

        if "hello" in message.lower():
            return "Hi there!"

        elif "bye" in message.lower():
            return "Goodbye!"

        return "I don't understand."


bot = ChatBot("Caramel")

print(bot.respond("hello"))
print(bot.respond("how are you?"))
print(bot.respond("bye"))