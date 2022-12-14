import asyncio
import time
from rtcbot import CVCamera, CVDisplay , CVCamera1

camera = CVCamera()
display = CVDisplay()
display.putSubscription(camera)


time.sleep(10)


camera1 = CVCamera1()
display2 = CVDisplay()
display2.putSubscription(camera1)



try:
    asyncio.get_event_loop().run_forever()
finally:
    camera.close()
    display.close()
    display2.close()
