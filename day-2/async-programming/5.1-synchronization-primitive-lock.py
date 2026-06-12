import asyncio

lock = asyncio.Lock()

async def worker(name):

    async with lock:

        print(f"{name} entered")

        await asyncio.sleep(2)

        print(f"{name} leaving")

async def main1():

    await asyncio.gather(
        worker("A"),
        worker("B")
    )

asyncio.run(main1())

# Output:
# A entered
# waits for 2 seconds
# A leaving
# B entered
# waits for 2 seconds
# B leaving

# In this example,
# we have a lock that ensures that
# only one worker can enter the critical section at a time.
# When worker A acquires the lock,
# worker B has to wait until A releases it before

print("-" * 20)

# Real World: ATM Machine
# Problem
# Only one person can use the ATM at a time.

import asyncio

atm = asyncio.Lock()

async def withdraw(name):
    print(f"{name} arrived")
    async with atm:
        print(f"{name} using ATM")
        await asyncio.sleep(10) # "I am busy waiting for 10 seconds, but feel free to let other people arrive or do other background work while I wait."
        print(f"{name} finished")

async def main():
    await asyncio.gather(
        withdraw("Abhishek"),
        withdraw("Travis"),
        withdraw("Klassan")
    )

asyncio.run(main())