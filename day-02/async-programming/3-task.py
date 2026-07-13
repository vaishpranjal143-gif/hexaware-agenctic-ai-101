# A task is a scheduled coroutine.
# When you create a task,
# it is automatically scheduled to run as soon as possible.
# Tasks are used to run coroutines concurrently,
# allowing you to manage multiple operations at the same time
# without blocking the main thread.

# Real World: Swiggy Kitchen Orders
# Problem
# Three customers place orders.
# We don't want to cook one order completely before starting the next.
# We schedule all orders.

import asyncio

async def worker():
    print("Worker Started")

    await asyncio.sleep(2)

    print("Worker Finished")

async def main1():

    task = asyncio.create_task(worker())

    await task

asyncio.run(main1())

# Output:
# Worker Started
# waits for 2 seconds
# Worker Finished

import asyncio

async def prepare_order(order_name):
    print(f"{order_name} started")
    await asyncio.sleep(10)
    print(f"{order_name} ready")

async def main():
    pizza_task = asyncio.create_task(
        prepare_order("Pizza")
    )

    burger_task = asyncio.create_task(
        prepare_order("Burger")
    )

    pasta_task = asyncio.create_task(
        prepare_order("Pasta")
    )

    print("All orders scheduled")

    await pizza_task
    await burger_task
    await pasta_task

asyncio.run(main())