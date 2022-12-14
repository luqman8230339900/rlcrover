import asyncio 
from aiohttp import web
from rtcbot import Websocket, RTCConnection, CVCamera
routes = web.RouteTableDef()

cam = CVCamera(1)

# Connect establishes a websocket connection to the server,
# and uses it to send and receive info to establish webRTC connection.


@routes.get("/ws")
async def websocketHandler(request):
	ws = Websocket(request)
	msg = await ws.get()
	print("======Msg======", msg)
	
		
		

async def connect():
    
    while True:
        conn = RTCConnection()
        conn.video.putSubscription(cam)
        print("==============inside connect==========")
        ws = Websocket("http://localhost:8080/ws")
        remoteDescription = await ws.get()
        print("remote description:====", remoteDescription )
        robotDescription = await conn.getLocalDescription(remoteDescription)
        ws.put_nowait(robotDescription)
        print("Started WebRTC")
        await ws.close()
    


asyncio.ensure_future(connect())
try:
    asyncio.get_event_loop().run_forever()
finally:
    cam.close()
    conn.close()
