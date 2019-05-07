import asyncio
from time import sleep
import random

async def listen(index, listenQueue):

    while True:
        if listenQueue.empty():
            print("started listening %d" % index)
            await listenQueue.put(False)
            await asyncio.sleep(random.randint(1,10))
            break
        else:
            print("Waiting to listen %d" % index)
            await asyncio.sleep(1)
            continue

    print("Finished listening %d" % index)
    await process(index, listenQueue)
    print("Finished awaiting %d" % index)

async def process(index, listenQueue):

    print("Started Process %d" % index)

    await listenQueue.get()
    await asyncio.sleep(1)

    print("Finished processing %d" % index)

async def asyncWorker(index, listenQueue):

    for i in range(3):

        await loop.create_task(listen(index, listenQueue))

async def main(loop):
    listenQueue = asyncio.Queue()
    corouteQueue = asyncio.Queue()
    while True:
        await asyncio.gather(asyncWorker(1, listenQueue), asyncWorker(2, listenQueue), asyncWorker(3, listenQueue), asyncWorker(4, listenQueue))
    
global loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
