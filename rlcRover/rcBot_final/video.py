import asyncio
from rtcbot import CVCamera, CVDisplay
from rtcbot import , CVDisplay

camera = CVCamera()
camera1 = CVCamera1()
display = CVDisplay()

#display.putSubscription(camera)

try:
    asyncio.get_event_loop().run_forever()
finally:
    camera.close()
    display.close()
