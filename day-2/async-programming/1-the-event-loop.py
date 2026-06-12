# The Event Loop is a core part of asynchronous programming in Python.
# It allows you to run multiple tasks concurrently without blocking the main thread.
# The `asyncio` library provides an event loop that can manage and schedule asynchronous tasks.

import asyncio

async def greet():
    print("Hello from Event Loop")

# Event Loop is created and started here
asyncio.run(greet())

# Output:
# Hello from Event Loop

# The Event Loop is like a restaurant manager
# who keeps checking which table needs attention.
import asyncio

async def customer(name):
    print(f"\n{name} entered restaurant")
    await asyncio.sleep(10)
    print(f"\n{name} received food")

async def main():
    await asyncio.gather(
        customer("Venkatesh"),
        customer("Virat"),
        customer("Rajat")
    )

print("\nRestaurant Opened")
asyncio.run(main())
print("\nRestaurant Closed")