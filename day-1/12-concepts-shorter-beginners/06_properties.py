# CONCEPT 6: PROPERTIES
# @property turns a method into an attribute — looks like data, works like a method.
# @setter lets you check a value BEFORE saving — like a security guard at the door.

# Step 1: Why Do We Need Properties?
# Without properties:

class Student1:
    def __init__(self):
        self.age = 18

student = Student1()
student.age = -50
print(student.age)

# output: -50 (which doesn't make sense for an age!)

# Step 2: Using @property to Fix It
# With properties:
class Student:
    def __init__(self):
        self._age = 18  # Use _age to store the value internally

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value < 0:
            print("Age cannot be negative! Keeping the old value.")
        else:
            self._age = value

student = Student()
student.age = -50  # This will trigger the setter and print a warning
print(student.age)  # Output: 18