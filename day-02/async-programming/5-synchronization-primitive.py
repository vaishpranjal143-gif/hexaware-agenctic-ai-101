import asyncio

lock = asyncio.Lock()
semaphore = asyncio.Semaphore(2)
event = asyncio.Event()

print(type(lock))
print(type(semaphore))
print(type(event))

# Output:
# <class '_asyncio.Lock'>
# <class '_asyncio.Semaphore'>
# <class '_asyncio.Event'>

# Real World: Traffic Control System
# Problem
# Multiple vehicles use the same road.
# Need rules.

import asyncio

lock = asyncio.Lock()
semaphore = asyncio.Semaphore(2)
event = asyncio.Event()

print("Traffic control tools created")