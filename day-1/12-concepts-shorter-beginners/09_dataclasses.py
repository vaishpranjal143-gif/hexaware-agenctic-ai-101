# CONCEPT 9: DATACLASSES
# @dataclass writes __init__, __repr__, and __eq__ for you automatically.
# Use field(default_factory=list) for lists — never write = [] as a default!

from dataclasses import dataclass

@dataclass
class Student:
    name: str
    age: int

john = Student("John", 20)

print(john)

#example 2

from dataclasses import dataclass

@dataclass
class Employee:
    name: str
    salary: int

emp = Employee("Alice", 50000)

print(emp)

# Without @dataclass:
#     We write __init__()

# With @dataclass:
#     Python writes __init__() for us.