# CONCEPT 7: METACLASSES
# A metaclass is a "class that creates classes".

# Object creates objects
# Class creates objects
# Metaclass creates classes

# Metaclass --> Class --> Object

class MyMeta(type):

    def __new__(cls, name, bases, attrs):
        print(f"Creating class: {name}")
        return super().__new__(cls, name, bases, attrs)

class Student(metaclass=MyMeta):
    pass

class Teacher(metaclass=MyMeta):
    pass