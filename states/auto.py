import threading
import time 
from utilities import*
from states.controllerFullFuzzy import SailController, RudderController, DHController


class Automatic(threading.Thread):
    def __init__(self, data_queue, mision_queue, board_port, xbee_port=None):
        super().__init__()
        self.name = 'AUTOMATIC'
        self.done = False
        self.data_queue = data_queue
        self.mision_queue = mision_queue
        self.board_port = board_port
        self.xbee_port = xbee_port
        # Inicializar objetos de controladores
        self.desire = DHController()  # por ahora solo controla el bucle
        self.rudder = RudderController()
        self.sail = SailController()
        self.waypoints = None

    def run(self):
        # Waypoint charge
        if not self.mision_queue.empty():
            self.waypoints = self.mision_queue.get()
        # Init algorithm
        if not self.data_queue.empty():
            data_list = self.data_queue.get()
        
        AS = 0  # Posicion inicial
        P0 = (float(data_list['lat']), float(data_list['lng']))
        posBef = P0

        while not self.done:
            
            if not self.data_queue.empty():
                # Data update - 
                new_data_list = self.data_queue.get()
                if data_list['time'] < new_data_list['time']:
                    data_list = new_data_list
                t = data_list['time']    
                waypoint = (self.waypoints[0]['lat'], self.waypoints[0]['lng'])
                print('->', waypoint)
                posAct = (float(data_list['lat']), float(data_list['lng']))
                H = float(data_list['hdn'])
                RWH = float(data_list['rwd'])
                if H > 180:
                    H = H - 360 
                if RWH > 180:
                    RWH = RWH - 360 
                
                # Desired Heading
                DHin = angle_to_north(*posAct, *waypoint)
                WH = RWH + H
                DRWHin = WH - DHin
                distancia_P0_W, distancia_Pn_recta = distancia_a_recta(P0, waypoint, posAct)
                DRWHout = self.desire.compute(RWH, DRWHin, distancia_Pn_recta)
                DH = WH + DRWHout
                # Desired Sail
                errorSail = AS - RWH
                if errorSail < -180 or errorSail > 180:
                    errorSail = 360 - errorSail
                sail_inc = self.sail.compute(RWH, errorSail)
                AS = AS + sail_inc # update sail angle
                if AS > 90: 
                    AS = 90
                elif AS < -90:
                    AS = -90
                # Desired Rudder
                C = angle_to_north(*posBef, *posAct)
                DHC = DH - C
                DHH = DH - H
                if DHC > 180 or DHC < -180:
                    DHC = DHC - 360 
                if DHH > 180 or DHH < -180:
                    DHH = DHH - 360 
                DHHAdd = DHH
                rudder_angle = self.rudder.compute(DHC, DHH, DHHAdd, RWH)
                
                dist_bef_act = distancia_entre_puntos(*posBef, *posAct)
                

                # Send Data
                control_list = f'{int(90 + AS/2)}/{int(90 + rudder_angle)}//'
                print(control_list)
                self.board_port.send_state_variables(control_list)
                print(f'-> DiRumbo: {distancia_Pn_recta:.2f} || DHin: {DHin:.2f} -> DHOut: {DH:.2f}')
                print(f'   Sail: {AS:.2f}, Rudder: {rudder_angle:.2f}, ---->>>> RWH: {RWH:.2f}/Heading: {H:.2f}')
                print(f'   PosInit: {P0}, PosBef: {posBef} ------ >>>> DistanciaBefAct{dist_bef_act:4f}')  
                print(f'   PosAct: {posAct}, PosBef: {posBef} ------ >>>> DistanciaBefAct{dist_bef_act:4f}') 
                print(f'   DiObj: {distancia_P0_W:.2f}, Waypoint: {waypoint}  ------ >>>> time : {t:4f}')
                time.sleep(0.1)
                posBef = posAct


            # Waypoint reached
            if distancia_entre_puntos(*posAct, *waypoint) < 6:
                point_reached = self.waypoints.pop(0)
                P0 = posAct
                print('W:', point_reached, 'REACHED')
            
            # Mision Complete
            if not self.waypoints:
                self.done = True                
                print('DONE')

    def stop(self):
        self.done = True
