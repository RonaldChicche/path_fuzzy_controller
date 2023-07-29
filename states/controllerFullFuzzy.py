import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl



class DHController:
    def __init__(self):
        # Variable de control de bucles e hilos
        self.run = True
        # Definir las variables de entrada y salida
        self.RWH_angle = ctrl.Antecedent(np.arange(-180, 180, 2), 'RWH_angle')
        self.inDRWH_ang = ctrl.Antecedent(np.arange(-180, 180, 2), 'inDRWH_ang')
        self.Dist_m = ctrl.Antecedent(np.arange(-180, 180, 2), 'Distancia')
        self.ouDRWH_ang = ctrl.Consequent(np.linspace(-10, 10, 180), 'ouDRWH_ang')

        # Asignar los conjuntos difusos a las variables de entrada y salida
        self.RWH_angle['N'] = fuzz.trapmf(self.RWH_angle.universe, [-95, -90, -5, 0])
        self.RWH_angle['P'] = fuzz.trapmf(self.RWH_angle.universe, [0, 5, 90, 95])

        self.inDRWH_ang['Low'] = fuzz.trapmf(self.inDRWH_ang.universe, [-75, -70, 70, 75])
        self.inDRWH_ang['N'] = fuzz.trimf(self.inDRWH_ang.universe, [-180, -180, 0])
        self.inDRWH_ang['Z'] = fuzz.trimf(self.inDRWH_ang.universe, [-180, 0, 180])
        self.inDRWH_ang['P'] = fuzz.trimf(self.inDRWH_ang.universe, [0, 180, 180])

        self.Dist_m['tfL'] = fuzz.trapmf(self.Dist_m.universe, [-70, -70, -45, -40])
        self.Dist_m['tfR'] = fuzz.trapmf(self.Dist_m.universe, [40, 45, 70, 70])

        self.ouDRWH_ang['N'] = fuzz.trimf(self.ouDRWH_ang.universe, [-180, -180, 0])
        self.ouDRWH_ang['TL'] = fuzz.trimf(self.ouDRWH_ang.universe, [-50, -50, -45])
        self.ouDRWH_ang['Z'] = fuzz.trimf(self.ouDRWH_ang.universe, [-180, 0, 180])
        self.ouDRWH_ang['TR'] = fuzz.trimf(self.ouDRWH_ang.universe, [45, 50, 50])
        self.ouDRWH_ang['P'] = fuzz.trimf(self.ouDRWH_ang.universe, [0, 180, 180])

        # Definir las reglas difusas
        self.rule1 = ctrl.Rule(self.inDRWH_ang['N'], self.ouDRWH_ang['N'])
        self.rule2 = ctrl.Rule(self.inDRWH_ang['Z'], self.ouDRWH_ang['Z'])
        self.rule3 = ctrl.Rule(self.inDRWH_ang['P'], self.ouDRWH_ang['P'])
        self.rule4 = ctrl.Rule(self.RWH_angle['N'] & self.inDRWH_ang['Low'] & ~self.Dist_m['tfR'], self.ouDRWH_ang['TL'])
        self.rule5 = ctrl.Rule(self.RWH_angle['P'] & self.inDRWH_ang['Low'] & ~self.Dist_m['tfL'], self.ouDRWH_ang['TR'])
        self.rule6 = ctrl.Rule(self.inDRWH_ang['Low'] & self.Dist_m['tfR'], self.ouDRWH_ang['TR'])
        self.rule7 = ctrl.Rule(self.inDRWH_ang['Low'] & self.Dist_m['tfL'], self.ouDRWH_ang['TL'])

        # Crear el sistema de control difuso
        self.sistema_control = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3, self.rule4, self.rule5,
                                                  self.rule6, self.rule7])
        self.sistema = ctrl.ControlSystemSimulation(self.sistema_control)

    def compute(self, RWH_angle_val, inDRWH_ang_val, Dist_m_val):
        # Asignar valores a las entradas del sistema
        self.sistema.input['RWH_angle'] = RWH_angle_val
        self.sistema.input['inDRWH_ang'] = inDRWH_ang_val
        self.sistema.input['Distancia'] = Dist_m_val

        # Realizar la inferencia
        self.sistema.compute()

        # Obtener el resultado
        return self.sistema.output['ouDRWH_ang']
    
    def close(self):
        self.run = False


class RudderController:
    def __init__(self):
        # Definir las variables de entrada y salida
        self.DHCerr = ctrl.Antecedent(np.arange(-180, 180, 2), 'DHCerror')
        self.DHHerr = ctrl.Antecedent(np.arange(-180, 180, 2), 'DHHerror')
        self.DHHerrAdd = ctrl.Antecedent(np.arange(-180, 180, 2), 'DHHerrAdd')
        self.RWH_angle = ctrl.Antecedent(np.arange(-180, 180, 2), 'RWH_angle')
        self.Rud_angle = ctrl.Consequent(np.linspace(-40, 40, 180), 'Rudder_angle')

        # Asignar los conjuntos difusos a las variables de entrada y salida
        self.DHCerr['SL'] = fuzz.trapmf(self.DHCerr.universe, [-180, -180, -70, -10])
        self.DHCerr['L'] = fuzz.trimf(self.DHCerr.universe, [-90, -40, 0])
        self.DHCerr['M'] = fuzz.trimf(self.DHCerr.universe, [-10, 0, 10])
        self.DHCerr['R'] = fuzz.trimf(self.DHCerr.universe, [0, 40, 90])
        self.DHCerr['SR'] = fuzz.trapmf(self.DHCerr.universe, [10, 70, 180, 180])

        self.DHHerr['SL'] = fuzz.trapmf(self.DHHerr.universe, [-180, -180, -70, -10])
        self.DHHerr['L'] = fuzz.trimf(self.DHHerr.universe, [-90, -40, 0])
        self.DHHerr['M'] = fuzz.trimf(self.DHHerr.universe, [-10, 0, 10])
        self.DHHerr['R'] = fuzz.trimf(self.DHHerr.universe, [0, 40, 90])
        self.DHHerr['SR'] = fuzz.trapmf(self.DHHerr.universe, [10, 70, 180, 180])

        self.DHHerrAdd['NL'] = fuzz.trapmf(self.DHHerrAdd.universe, [-180, -180, -45, -40])
        self.DHHerrAdd['PL'] = fuzz.trapmf(self.DHHerrAdd.universe, [40, 45, 180, 180])

        self.RWH_angle['AW'] = fuzz.trapmf(self.RWH_angle.universe, [-65, -55, 55, 65])

        self.Rud_angle['SL'] = fuzz.trimf(self.Rud_angle.universe, [-40, -40, -20])
        self.Rud_angle['L'] = fuzz.trimf(self.Rud_angle.universe, [-40, -20, 0])
        self.Rud_angle['M'] = fuzz.trimf(self.Rud_angle.universe, [-20, 0, 20])
        self.Rud_angle['R'] = fuzz.trimf(self.Rud_angle.universe, [0, 20, 40])
        self.Rud_angle['SR'] = fuzz.trimf(self.Rud_angle.universe, [20, 40, 40])

        # Definir las reglas difusas
        self.rule1 = ctrl.Rule(self.DHCerr['SL'] & self.RWH_angle['AW'], self.Rud_angle['SL'])
        self.rule2 = ctrl.Rule(self.DHCerr['L'] & self.RWH_angle['AW'], self.Rud_angle['L'])
        self.rule3 = ctrl.Rule(self.DHCerr['M'] & self.RWH_angle['AW'], self.Rud_angle['M'])
        self.rule4 = ctrl.Rule(self.DHCerr['R'] & self.RWH_angle['AW'], self.Rud_angle['R'])
        self.rule5 = ctrl.Rule(self.DHCerr['SR'] & self.RWH_angle['AW'], self.Rud_angle['SR'])
        self.rule6 = ctrl.Rule(self.DHCerr['SL'] & ~self.RWH_angle['AW'], self.Rud_angle['SL'])
        self.rule7 = ctrl.Rule(self.DHCerr['L'] & ~self.RWH_angle['AW'], self.Rud_angle['L'])
        self.rule8 = ctrl.Rule(self.DHCerr['M'] & ~self.RWH_angle['AW'], self.Rud_angle['M'])
        self.rule9 = ctrl.Rule(self.DHCerr['R'] & ~self.RWH_angle['AW'], self.Rud_angle['R'])
        self.rule10 = ctrl.Rule(self.DHCerr['SR'] & ~self.RWH_angle['AW'], self.Rud_angle['SR'])
        self.rule11 = ctrl.Rule(self.DHHerr['SL'] & self.DHHerrAdd['NL'] & ~self.RWH_angle['AW'], self.Rud_angle['SL'])
        self.rule12 = ctrl.Rule(self.DHHerr['L'] & self.DHHerrAdd['NL'] & ~self.RWH_angle['AW'], self.Rud_angle['L'])
        self.rule13 = ctrl.Rule(self.DHHerr['R'] & self.DHHerrAdd['PL'] & ~self.RWH_angle['AW'], self.Rud_angle['R'])
        self.rule14 = ctrl.Rule(self.DHHerr['SR'] & self.DHHerrAdd['PL'] & ~self.RWH_angle['AW'], self.Rud_angle['SR'])

        # Crear el sistema de control difuso
        self.sistema_control = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3, self.rule4,
                                                   self.rule5, self.rule6, self.rule7, self.rule8,
                                                   self.rule9, self.rule10, self.rule11, self.rule12,
                                                   self.rule13, self.rule14])
        self.sistema = ctrl.ControlSystemSimulation(self.sistema_control)

    def compute(self, DHCerror, DHHerror, DHHerrAdd, RWH_angle):
        # Establecer los valores de entrada
        self.sistema.input['DHCerror'] = DHCerror
        self.sistema.input['DHHerror'] = DHHerror
        self.sistema.input['DHHerrAdd'] = DHHerrAdd
        self.sistema.input['RWH_angle'] = RWH_angle

        # Realizar la inferencia
        self.sistema.compute()

        # Obtener el valor de salida
        Rudder_angle = self.sistema.output['Rudder_angle']
        return Rudder_angle


class SailController:
    def __init__(self):
        # Definir las variables de entrada y salida
        self.RWH_angle = ctrl.Antecedent(np.arange(-180, 180, 2), 'RWH_angle')
        self.error = ctrl.Antecedent(np.arange(-180, 180, 2), 'error')
        self.SA_increment = ctrl.Consequent(np.linspace(-10, 10, 180), 'SA_increment')

        # Asignar los conjuntos difusos a las variables de entrada y salida
        self.RWH_angle['NL'] = fuzz.trimf(self.RWH_angle.universe, [-180, -180, -90])
        self.RWH_angle['N'] = fuzz.trimf(self.RWH_angle.universe, [-150, -80, 0])
        self.RWH_angle['Z'] = fuzz.trimf(self.RWH_angle.universe, [-70, 0, 70])
        self.RWH_angle['P'] = fuzz.trimf(self.RWH_angle.universe, [0, 80, 150])
        self.RWH_angle['PL'] = fuzz.trimf(self.RWH_angle.universe, [90, 180, 180])

        self.error['NL'] = fuzz.trapmf(self.error.universe, [-180, -180, -50, -30])
        self.error['N'] = fuzz.trimf(self.error.universe, [-45, -25, 0])
        self.error['Z'] = fuzz.trimf(self.error.universe, [-15, 0, 15])
        self.error['P'] = fuzz.trimf(self.error.universe, [0, 25, 45])
        self.error['PL'] = fuzz.trapmf(self.error.universe, [30, 50, 180, 180])

        self.SA_increment['NL'] = fuzz.trimf(self.SA_increment.universe, [-10, -10, -5])
        self.SA_increment['N'] = fuzz.trimf(self.SA_increment.universe, [-10, -5, 0])
        self.SA_increment['Z'] = fuzz.trimf(self.SA_increment.universe, [-5, 0, 5])
        self.SA_increment['P'] = fuzz.trimf(self.SA_increment.universe, [0, 5, 10])
        self.SA_increment['PL'] = fuzz.trimf(self.SA_increment.universe, [5, 10, 10])

        # Definir las reglas difusas
        self.rule1 = ctrl.Rule(self.RWH_angle['NL'], self.SA_increment['Z'])
        self.rule2 = ctrl.Rule(self.RWH_angle['N'] & self.error['NL'], self.SA_increment['P'])
        self.rule3 = ctrl.Rule(self.RWH_angle['N'] & self.error['N'], self.SA_increment['Z'])
        self.rule4 = ctrl.Rule(self.RWH_angle['N'] & self.error['Z'], self.SA_increment['Z'])
        self.rule5 = ctrl.Rule(self.RWH_angle['N'] & self.error['P'], self.SA_increment['Z'])
        self.rule6 = ctrl.Rule(self.RWH_angle['N'] & self.error['PL'], self.SA_increment['N'])
        self.rule7 = ctrl.Rule(self.RWH_angle['Z'] & self.error['NL'], self.SA_increment['PL'])
        self.rule8 = ctrl.Rule(self.RWH_angle['Z'] & self.error['N'], self.SA_increment['P'])
        self.rule9 = ctrl.Rule(self.RWH_angle['Z'] & self.error['Z'], self.SA_increment['Z'])
        self.rule10 = ctrl.Rule(self.RWH_angle['Z'] & self.error['P'], self.SA_increment['N'])
        self.rule11 = ctrl.Rule(self.RWH_angle['Z'] & self.error['PL'], self.SA_increment['NL'])
        self.rule12 = ctrl.Rule(self.RWH_angle['P'] & self.error['NL'], self.SA_increment['P'])
        self.rule13 = ctrl.Rule(self.RWH_angle['P'] & self.error['N'], self.SA_increment['Z'])
        self.rule14 = ctrl.Rule(self.RWH_angle['P'] & self.error['Z'], self.SA_increment['Z'])
        self.rule15 = ctrl.Rule(self.RWH_angle['P'] & self.error['P'], self.SA_increment['Z'])
        self.rule16 = ctrl.Rule(self.RWH_angle['P'] & self.error['PL'], self.SA_increment['N'])
        self.rule17 = ctrl.Rule(self.RWH_angle['PL'], self.SA_increment['Z'])

        # Crear el sistema de control difuso
        self.sistema_control = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3, self.rule4,
                                                   self.rule5, self.rule6, self.rule7, self.rule8,
                                                   self.rule9, self.rule10, self.rule11, self.rule12,
                                                   self.rule13, self.rule14, self.rule15, self.rule16,
                                                   self.rule17])
        self.sistema = ctrl.ControlSystemSimulation(self.sistema_control)

    def compute(self, RWH_angle, error):
        # Establecer los valores de entrada
        self.sistema.input['RWH_angle'] = RWH_angle
        self.sistema.input['error'] = error

        # Realizar la inferencia
        self.sistema.compute()

        # Obtener el valor de salida
        SA_increment = self.sistema.output['SA_increment']
        return SA_increment
