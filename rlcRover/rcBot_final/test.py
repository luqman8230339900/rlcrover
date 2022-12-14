import time
import asyncio
async def  Task_ex(x):
   time.sleep(4)
   print("Task {}".format(x))
   
   
   
async def Produce_task():
   for n in range(10):
      asyncio.set_future(Task_ex(n))

loop = asyncio.get_event_loop()
loop.run_forever(Produce_task())
loop.close()
