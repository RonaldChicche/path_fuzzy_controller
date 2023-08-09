import time 
import math
#from utilities import*
from states.controllerFullFuzzy import RudderController, DHController, SailController


# Add mision recorder

class Automatic():
    def __init__(self, queue, port):
        self.name = 'AUTOMATIC'
        self.done = False
        self.data_queue = queue['DATA_ENV']
        self.mision_queue = queue['MISION']
        self.xbee_port = port['XBEE']
        self.board_port = port['BOARD_ENV']
        # Waypoint charge
        if not self.mision_queue.empty():
            self.waypoints = self.mision_queue.get()
        # First lecture
        if not self.data_queue.empty():
            self.data_list = self.data_queue.get()
            self.pos_partida = (float(self.data_list['lat']), float(self.data_list['lng']))
            self.posBef = self.pos_partida
        # Inicializar objetos de controladores
        self.desire = DHController()  # por ahora solo controla el bucle
        self.rudder = RudderController()
        self.sail = SailController()
        #self.clutch = ClutchController()
        # Datos de inicio
        self.start_time = time.time()
        self.past_position = (float(self.data_list['lat']), float(self.data_list['lng']))
        self.current_waypoint = (self.waypoints[0]['lat'], self.waypoints[0]['lng'])
        self.sail_pos = 0  # Sail initial position
        self.error_sail = 0
        self.rudder_pos = 0 # Rudder initial position
        self.clutch = False
        self.waypoints_done = []

    def run(self):
        # Data Reading 
        new_data_list = self.data_queue.get() # Read from queue 
        if self.data_list['time'] < new_data_list['time']: # Watch out whether it is new data or not
            data_list = new_data_list
            self.data_list = new_data_list
        else:
            data_list = self.data_list
        # Control variables update
        t = data_list['time']  
        self.current_position = (float(data_list['lat']), float(data_list['lng']))
        self.relative_wind = float(data_list['rwd'])
        self.heading = float(data_list['hdn'])
        if self.heading > 180:
            self.heading = self.heading - 360 
        
        # Desired Heading -------------------------------------------------------------------------------
        self.desired_heading = angle_to_north(*self.current_position, *self.current_waypoint)
        self.desvio = distancia_a_recta(self.pos_partida, self.current_waypoint, self.current_position)
        self.new_desired_heading = self.heading_controller(self.relative_wind, 
                                                           self.heading, 
                                                           self.desvio, 
                                                           self.desired_heading)
        
        # Desired Rudder -------------------------------------------------------------------------------
        self.curse = angle_to_north(*self.past_position, *self.current_position)
        self.rudder_pos = self.rudder_controller(self.relative_wind, 
                                             self.new_desired_heading, 
                                             self.heading, 
                                             self.curse)

        # Desired Sail ---------------------------------------------------------------------------------
        # self.current_sail_pos = read feedback to aplly controller
        # self.increment = self.sail_controller(self.relative_wind, self.current_sail_pos)
        new_sail_pos = self.sail_controller(self.relative_wind) # To send for control sail1 = sail2
        # Adapt output for board
        sail1_to_send = int(re_locate(new_sail_pos, -180, 180, 0, 180)) # Mini sailboat
        #to_send = int(re_locate(new_sail_pos, -180, 180, 0, 180)) # Real sailboat
        
        # Desired clutch -------------------------------------------------------------------------------
        if self.clutch == True:
            clutch_angle = 120
        else:
            clutch_angle = 0
        
        # Additional control data
        self.distancia_recorrida = distancia_entre_puntos(*self.past_position, *self.current_position)
        self.distancia_waypoint = distancia_entre_puntos(*self.current_position, *self.current_waypoint)

        #self.current_waypoint reached
        if self.distancia_waypoint < 5: # Adjust as you need (meters)
            point_reached = self.waypoints.pop(0)
            self.pos_partida = self.current_position
            print('<AUTO> Waypoint:', point_reached, 'REACHED')
        
        # Mision Complete
        if not self.waypoints:
            self.done = True                
            print('<AUTO> Mision DONE')

        # Send to board env and xbee ----------------------------------------------------------------------------
        dt = time.time() - self.start_time
        if dt > 1: #enviar en lapsos de 1 seg
            control_trama = f'{int(90 + self.rudder_pos)}/{sail1_to_send}/{sail1_to_send}/{clutch_angle}//'
            print(f'<AUTO> Control: {control_trama} ---- t:{dt}')
            self.board_port.send_state_variables(control_trama, console=True)
            self.start_time = time.time()
            # Send to xbee
            state_str = f"CC/{self.desvio:.2f}/{self.desired_heading}/{self.new_desired_heading:.2f}/{self.sail_pos:.2f}/{self.rudder_pos:.2f}/{self.relative_wind:.2f}/{self.heading:.2f}/{self.pos_partida}/{self.current_position}/{self.past_position}/{self.distancia_recorrida:.2f}/{self.distancia_waypoint:.2f}/{self.current_waypoint}/{t:4f}//"
            self.xbee_port.send_state_variables(state_str)

        # Update sail position for servo purposes
        self.past_position = self.current_position

    def heading_controller(self, relative_wind, heading, desvio, desired_heading):
        WH = heading - relative_wind
        DRWHin = WH - desired_heading
        DRWHout = self.desire.compute(relative_wind, DRWHin, desvio)
        DH = WH + DRWHout
        
        return DH
    
    def rudder_controller(self,RWH, DH, H, C):
        DHC = DH - C
        DHH = DH - H
        if DHC > 180 or DHC < -180:
            DHC = DHC - 360 
        if DHH > 180 or DHH < -180:
            DHH = DHH - 360 
        DHHAdd = DHH
        rudder_angle = self.rudder.compute(DHC, DHH, DHHAdd, RWH)
        
        return rudder_angle
    
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
    
   
def angle_to_north(lat1, lon1, lat2, lon2):
    # Convertir las coordenadas de grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    # Calcular el ángulo respecto al norte utilizando la función atan2
    angle_rad = math.atan2(dlon, dlat) 
    angle_deg = math.degrees(angle_rad)

    return angle_deg
    
def distancia_entre_puntos(lat1, lon1, lat2, lon2):
    # Radio de la Tierra en metros
    radio_tierra = 6371000.0

    # Convertir las coordenadas a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Diferencia de latitud y longitud
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Calcular la distancia usando la fórmula de Haversine
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distancia = radio_tierra * c

    return distancia

def distancia_a_recta(P0, W, Pn):

    # Calcular las coordenadas del punto proyectado de Pn sobre la línea que pasa por W y P0
    x0, y0 = P0[1], P0[0]  # Coordenadas P0 (lon, lat)
    x1, y1 = W[1], W[0]    # Coordenadas W (lon, lat)
    x2, y2 = Pn[1], Pn[0]  # Coordenadas Pn (lon, lat)

    A = x0 - x1
    B = y0 - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D
    param = dot / len_sq

    if param < 0:
        x = x1
        y = y1
    elif param > 1:
        x = x2
        y = y2
    else:
        x = x1 + param * C
        y = y1 + param * D

    # Calcular la distancia entre Pn y el punto proyectado
    distancia_Pn_recta = distancia_entre_puntos(Pn[0], Pn[1], y, x)

    return distancia_Pn_recta

def re_locate(value, from_low, from_high, to_low, to_high):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low