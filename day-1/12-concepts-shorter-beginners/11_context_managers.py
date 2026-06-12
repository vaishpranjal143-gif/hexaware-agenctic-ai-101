# CONCEPT 11: CONTEXT MANAGERS
# __enter__ runs when you enter a "with" block.
# __exit__  ALWAYS runs when you leave — even if something goes wrong.
# Think: an automatic door that always closes behind you.

class Room:
    def __enter__(self):
        print("Entering the room")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Leaving the room")

with Room():
    print("Inside the room")

# Entering the room
# Inside the room
# Leaving the room

# with Room():
#       ↓
# __enter__()

#       ↓
# Inside the block

#       ↓
# __exit__()