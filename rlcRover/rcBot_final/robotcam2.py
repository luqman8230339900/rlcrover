import asyncio
import time
import random
import serial
import time

from rtcbot import Websocket, RTCConnection, CVCamera2, Microphone, Speaker
from rtcbot.base import ThreadedSubscriptionProducer
from aiortc import RTCConfiguration, RTCIceServer

cam = CVCamera2()
mic = Microphone()
speaker = Speaker()
# conn = RTCConnection()
# conn.video.putSubscription(camera)
#keystates = {"w": False, "a": False, "s": False, "d": False, "p": False}


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
		# line = ser.readline().decode('utf-8').rstrip()
		# print(line)
		# time.sleep(1)




# #-----uart class---

# def receive_uart():
	# if __name__ == '__main__':
		# ser = serial.Serial('/dev/ttyS1', 115200, timeout=1)
		# ser.reset_input_buffer()
		# while True:
			# if ser.in_waiting > 0:
				# line = ser.readline().decode('utf-8').rstrip()
				# print(line)
				# return line

	

# class Uart(ThreadedSubscriptionProducer):
    # def _producer(self):
        # self._setReady(True) # Notify that ready to start gathering data
        # while not self._shouldClose: # Keep gathering until close is requested
            # #time.sleep(1)
            # data = receive_uart()
            # #Send the data to the asyncio thread, 
            # #so it can be retrieved with await mysensor.get()
            # self._put_nowait(data)
        # self._setReady(False) # Notify that sensor is no longer operational

# myuart = Uart()

# async def send_sensor_data():
    # while True:
        # data = await myuart.get() # we await the output of MySensor in a loop
        # conn.put_nowait(data)




# Connect establishes a websocket connection to the server,
# and uses it to send and receive info to establish webRTC connection.

async def connect():
    while True:
        #conn = RTCConnection()
        print("==============inside connect==========")
        #conn = RTCConnection()
        conn = RTCConnection(rtcConfiguration=RTCConfiguration([
               RTCIceServer(urls="stun:stun.l.google.com:19302"),
               RTCIceServer(urls="turn:182.180.77.38:3478?transport=udp",
               username="test",credential="test")
                ]))
                
        conn.video.putSubscription(cam)
  #      conn.audio.putSubscription(mic)
 #       speaker.putSubscription(conn.audio.subscribe())

        ws = Websocket("http://182.180.77.38:8443/ws")
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
        def onMessage(m):
            #global keystates



            print("key press", m)
            
            if m == 87:    # W forward
                data = 'w'
                
            elif m == 83:    # s  back
                data = 's'
            
            elif m == 68:    # d   right
                data = 'd'

            elif m == 65:    # a   left
                data = 'a'
       
            elif m == 108:    # a   light
                data = 'l'
                
            elif m == 104:    # a   pause
                data = 'p'                
                
            # if m["keyCode"] == 87:    # W
                # keystates["w"] = m["type"] == "keydown"
                # data = 'w'
            # elif m["keyCode"] == 83:  # S
                # keystates["s"] = m["type"] == "keydown"
                # data = 's'
            # elif m["keyCode"] == 65:  # A
                # keystates["a"] = m["type"] == "keydown"
                # data = 'a'
            # elif m["keyCode"] == 68:  # D
                # keystates["d"] = m["type"] == "keydown"
                # data = 'd'
            # elif m["keyCode"] == 80:  # p
                # keystates["p"] = m["type"] == "keydown"
                # data = 'p'  
                           
            print("Keypress:", data)
            send_uart(data)
        
    
    

asyncio.ensure_future(connect())
#asyncio.ensure_future(send_sensor_data())
#asyncio.ensure_future(send_sensor_data())
try:
    asyncio.get_event_loop().run_forever()
finally:
    cam.close()
    speaker.close()
    mic.close()
    
    
