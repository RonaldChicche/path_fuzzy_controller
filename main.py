import sys
import time
import netpyV2 as net
from state_machine import StateMachine
from queue import Queue, LifoQueue


queue = {
    "DATA_ENV": LifoQueue(), # Enviromental variables / Listener -> RuderCtrl-100ms~
    "DATA_WIND": LifoQueue(), # Sail control variables / SailCtrl -> Listener-realtime~
    "DATA_CTRL_REPORT": LifoQueue(maxsize=10), # Report ctrl state variables / Auto <- Sail, Rudder
    "CONTROL": Queue(maxsize=10),
    "MISION": Queue(maxsize=10)
}

ports = {
    "BOARD_ENV": net.SerialPort(port='/dev/ttyS0', baudrate=115200, name='DATA ENV'), # "DATA" -> Listener  /dev/ttyS0->raw  wire
    "BOARD_WIND": net.SerialPort(port='/dev/ttyACM0', baudrate=115200, name='DATA WIND'), # Sail and clutch control data
    #"BOARD_SAIL": net.SerialPort(port='/dev/ttyUSB1', baudrate=115200, name='SAIL ACTUATOR'), # Tester servo
    #"BOARD_ADD": net.SerialPort(port='/dev/ttyUSB0', baudrate=115200), # Raw aditionnal sensor data 
    "XBEE": net.SerialPort(port='/dev/ttyUSB0', baudrate=57600, name='XBEE') # "Command"
}


state_machine = StateMachine(ports=ports, queues=queue)
state_machine.start()

if __name__ == '__main__':
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt received. Closing the state machine...")
        state_machine.close()
        state_machine.join()
        print("State machine closed. Exiting...")
        sys.exit()