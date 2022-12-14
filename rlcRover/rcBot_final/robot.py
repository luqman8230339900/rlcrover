import asyncio
import time
import random
import serial
import time
import requests

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

#keystates = {"w": False, "a": False, "s": False, "d": False , "p": False}


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
    global test
    while True:
        print("                                                   ")
        #conn = RTCConnection()
        # conn = RTCConnection(rtcConfiguration=RTCConfiguration([
        # RTCIceServer(urls="stun:stun.voipstunt.com:3478"),
        # RTCIceServer(urls="turn:182.180.77.38:3478?transport=udp",
        # username="test",credential="test")
			# ]))
        conn = RTCConnection(rtcConfiguration=RTCConfiguration([
               RTCIceServer(urls=["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"]),
               RTCIceServer(urls=["turn:182.180.77.38:3478"],
               username="test",credential="test")
                ]))
       



			

       
       # conn.video.putSubscription(cam)
        
        #conn.audio.putSubscription(mic)
        #speaker.putSubscription(conn.audio.subscribe())
        #print("==============inside connect==========")
        #ws = Websocket("http://localhost:8080/ws")
        
        ws = Websocket("http://182.180.77.38:8081/ws")

        print("==============connected to the server==========")
        remoteDescription = await ws.get()
       
       
       
        print("Test:   ", test)
        if (test == 'f'):
            print("*****************get p ")
            test == ''
            conn.video.putSubscription(camera1)    
        elif (test == 'b'):
            conn.video.putSubscription(cam)
            #conn.audio.putSubscription(mic)
            test == ''           
        else:	
            conn.video.putSubscription(cam)
	 
       
            
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
            global test
            global data
            #print("key code", keystates)
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
               
            elif m == 21:    #   back camera 
                test = 'b'
                print("value of p : ",  test) 
            
            elif m == 22:    #   front camera 
                test = 'f'
                print("value of p : ",  test)
                
                
                
            print("Keypress:", data)
            send_uart(data)
        
    
  

asyncio.ensure_future(connect())
#asyncio.ensure_future(sock_request())
#asyncio.ensure_future(send_sensor_data())
try:
    asyncio.get_event_loop().run_forever()
finally:
    cam.close()
    camera1.close()
    mic.close()

