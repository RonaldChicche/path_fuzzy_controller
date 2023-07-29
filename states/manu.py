import threading
import time


class Manual(threading.Thread):
    def __init__(self, data_queue, control_queue, board_port):
        super().__init__()
        self.name = 'MANUAL'
        self.done = False
        self.data_queue = data_queue
        self.control_queue = control_queue
        self.board_port = board_port

    def run(self):
        while not self.done:
            # Lógica del estado manual
            if not self.control_queue.empty():
                control = self.control_queue.get()
                #data = self.data_queue.get()
                self.board_port.send_state_variables(control)
                print('<MANUAL> RECEIVED: ', control)
            #time.sleep(1)

    def stop(self):
        self.done = True