import os
import csv
import time
import threading
import netpyV2 as net
from datetime import datetime


class DataForwarder(threading.Thread):
    def __init__(self, xbee_port, board_port, data_queue):
        super().__init__()
        self.name = 'LISTENER'
        self.xbee = xbee_port
        self.board = board_port
        self.done = False
        self.start_time = time.time()
        self.data_historic = []
        self.data_queue = data_queue

    def run(self):
        print('Listener Inited ...')
        while not self.done:
            try:
                # Receive from board
                self.board.receive_state_variables()
                data = self.split_string_to_dict(self.board.trama)
                if data is not None:
                    data['time'] = time.time() - self.start_time
                    self.data_queue.put(data)
                    #print(data)  # Comentar
                    self.data_historic.append(data)
                    # Send to command center
                    self.xbee.send_state_variables(data, console=False)
            except Exception as e:
                print("ERROR")
                print(f"Error processing data: {e}")

    def split_string_to_dict(self, string):
        # Lista de claves para los datos
        keys = ['lat', 'lng', 'sat', 'vel', 'alt', 'day', 'mth', 'hor', 'min', 'alx', 'aly', 'hdn', 'tmp', 'hum', 'vwind', 'rwd', 'sail'] 
        data = string.split('/')[:-2]

        # Verificar que la cantidad de datos coincida con la cantidad de claves
        if len(data) != len(keys):
            print(data)
            return None  # Retornar None si no coinciden

        # Crear el diccionario con los datos y las claves
        result = dict(zip(keys, data))
        return result
    
    def save_data(self):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_folder = os.path.join(os.getcwd(), "DataBase")
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)
        file_path = os.path.join(base_folder, f'data_{current_time}.csv')
        try:
            keys = self.data_historic[0].keys()
            with open(file_path, 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(self.data_historic)
        except Exception as e:
            print(f"Error writing CSV: {e}")

    def stop(self):
        self.done = True
        self.save_data()
        