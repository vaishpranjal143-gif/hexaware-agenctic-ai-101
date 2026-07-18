# A Future holds a result that becomes available later.
# It is a low-level construct that
# represents an eventual result of an asynchronous operation.

# A Future can be in one of three states: pending, done, or cancelled.

# You can create a Future using the event loop's create_future() method,
# and you can set its result using the set_result() method.

# When you await a Future,
# it will pause the execution of the coroutine until the Future is done,
# at which point it will return the result of the Future.

import asyncio

async def main1():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    future.set_result("Hello Future")
    result = await future
    print(result)
asyncio.run(main1())

# Output:
# Hello Future

# Real World: Amazon Delivery
# Problem
# The laptop has not arrived yet.
# But we know it will arrive.
# A Future represents that upcoming result.

import asyncio
async def deliver_laptop(future):
    print("Laptop dispatched")
    await asyncio.sleep(5)
    future.set_result("Laptop Delivered")

async def main():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    asyncio.create_task(
        deliver_laptop(future)
    )
    print("Waiting for delivery...")
    result = await future
    print(result)
asyncio.run(main())