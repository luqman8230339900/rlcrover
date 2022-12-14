import asyncio
from rtcbot import CVCamera, CVDisplay , CVCamera2

camera = CVCamera()
display = CVDisplay()

@camera.subscribe
def onFrame(frame):
    print("got video frame")
    display.put_nowait(frame)

try:
    asyncio.get_event_loop().run_forever()
finally:
    camera.close()
    display.close()
