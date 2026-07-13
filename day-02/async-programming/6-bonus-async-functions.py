import asyncio

async def main():

    loop = asyncio.get_running_loop()

    print(type(loop))

if __name__ == "__main__":

    asyncio.run(main())