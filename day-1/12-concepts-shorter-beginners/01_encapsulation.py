# CONCEPT 1: ENCAPSULATION
# Hiding secret data inside a class so nobody can touch it directly.
# Think of it like a safe — you can use it, but you can't see the PIN.

class ChatBot:
    def __init__(self, name, secret_pin):
        self.name        = name           # public  — anyone can read this
        self.__pin       = secret_pin     # private — hidden! __ means secret

    def greet(self):
        return f"Hi! I am {self.name}. How can I help you today?"

    def unlock(self, guess):
        if guess == self.__pin:
            return "Access granted! Welcome."
        return "Wrong PIN. Access denied!"

bot = ChatBot("Aria", "1234")
print(bot.greet())
print(bot.unlock("0000"))       # wrong PIN
print(bot.unlock("1234"))       # correct PIN
print(bot.name)                 # public — works fine

try:
    print(bot.__pin)            # private — this will FAIL
except AttributeError:
    print("Cannot read the secret PIN from outside!")
