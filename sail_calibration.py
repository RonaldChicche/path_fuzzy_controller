import serial
import time
import numpy as np
from states.controllerFullFuzzy import SailController

# Configura el puerto serial xbee/ttyUSB0
puerto_serial = serial.Serial('/dev/ttyACM0', 115200)   # Arduino - sensor 
servo_serial = serial.Serial('/dev/ttyUSB1', 115200)  # Nano - servo
sail_controller = SailController()


def enviar_comando(angulo):
    comando = f"{angulo}\n" 
    servo_serial.write(comando.encode())
    print(f'Comand: {comando}')

def arduino_map(value, from_low, from_high, to_low, to_high):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

def read_puerto():
    if servo_serial.in_waiting > 0:
        data = servo_serial.readline().decode()
        print(data) 


try:
    # # Servo controler ----
    # while True:
    #     for angulo in range(0, 180, 10):  # Cambia los valores de inicio, fin y paso según tus necesidades
    #         enviar_comando(angulo)
    #         read_puerto()
    #         time.sleep(0.1)  # Espera 0.1 segundos antes de enviar el siguiente comando

    #     for angulo in range(180, 0, -10):  # Cambia los valores de inicio, fin y paso según tus necesidades
    #         enviar_comando(angulo)
    #         read_puerto()
    #         time.sleep(0.1)
    # Data receiver ----
    wind_data = 0
    sail_pos = 0
    start_time = time.time()
    while True:
        wind_data = puerto_serial.readline().decode()
        timer = time.time() - start_time
        print(wind_data, timer)
        # #wind_data = read_puerto(wind_data)
        # wind_data = int(wind_data)
        # errorSail = wind_data - sail_pos
        # if errorSail > 180:
        #     errorSail = errorSail - 360
        # elif errorSail < -180:
        #     errorSail = 360 + errorSail

        # increment = sail_controller.compute(wind_data, errorSail)
        # new = sail_pos + increment
        # if new > 180:
        #     new = new - 360
        # elif new < -180:
        #     new = new + 360
        
        # to_send = int(arduino_map(new, -180, 180, 0, 180))
        # print(f'sail: {sail_pos:.2f}, w: {wind_data}, err: {errorSail:.2f}, inc: {increment:.2f}, newP: {new:.2f}, sended: {to_send}')
        # #msg = f'CC/120/130/-120/{sail_pos:.2f}/-33/{wind_data}/90/(-12.45454, -77.36363)/(-12.45455, -77.363563)/4/100/(-12.45454, -77.36363)/1024.45//\n'
        # t = time.time() - start_time
        # if t > 0.5:
        #     #servo_serial.write(f'{new}\n'.encode())
        #     enviar_comando(to_send)
        #     start_time = time.time()
        #     print(t, '->', new)
        # sail_pos = new

except KeyboardInterrupt:
    print("Interrupción del usuario. Deteniendo el envío.")

except AssertionError as e:
    print(e)

except ValueError as e:
    print(e)

finally:
    #print(f'sail: {sail_pos:.2f}, w: {wind_data}, err: {errorSail:.2f}, inc: {increment:.2f}, sended: {new:.2f}')
    # Cierra el puerto serial al finalizar
    servo_serial.close()
