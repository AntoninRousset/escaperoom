import asyncio


tasks = set()


async def create():
    pass


async def cancel():
    for task in tasks:
        task.cancel()
    await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
