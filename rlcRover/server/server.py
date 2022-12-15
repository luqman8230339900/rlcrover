from aiohttp import web
import ssl  
import aiohttp_cors
routes = web.RouteTableDef()
from rtcbot import Websocket, getRTCBotJS

ws = None # Websocket connection to the robot

@routes.get("/ws")
async def websocket(request):
    global ws
    ws = Websocket(request)
    print("Robot Connected")
    await ws  # Wait until the websocket closes
    print("Robot disconnected")
    return ws.ws



# Called by the browser to set up a connection
@routes.post("/connect")
async def connect(request):
    global ws
    if ws is None:
        raise web.HTTPInternalServerError("There is no robot connected")
    clientOffer = await request.json()
    #conn = ConnectionHandler() # Our ConnectionHandler class!
    # Send the offer to the robot, and receive its response
    ws.put_nowait(clientOffer)
    print("======offer send============")
    robotResponse = await ws.get()
    print("======get response============")
    return web.json_response(robotResponse)


# Serve the RTCBot javascript library at /rtcbot.js
@routes.get("/rtcbot.js")
async def rtcbotjs(request):
    return web.Response(content_type="application/javascript", text=getRTCBotJS())


@routes.get("/")
async def index(request):
	with open("index.html", "r") as f:
		return web.Response(content_type="text/html", text=f.read())
        


async def cleanup(app=None):
    global ws
    if ws is not None:
        c = ws.close()
        if c is not None:
            await c




# ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# ssl_context.load_cert_chain('server.crt', 'server.key')








app = web.Application()
#app.add_routes(routes)
cors = aiohttp_cors.setup(app, defaults={
   "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*"
    )
  })

for route in list(app.add_routes(routes)):
    cors.add(route)
app.on_shutdown.append(cleanup)
#web.run_app(app)
web.run_app(app, port=8081)
# web.run_app(
#           app, port=80, ssl_context=ssl_context
#     )

