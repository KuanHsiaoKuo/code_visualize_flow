import asyncio


async def main_task():
    print("Task started")
    await asyncio.sleep(1)
    print("Task completed")


async def main():
    # Start the main task
    task = asyncio.create_task(main_task())

    # Wait for the task to complete
    await task


# Run the main coroutine inside an event loop
if __name__ == "__main__":
    asyncio.run(main())
