import asyncio

event = asyncio.Event()

async def waiter():
    print("Waiting for signal")
    await event.wait()
    print("Signal received")

async def sender():
    await asyncio.sleep(3)
    print("Sending signal")
    event.set()

async def main1():
    await asyncio.gather(
        waiter(),
        sender()
    )

asyncio.run(main1())

# Output:
# Waiting for signal
# Sending signal
# Signal received

print("-" * 20)

# Real World: School Bell
# Problem
# Students cannot go to lunch until the bell rings.

import asyncio

school_bell = asyncio.Event()

async def student(name):
    print(f"{name} waiting")
    await school_bell.wait() 
    print(f"{name} going for lunch")

async def principal():
    print("Class in progress")
    await asyncio.sleep(5)
    print("Bell rang")
    school_bell.set()

async def main():
    await asyncio.gather(
        student("Suryavanshi"),
        student("Jaiswal"),
        student("Butler"),
        principal()
    )
asyncio.run(main())