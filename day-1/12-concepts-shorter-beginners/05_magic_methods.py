# CONCEPT 5: MAGIC METHODS (Dunder Methods)
# Special methods that make your class work with Python's built-in syntax.
# Think: a to-do list that works just like a normal Python list.

class TaskList:
    def __init__(self, owner):
        print("Creating a task list for", owner)
        self.owner  = owner
        self._tasks = []

    def add(self, task):
        self._tasks.append(task)

    def __len__(self):           return len(self._tasks)        # len(my_list)
    def __contains__(self, t):   return t in self._tasks        # "task" in my_list
    def __getitem__(self, i):    return self._tasks[i]          # my_list[0]
    def __repr__(self):          return f"TaskList({self.owner}, {len(self)} tasks)"
    def __iter__(self):          return iter(self._tasks)       # for t in my_list

my_tasks = TaskList("Aria")
my_tasks.add("Search the web")
my_tasks.add("Write a report")
my_tasks.add("Send an email")

print(my_tasks)                                   # __repr__
print("Total tasks:", len(my_tasks))              # __len__
print("Has report?", "Write a report" in my_tasks) # __contains__
print("First task:", my_tasks[0])                 # __getitem__

for task in my_tasks:                             # __iter__
    print("  →", task)