# Coroutines are a special type of function
# that can pause and resume their execution.
# A coroutine is simply a function defined using:
# async def instead of def.

import asyncio

async def greet():
    print("Start")

    await asyncio.sleep(2)

    print("End\n")

asyncio.run(greet())

# The main difference is that await asyncio.sleep(2) is non-blocking,
# which pauses only the current task and lets other asynchronous tasks run,
# whereas time.sleep(2) is blocking,
# freezing your entire program and stopping everything else from executing.

# Output:
# Start
# waits for 2 seconds
# End

import time

start_time = time.perf_counter()

def make_tea1():
    print("Tea: Boiling water")
    time.sleep(10)
    print("Tea: Ready")

def make_toast1():
    print("Toast: Toasting bread")
    time.sleep(6)
    print("Toast: Ready")

def boil_eggs1():
    print("Eggs: Boiling")
    time.sleep(14)
    print("Eggs: Ready")

make_tea1()
make_toast1()
boil_eggs1()

end_time = time.perf_counter()

print(f"Breakfast Ready in {end_time - start_time:.2f} seconds\n")

# Output:
# Tea: Boiling water
# Toast: Toasting bread
# Eggs: Boiling
# Breakfast Ready
# waits for 5 seconds
# Tea: Ready
# waits for 3 seconds
# Toast: Ready
# waits for 7 seconds
# Eggs: Ready

import asyncio
import time

async def make_tea():
    print("Tea: Boiling water")
    await asyncio.sleep(5)
    print("Tea: Ready")

async def make_toast():
    print("Toast: Toasting bread")
    await asyncio.sleep(3)
    print("Toast: Ready")

async def boil_eggs():
    print("Eggs: Boiling")
    await asyncio.sleep(7)
    print("Eggs: Ready")

async def main():
    start_time = time.perf_counter()
    await asyncio.gather(
        make_tea(),
        make_toast(),
        boil_eggs()
    )
    end_time = time.perf_counter()
    print(f"Breakfast Ready in {end_time - start_time:.2f} seconds")

asyncio.run(main())