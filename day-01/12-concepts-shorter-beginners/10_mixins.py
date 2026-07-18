# CONCEPT 10: MIXINS
# A Mixin is a small class that adds one extra ability.

class CanTalk:

    def talk(self):
        print("Hello!")

class Robot(CanTalk):
    pass

bot = Robot()

bot.talk()

# Robot does not have a talk() method.

# Inheritance = IS-A relationship
# Dog IS AN Animal

# Mixin = CAN-DO relationship
# Robot CAN TALK
# Robot CAN DANCE
# Robot CAN LOG

# Polymorphism = SAME METHOD, DIFFERENT BEHAVIOR
# dog.speak() → Bark
# cat.speak() → Meow

# 1. Inheritance → "What are you?"
# Example: Dog is an Animal
class Animal:
    def eat(self):
        print("Eating...")

class Dog1(Animal):
    pass

dog = Dog1()
dog.eat()

# 2. Mixin → "What can you do?"
# Example: Robot can talk, dance, and log.
class CanTalk1:
    def talk(self):
        print("Hello!")

class Robot1(CanTalk):
    pass

bot = Robot()
bot.talk()

# Robot is NOT a CanTalk.
# Robot HAS the ability to talk.

# 3. Polymorphism → "Same method, different behavior"
# Example: Different animals speak differently
class Dog:
    def speak(self):
        print("Bark")

class Cat:
    def speak(self):
        print("Meow")

animals = [Dog(), Cat()]

for animal in animals:
    animal.speak()