class ChatBot:

    def __init__(self, name):
        self.name = name
        self.history = []

    def respond(self, message):

        self.history.append(message)

        if "hello" in message.lower():
            return "Hi there!"

        return "Interesting..."


bot = ChatBot("Caramel")

print(bot.respond("hello"))
print(bot.respond("how are you?"))
print(bot.respond("bye"))
print(bot.history)