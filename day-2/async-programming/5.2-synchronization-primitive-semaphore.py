import asyncio

semaphore = asyncio.Semaphore(2)
async def worker(name):
    async with semaphore:
        print(f"{name} running")
        await asyncio.sleep(2)
        print(f"{name} finished")

async def main1():
    await asyncio.gather(
        worker("A"),
        worker("B"),
        worker("C"),
        worker("D")
    )
asyncio.run(main1())

# Output:
# A running
# B running
# C running
# D running
# waits for 2 seconds
# A finished
# B finished
# waits for 2 seconds
# C finished
# D finished

# Only 2 tasks run simultaneously.
# When A and B finish, C and D start running.

print("-" * 20)

# Real World: Parking Lot
# Problem
# Parking lot has 2 slots.
# Only 2 cars can enter.

import asyncio

parking_lot = asyncio.Semaphore(4)
async def park(car):
    print(f"{car} arrived")
    async with parking_lot:
        print(f"{car} parked")
        await asyncio.sleep(10)
        print(f"{car} leaving")
async def main():
    await asyncio.gather(
        park("Car A"),
        park("Car B"),
        park("Car C"),
        park("Car D")
    )
asyncio.run(main())