# CONCEPT 12: __slots__
# Every Python object has a __dict__ (like a backpack) — flexible but heavy.
# __slots__ replaces it with fixed pockets — lighter and faster.
# Use when you create millions of small objects and memory matters.

class Student:
    __slots__ = ("name", "age")
    def __init__(self, name, age):
        self.name = name
        self.age = age

student = Student("John", 20)
student.name = "Alice"     # Allowed
# student.grade = "A"        # Not Allowed

# output: AttributeError: 'Student' object has no attribute 'grade'

# __slots__ restricts an object to a fixed set of attributes, preventing new attributes from being added later.


# Most Python developers never write __slots__.
# Use it only when memory optimization becomes important.
# "This object is only allowed to have the attributes listed in __slots__."
