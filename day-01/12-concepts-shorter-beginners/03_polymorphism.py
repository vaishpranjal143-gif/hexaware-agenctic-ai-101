# CONCEPT 3: POLYMORPHISM
# Same method name, but each class does it differently.
# Think: you say "speak" to a dog and a cat — they respond differently.

class WeatherBot:
    def respond(self, question):
        return f"Weather answer: It will be sunny today!"

class JokeBot:
    def respond(self, question):
        return f"Joke answer: Why did the AI go to school? To get smarter!"

class TranslateBot:
    def respond(self, question):
        return f"Translation: '{question}' means 'Bonjour' in French!"

def ask(bot, question):                  # works with ANY bot — no if/elif needed
    return bot.respond(question)

bots = [WeatherBot(), JokeBot(), TranslateBot()]

for bot in bots:
    print(ask(bot, "Hello"))             # same call → each bot answers differently
