import sys
import time
import netpyV2 as net
from states.auto import Automatic
from states.manu import Manual
from state_machine import StateMachine
from queue import Queue, LifoQueue


queue = {
    "DATA": LifoQueue(),
    "CONTROL": Queue(),
    "MISION": Queue()
}

ports = {
    "BOARD": net.SerialPort(port='/dev/ttyS0', baudrate=115200),
    "XBEE": net.SerialPort(port='/dev/ttyUSB0', baudrate=57600)
}

# states = {
#     "MANUAL": Manual(queue['DATA'], queue['CONTROL'], ports["BOARD"]),
#     "AUTOMATIC": Automatic(queue['DATA'], queue['MISION'], ports['BOARD']),
# }

state_machine = StateMachine("MANUAL", ports=ports, queues=queue)
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