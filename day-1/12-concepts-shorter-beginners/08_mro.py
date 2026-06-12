# CONCEPT 8: MRO — Method Resolution Order
# When a class has multiple parents, Python checks them left to right.
# Print __mro__ to see exactly which class Python will use first.

class CanTalk:
    def greet(self): return "Hello! I can talk."

class CanSee:
    def greet(self): return "Hello! I can see."

class CanHear:
    def greet(self): return "Hello! I can hear."

class SuperBot(CanTalk, CanSee, CanHear):   # inherits from all three
    def talk(self):  return CanTalk.greet(self)   # call each parent directly
    def see(self):   return CanSee.greet(self)
    def hear(self):  return CanHear.greet(self)

bot = SuperBot()

print("Python checks classes in this order (MRO):")
for i, cls in enumerate(SuperBot.__mro__):
    print(f"  {i+1}. {cls.__name__}")

print()
print("Default greet() — Python picks the FIRST one in MRO:")
print(bot.greet())                            # CanTalk wins — it is listed first

print()
print("Calling each parent directly:")
print(bot.talk())
print(bot.see())
print(bot.hear())
