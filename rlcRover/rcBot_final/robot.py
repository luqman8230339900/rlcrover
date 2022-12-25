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





def cam_front():
    global connection
    global camera1
    global  videoSubscription2
    print("previous camea close done ")
    videoSubscription2 = camera1.subscribe()
    conn.video.putSubscription(videoSubscription2)
    print("camera stream change to camera 2") 
	
def cam_back():
    global connection
    global  videoSubscription
    print("previous camea close done ")
    videoSubscription = cam.subscribe()
    conn.video.putSubscription(videoSubscription)
    print("camera stream change to camera 2") 	





async def connect():
    global test
    global  videoSubscription
    global conn
    while True:
        print("                                                   ")

    
        ws = Websocket("http://13.232.83.112:8081/ws")
        print("==============connected to the server==========")
        remoteDescription = await ws.get()
        videoSubscription = cam.subscribe()	

        conn = RTCConnection(rtcConfiguration=RTCConfiguration([
               RTCIceServer(urls=["stun:13.232.83.112:3478"]),
               RTCIceServer(urls=["turn:13.232.83.112:3478?transport=udp"],
               username="test",credential="test")
                ]))        
        connection = conn        
        conn.video.putSubscription(videoSubscription)
 
   
		
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
            global test
            global data
            global conn
            #print("key code", keystates)
            print("key press", m)
            
            
            # if m["keyCode"] == 87:  # W
                # test = 'f'
                # cam_front()

            # if m["keyCode"] == 83:  # s
                # test = 'b'
                # cam_back()
                
                
                
                           
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
                cam_back()
            
            elif m == 22:    #   front camera 
                test = 'f'
                print("value of p : ",  test)
                cam_front() 
                
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

