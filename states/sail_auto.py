import threading
import time 
from utilities import*
from states.controllerFullFuzzy import SailController

# Pass data queue, reading direction/velocity sensor and send to Listener and AutoRudder
# Pass ctrl queue, state control variables -> Auto for reading 
# data -> dir/vel
class AutomaticSail(threading.Thread):
    def __init__(self, queue, port):
        super().__init__()
        self.name = 'AUTO RUDDER'
        self.done = False
        self.wind_queue = queue['DATA_WIND']
        self.board_port = port['BOARD_WIND']
        # Inicializar objetos de controladores
        self.sail_controller = SailController()
        #self.clucth_controller = ClutchController()
        self.state_data = {}
        # Variables
        self.windDir_data = 0
        self.sail_pos = 0
        self.error_sail = 0
        self.clutch_state = False
        self.windVel_data = 0

    def run(self):
        while not self.done:
            self.board_port.hear()
            lecture = self.board_port.trama.decode()
            data = self.split_lecture(lecture)
            self.data_queue.put(data) # Send to listener
            # Controllers
            self.control_sail(data['winDir'])
            self.control_clutch(data['winVel'])
            self.state_data['sail'] = self.sail_pos
            self.state_data['clutch'] = self.clutch_state
            print(self.board_port.trama)

    def control_sail(self, windDir):
        self.windDir = int(windDir)
        errorSail = self.windDir - self.sail_pos
        if errorSail > 180:
            errorSail = errorSail - 360
        elif errorSail < -180:
            errorSail = 360 + errorSail
        increment = self.sail_controller.compute(self.windDir, errorSail)
        new = self.sail_pos + increment
        if new > 180:
            new = new - 360
        elif new < -180:
            new = new + 360

        self.sail_pos = new

    def control_clutch(self, winVel, sail_pos):
        # Use clutch control here
        self.clutch_state = False

    def split_lecture(self, lecture):
        keys = ['windDir', 'windVel']
        data = lecture.split('/')
        if len(data) != len(keys):
            print(f"Data:{len(data)} - Keys:{len(keys)} -> {data}")
            return None
        result = dict(zip(keys, data))
        return result


    def close(self):
        self.done = True
        print(self.name, '-> CLOSED')


class AutoSail:
    def __init__(self, queue, port):
        self.name = 'AUTO RUDDER'
        self.board_port = port['BOARD_WIND']
        self.report_queue = queue
        # Inicializar objetos de controladores
        self.sail_controller = SailController()
        #self.clucth_controller = ClutchController()
        self.state_data = {}
        # Variables
        self.windDir_data = 0
        self.sail_pos = 0
        self.error_sail = 0
        self.clutch_state = False
        self.windVel_data = 0

    def control_sail(self, windDir):
        self.windDir = int(windDir)
        errorSail = self.windDir - self.sail_pos
        if errorSail > 180:
            errorSail = errorSail - 360
        elif errorSail < -180:
            errorSail = 360 + errorSail
        increment = self.sail_controller.compute(self.windDir, errorSail)
        new = self.sail_pos + increment
        if new > 180:
            new = new - 360
        elif new < -180:
            new = new + 360

        self.sail_pos = new

    def control_clutch(self, winVel, sail_pos):
        # Use clutch control here
        self.clutch_state = False

    def split_lecture(self, lecture):
        keys = ['windDir', 'windVel']
        data = lecture.split('/')
        if len(data) != len(keys):
            print(f"Data:{len(data)} - Keys:{len(keys)} -> {data}")
            return None
        result = dict(zip(keys, data))
        return result

    def process_data(self, data):
        # Process the data received from the queue or port
        # Call control_sail and control_clutch with appropriate arguments
        self.control_sail(data['windDir'])
        self.control_clutch(data['windVel'], self.sail_pos)
        self.state_data['sail'] = self.sail_pos
        self.state_data['clutch'] = self.clutch_state
        print(self.board_port.trama)

    def close(self):
        # Perform any cleanup if needed
        print(self.name, '-> CLOSED')
