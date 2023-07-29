import threading
import json
from states.auto import Automatic
from states.manu import Manual
from listener import DataForwarder
#from utilities import *


class StateMachine(threading.Thread):
    def __init__(self, start_state, ports, queues):
        super().__init__()
        self.name = 'MAIN_STATE_MACHINE'
        self.done = False
        self.state_name = start_state
        # Comunication queues
        self.queue = queues
        self.port = ports
        # Operation threads
        self.listener = DataForwarder(self.port['XBEE'], self.port['BOARD'], self.queue['DATA'])
        if self.state_name == 'AUTOMATIC':
            self.current_state = Automatic(self.queue['DATA'], self.queue['MISION'], self.port["BOARD"])
        else:
            self.current_state = Manual(self.queue['DATA'], self.queue['CONTROL'], self.port["BOARD"])
    
    def set_state(self, state_name):
        self.current_state.done = True
        self.current_state.join()
        self.state_name = state_name
        if state_name == 'MANUAL':
            self.current_state = Manual(self.queue['DATA'], self.queue['CONTROL'], self.port["BOARD"])
        else:
            self.current_state = Automatic(self.queue['DATA'], self.queue['MISION'], self.port["BOARD"])
        self.current_state.start()

    def run(self):
        # Start threads
        self.listener.start()
        self.current_state.start()
        while not self.done:
            # Escucha de parte de xbee
            xbee_response = self.port['XBEE'].hear()
            if xbee_response != None:
                # Cambio de estado basado en alguna lógica
                xbee_data = self.extract_xbeeData(xbee_response)
                #print(xbee_data)
                if xbee_data != None:
                    if xbee_data['state'] == 'MANUAL':
                        print('IN MANUAL')
                        self.queue['CONTROL'].put(xbee_data['control'])
                        if self.state_name == 'AUTOMATIC':
                            self.set_state("MANUAL")
                    
                    if xbee_data['state'] == 'AUTOMATIC':
                        print('IN AUTOMATIC')
                        self.queue['MISION'].put(xbee_data['mision'])
                        if self.state_name == 'MANUAL':
                            self.set_state("AUTOMATIC")

                    # if self.state_name == "MANUAL":
                    #     print('IN MANUAL')
                    #     self.queue['CONTROL'].put(xbee_data['control'])
                    #     if xbee_data['state'] == 'AUTOMATIC':
                    #         self.set_state("AUTOMATIC")
                    #         print('CHANGED')
                        
                    # elif self.state_name == "AUTOMATIC":
                    #     print('IN AUTO')
                    #     self.queue['MISION'].put(xbee_data['mision'])
                    #     if xbee_data['state'] == 'MANUAL':
                    #         self.set_state("MANUAL")
                    #         print('CHANGED')

                    
                    print(self.state_name, ' -> ', xbee_data['state'])
                        

            if self.state_name == 'AUTOMATIC' and self.current_state.done:
                self.set_state("MANUAL")

    def extract_xbeeData(self, trama):
        try:
            data = json.loads(trama)
            state = data.get('state')
            control = data.get('control')
            mision = data.get('mision')

            # Si la trama es del tipo "MANUAL"
            if state == "MANUAL" and control:
                sail = control.get('sail')
                rudder = control.get('rudder')
                return {'state': state, 'control': {'sail': sail, 'rudder': rudder}, 'mision': []}

            # Si la trama es del tipo "AUTOMATIC"
            elif state == "AUTOMATIC" and mision:
                mision_list = [{"lat": point.get('lat'), "lng": point.get('lng')} for point in mision]
                return {'state': state, 'control': {}, 'mision': mision_list}

            else:
                raise ValueError("Invalid or incomplete trama format.")

        except Exception as e:
            print(f"Error al extraer datos: {e}")
            print(trama)
            return None

    def close(self):
        self.done = True
        self.current_state.stop()
        print(self.current_state)
        self.current_state.join()
        print(self.state_name, 'STOPED')
        self.listener.stop()
        self.listener.join()
        print('LISTENER STOPED')
        self.port['XBEE'].close_port()
        self.port['BOARD'].close_port()
        print('PORTS STOPED')
        print(self.current_state)