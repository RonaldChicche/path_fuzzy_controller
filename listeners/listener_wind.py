import os
import csv
import time
import threading
from datetime import datetime
import sys
sys.path.insert(0, '/home/pi/Documents/states/')
#import controllerFullFuzzy #import SailController


def re_locate(value, from_low, from_high, to_low, to_high):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

class ListenerWind(threading.Thread):
    def __init__(self, ports, queues):
        super().__init__()
        self.name = 'LISTEN WIND'
        self.done = False
        self.data_wind = queues['DATA_WIND']
        # Optional wind config -------------------------------------------
        self.board = ports['BOARD_WIND']
        #self.board_sail = ports['BOARD_SAIL']
        #self.sail = controllerFullFuzzy.SailController()
        self.sail_pos = 0  # Sail initial position
        self.error_sail = 0 
        self.start_time = time.time()
        

    def run(self):
        print('Listener Wind Inited ...')
        while not self.done:
            try:
                # Receive from board
                self.board.trama = self.board.readline().decode()
                data = self.split_string_to_dict(self.board.trama)
                #print(data)
                if data is not None and data['direction'] != '':
                    self.data_wind.put(data)
                #     print(data)
                #     # Optional wind config -----------------------------------------------------------
                #     new_sail_pos = self.sail_controller(int(data['direction'])) # To send for control sail1 = sail2
                #     sail1_to_send = int(re_locate(new_sail_pos, -180, 180, 0, 180))
                #     t = time.time() - self.start_time
                #     print(t)
                #     if t > 0.2:
                #         command = f'{sail1_to_send}\n'
                #         self.board_sail.write(command.encode())
                #         self.start_time = time.time()

                #     wind_data = data['direction']
                #     print(f'sail: {self.sail_pos:.2f}, w: {wind_data}, err: {self.error_sail:.2f}, newP: {new_sail_pos:.2f}, sended: {sail1_to_send}')
                #     self.sail_pos = new_sail_pos
            except Exception as e:
                print("ERROR")
                print(f"Error processing data {self.name}: {e}")

    def sail_controller(self, wind_data): # sail_pos
        sail_pos = self.sail_pos # Add feedback reading as argument
        errorSail = wind_data - sail_pos
        if errorSail > 180:
            errorSail = errorSail - 360
        elif errorSail < -180:
            errorSail = 360 + errorSail
        self.error_sail = errorSail # send to cluch?
        increment = self.sail.compute(wind_data, errorSail)
        # Servo signal adaptation -> return increment instead?
        new = sail_pos + increment
        if new > 180:
            new = new - 360
        elif new < -180:
            new = new + 360
        
        return new
    
    def split_string_to_dict(self, string):
        # Lista de claves para los datos
        keys = ['direction', 'velocity'] 
        data = string.split('/')[:-2]

        # Verificar que la cantidad de datos coincida con la cantidad de claves
        if len(data) != len(keys):
            print(f"Data:{len(data)} - Keys:{len(keys)} -> {data}")
            return None  # Retornar None si no coinciden

        # Crear el diccionario con los datos y las claves
        result = dict(zip(keys, data))
        return result
    

    def stop(self):
        self.done = True
        print(f'<{self.name}> CLOSED')

        