import os 
import csv
import math
import json


def map_range(value, in_min, in_max, out_min, out_max):
    # Asegurarse de que el valor esté dentro del rango de entrada
    value = max(in_min, min(value, in_max))

    # Calcular la proporción del valor en el rango de entrada
    input_range = in_max - in_min
    output_range = out_max - out_min
    scaled_value = float(value - in_min) / float(input_range)

    # Calcular el valor correspondiente en el rango de salida
    output_value = out_min + (scaled_value * output_range)

    return output_value

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
    # Calcular la distancia entre Pn y W
    distancia_Pn_W = distancia_entre_puntos(Pn[0], Pn[1], W[0], W[1])

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

    return distancia_Pn_W, distancia_Pn_recta

def split_string_to_dict(string):
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

# def extract_xbeeData(trama):
#     try:
#         data = json.loads(trama)
#         state = data[0]['state']
#         command = data[1]['command']
#         waypoints = [point['position'] for point in data[2:]]
#         return {'state': state, 'command': command, 'waypoints': waypoints}
#     except Exception as e:
#         print(f"Error al extraer datos: {e}")
#         return None

def extract_xbeeData(trama):
    try:
        data = json.loads(trama)
        state = data.get('state')
        command = data.get('command')
        waypoints = data.get('waypoints')

        # Si la trama es del tipo "MANUAL"
        if state == "MANUAL" and command:
            sail = command.get('sail')
            rudder = command.get('rudder')
            return {'state': state, 'command': {'sail': sail, 'rudder': rudder}, 'waypoints': []}

        # Si la trama es del tipo "AUTOMATIC"
        elif state == "AUTOMATIC" and waypoints:
            waypoints_list = [{"lat": point.get('lat'), "lng": point.get('lng')} for point in waypoints]
            return {'state': state, 'command': {}, 'waypoints': waypoints_list}

        else:
            raise ValueError("Invalid or incomplete trama format.")

    except Exception as e:
        print(f"Error al extraer datos: {e}")
        print(trama)
        return None

def save_data(data_base, date='00-00'):
    name = 'data-' + date + '.csv'
    current_dir = os.getcwd()
    base_folder = os.path.join(current_dir, "DataBase")
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    file_path = os.path.join(base_folder, name)
    try:
        keys = data_base[0].keys()
        print(keys)
        with open(file_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data_base)
    except Exception as e:
        print(f"Error writing CSV: {e}")
        print("Writing data to JSON instead.")
        with open('data.json', 'w') as output_file:
            json.dump(data_base, output_file)
    