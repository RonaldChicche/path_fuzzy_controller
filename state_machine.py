import threading
import json
from states.auto import Automatic
from states.manu import Manual
from listeners.listener import ListenerEnviroment
from listeners.listener_wind import ListenerWind
#from utilities import *


class StateMachine(threading.Thread):
    def __init__(self, ports, queues):
        super().__init__()
        self.name = 'STATE_MACHINE'
        self.done = False
        # Comunication queues
        self.queue = queues
        self.port = ports
        # Operation threads
        self.listener = ListenerEnviroment(ports=self.port, queues=self.queue)
        self.listener_wind = ListenerWind(ports=self.port, queues=self.queue)
        self.state_name = 'MANUAL'
        self.current_state = Manual(queue=self.queue, port=self.port)

    def run(self):
        # Start threads
        print("<STATE_MACHINE> Starting")
        self.listener.start()
        self.listener_wind.start()
        while not self.done:
            # Escucha de parte de xbee
            xbee_response = self.port['XBEE'].hear()
            if xbee_response != None:
                #print(xbee_data)
                xbee_data = self.extract_xbeeData(xbee_response)
                if xbee_data != None:
                    if xbee_data['state'] == 'M': 
                        #print('IN MANUAL')
                        self.queue['CONTROL'].put(xbee_data['control'])
                        if self.state_name == 'AUTOMATIC':
                            self.set_state("MANUAL")
                    
                    if xbee_data['state'] == 'A':
                        #print('IN AUTOMATIC')
                        self.queue['MISION'].put(xbee_data['mision'])
                        if self.state_name == 'MANUAL':
                            self.set_state("AUTOMATIC")
            # Execute state
            self.current_state.run()

            # Mision done rutine
            if self.state_name == 'AUTOMATIC' and self.current_state.done:
                self.set_state("MANUAL")

    def set_state(self, new_state_name):
        self.state_name = new_state_name
        if self.state_name == 'AUTOMATIC':
            self.current_state = Automatic(queue=self.queue, port=self.port)
        else:
            self.current_state = Manual(queue=self.queue, port=self.port)
        print(f'<MAIN> New state: {self.current_state}')

    def extract_xbeeData(self, trama):
        try:
            data = json.loads(trama)
            state = data.get('state')
            # Si la trama es del tipo "MANUAL"
            if state == "M":
                control = data.get('control')
                sail1 = control.get('sail1')
                sail2 = control.get('sail2')
                rudder = control.get('rudder')
                clutch = control.get('clutch')
                return {'state': state, 'control': {'rudder': rudder, 'sail1': sail1, 'sail2': sail2, 'clutch':clutch}, 'mision': []}

            # Si la trama es del tipo "AUTOMATIC"
            elif state == "A":
                mision = data.get('mision')
                mision_list = [{"lat": point.get('lat'), "lng": point.get('lng')} for point in mision]
                return {'state': state, 'control': {}, 'mision': mision_list}

            else:
                raise ValueError("Invalid or incomplete trama format.")

        except Exception as e:
            print(f"Error al extraer datos: {e}")
            print(trama)



    def close(self):
        self.done = True
        self.listener.stop()
        self.listener.join()
        self.listener_wind.stop()
        self.listener_wind.join()
        self.port['XBEE'].close_port()
        self.port['BOARD_ENV'].close_port()
        self.port['BOARD_WIND'].close_port()
        print(f'<{self.name}> CLOSED')