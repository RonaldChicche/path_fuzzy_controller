import serial
import time

PORT = '/dev/ttyS0'
BAUD = 115200
msg = []

def receive_data(serial):
    data = ""
    while True:
        byte = serial.read()
        #print(byte)
        if byte:
            char = byte.decode('utf-8')
            if char == '/':
                data += char
                if data.endswith('//'):
                    break
            else:
                data += char
    return data


ardu = serial.Serial(PORT, BAUD,
                     parity=serial.PARITY_NONE,
                     stopbits=serial.STOPBITS_ONE,
                     bytesize=serial.EIGHTBITS,
                     timeout=1)

run = True
retry = 3
while run:
    try:
        #x = receive_data(ardu)
        x = '90/90//'
        print(x)
        ardu.write(x.encode())
        time.sleep(1)
        #x = ""
    except Exception as e:
        ardu.close()
        print("Exception:", e)
        ardu = serial.Serial(PORT, BAUD)
        retry -= 1
        if retry == 0:
            ardu.close()
            run = False
