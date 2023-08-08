import time


class Manual():
    def __init__(self, queue, port):
        self.name = 'MANUAL'
        self.control_queue = queue['CONTROL']
        self.board_port = port['BOARD_ENV']
        #self.board_port = port['BOARD_SAIL']

    def run(self):
        if not self.control_queue.empty():
            control = self.control_queue.get()
            self.board_port.send_state_variables(control)
            # Optional sail actuator nano
            # angl = control['sail1']
            # command = f'{int(angl)}\n'
            # self.board_port.write(command)
            print('<MANUAL> RECEIVED: ', control)
            #time.sleep(1)
