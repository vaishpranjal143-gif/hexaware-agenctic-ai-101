# CONCEPT 2: INHERITANCE
# A child class gets everything the parent has — and can add more.
# Think: every Bot has a name and can greet. ChatBot and SearchBot just add extra skills.

class Bot:                               # parent class — shared by everyone
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hi, I am {self.name}!"

class ChatBot(Bot):                      # child — gets greet() for free, adds chat()
    def chat(self, message):
        return f"{self.name} heard you say: '{message}'"

class SearchBot(Bot):                    # child — gets greet() for free, adds search()
    def search(self, topic):
        return f"{self.name} found results for: '{topic}'"

aria = ChatBot("Aria")
rex  = SearchBot("Rex")

print(aria.greet())                      # inherited from Bot — no need to rewrite
print(aria.chat("What is AI?"))          # ChatBot's own method

print(rex.greet())                       # inherited from Bot — works automatically
print(rex.search("machine learning"))    # SearchBot's own method
