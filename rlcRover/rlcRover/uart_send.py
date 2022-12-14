import serial
import time
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS1', 115200, timeout=1)
    ser.reset_input_buffer()
    while True:
        #ser.write(b"Hello from Raspberry Pi!\n")
        ser.write(b"60\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)
