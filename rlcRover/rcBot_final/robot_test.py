import asyncio
from aiohttp import web
import time
import random
import serial
import time
import requests
routes = web.RouteTableDef()

from rtcbot import Websocket, RTCConnection, CVCamera , Microphone, Speaker , CVCamera1
from rtcbot.base import ThreadedSubscriptionProducer
from aiortc import RTCConfiguration, RTCIceServer


test = ''
data = ''




cam = CVCamera()
mic = Microphone()
speaker = Speaker()

time.sleep(10)
camera1 = CVCamera1()



keystates = {"w": False, "a": False, "s": False, "d": False}





#uart send
def send_uart(data):
	if __name__ == '__main__':
		ser = serial.Serial('/dev/ttyS1', 115200, timeout=1)
		ser.reset_input_buffer()
		# ser.write(b"60\n")
		# line = ser.readline().decode('utf-8').rstrip()
		
		srt_data = data + "\n"
		print(srt_data)
		#ser.write(srt_data)
		
		ser.write(srt_data.encode())






async def connect():
    global test
    global conn
    while True:
        print("                                                   ")
        conn = RTCConnection()
        # conn = RTCConnection(rtcConfiguration=RTCConfiguration([
        # RTCIceServer(urls="stun:stun.voipstunt.com:3478"),
        # RTCIceServer(urls="turn:182.180.77.38:3478?transport=udp",
        # username="test",credential="test")
			# ]))
        # conn = RTCConnection(rtcConfiguration=RTCConfiguration([
               # RTCIceServer(urls=["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"]),
               # RTCIceServer(urls="turn:182.180.77.38:3478",
               # username="test",credential="test")
                # ]))
       
        if (test == 'p'):
            print("*****************get p ")
            test == ''
            #robotDescription = await conn.getLocalDescription(remoteDescription)
            conn.video.putSubscription(camera1)    
        elif (test == 'w'):
            print("*****************get W ")			
            conn.video.putSubscription(cam)
            test == ''           
        else:	
            conn.video.putSubscription(cam)
	                    #print("==============inside connect==========")
            ws = Websocket("http://localhost:8080/ws")
	        
	        #ws = Websocket("http://182.180.77.38:8081/ws")
            print("==============connected to the server==========")
            remoteDescription = await ws.get()      
	            
            print("********* Successfully get Client description:====")
            print("                                                   ")
            robotDescription = await conn.getLocalDescription(remoteDescription)
            print("                                                   ")
            print("********* Successfully get RC_CAR description:====")
            ws.put_nowait(robotDescription)
            print("                                                   ")
            print(" ********* Successfully Start Streaming:====")
            await ws.close()  


			

       


    

        


        @conn.subscribe
        async def onMessage(m):
            global conn
            global keystates
            global test
            if m["keyCode"] == 87:  # W
                keystates["w"] = m["type"] == "keydown"
                data = 'w'
                test = 'w'
                print("value of w : ",  test)
            
            elif m["keyCode"] == 83:  # S
                keystates["s"] = m["type"] == "keydown"
           
            elif m["keyCode"] == 65:  # A
                keystates["a"] = m["type"] == "keydown"
           
            elif m["keyCode"] == 68:  # D
                keystates["d"] = m["type"] == "keydown"
                data = 'p'
                #camera_flip()
                test = 'p'
                print("value of p : ",  test)
                conn.video.putSubscription(camera1)
                #remoteDescription = await ws.get()
                
           




                
            # elif m == 80:    # a   pause
                # data = 'p'
                # test = data


               
            
            
            # print("Keypress:", data)
            # send_uart(data)
        

  

asyncio.ensure_future(connect())


#asyncio.ensure_future(sock_request())
#asyncio.ensure_future(send_sensor_data())
try:
    asyncio.get_event_loop().run_forever()
finally:
    cam.close()
    mic.close()

