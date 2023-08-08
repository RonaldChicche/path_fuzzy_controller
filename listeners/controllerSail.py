import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl



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

        self.SA_increment['NL'] = fuzz.trimf(self.SA_increment.universe, [-20, -20, -10])
        self.SA_increment['N'] = fuzz.trimf(self.SA_increment.universe, [-20, -10, 0])
        self.SA_increment['Z'] = fuzz.trimf(self.SA_increment.universe, [-10, 0, 10])
        self.SA_increment['P'] = fuzz.trimf(self.SA_increment.universe, [0, 10, 20])
        self.SA_increment['PL'] = fuzz.trimf(self.SA_increment.universe, [10, 20, 20])

        # Definir las reglas difusas
        #self.rule1 = ctrl.Rule(self.RWH_angle['NL'], self.SA_increment['Z'])
        self.rule1_1 = ctrl.Rule(self.RWH_angle['NL'] & self.error['NL'], self.SA_increment['NL'])
        self.rule1_2 = ctrl.Rule(self.RWH_angle['NL'] & self.error['N'], self.SA_increment['N'])
        self.rule1_3 = ctrl.Rule(self.RWH_angle['NL'] & self.error['Z'], self.SA_increment['Z'])
        self.rule1_4 = ctrl.Rule(self.RWH_angle['NL'] & self.error['P'], self.SA_increment['P'])
        self.rule1_5 = ctrl.Rule(self.RWH_angle['NL'] & self.error['PL'], self.SA_increment['PL'])
        # ---------
        self.rule2 = ctrl.Rule(self.RWH_angle['N'] & self.error['NL'], self.SA_increment['Z'])
        self.rule3 = ctrl.Rule(self.RWH_angle['N'] & self.error['N'], self.SA_increment['N'])
        self.rule4 = ctrl.Rule(self.RWH_angle['N'] & self.error['Z'], self.SA_increment['NL'])
        self.rule5 = ctrl.Rule(self.RWH_angle['N'] & self.error['P'], self.SA_increment['PL'])
        self.rule6 = ctrl.Rule(self.RWH_angle['N'] & self.error['PL'], self.SA_increment['P'])
        #-----
        self.rule7 = ctrl.Rule(self.RWH_angle['Z'] & self.error['NL'], self.SA_increment['PL'])
        self.rule8 = ctrl.Rule(self.RWH_angle['Z'] & self.error['N'], self.SA_increment['P'])
        self.rule9 = ctrl.Rule(self.RWH_angle['Z'] & self.error['Z'], self.SA_increment['Z'])
        self.rule10 = ctrl.Rule(self.RWH_angle['Z'] & self.error['P'], self.SA_increment['N'])
        self.rule11 = ctrl.Rule(self.RWH_angle['Z'] & self.error['PL'], self.SA_increment['NL'])
        #------
        self.rule12 = ctrl.Rule(self.RWH_angle['P'] & self.error['NL'], self.SA_increment['N'])
        self.rule13 = ctrl.Rule(self.RWH_angle['P'] & self.error['N'], self.SA_increment['NL'])
        self.rule14 = ctrl.Rule(self.RWH_angle['P'] & self.error['Z'], self.SA_increment['PL'])
        self.rule15 = ctrl.Rule(self.RWH_angle['P'] & self.error['P'], self.SA_increment['P'])
        self.rule16 = ctrl.Rule(self.RWH_angle['P'] & self.error['PL'], self.SA_increment['Z'])
        # -----------
        self.rule2_1 = ctrl.Rule(self.RWH_angle['PL'] & self.error['NL'], self.SA_increment['NL'])
        self.rule2_2 = ctrl.Rule(self.RWH_angle['PL'] & self.error['N'], self.SA_increment['N'])
        self.rule2_3 = ctrl.Rule(self.RWH_angle['PL'] & self.error['Z'], self.SA_increment['Z'])
        self.rule2_4 = ctrl.Rule(self.RWH_angle['PL'] & self.error['P'], self.SA_increment['P'])
        self.rule2_5 = ctrl.Rule(self.RWH_angle['PL'] & self.error['PL'], self.SA_increment['PL'])

        # Crear el sistema de control difuso
        self.sistema_control = ctrl.ControlSystem([self.rule1_1, self.rule1_2, self.rule1_3, self.rule1_4, self.rule1_5, 
                                                   self.rule2, self.rule3, self.rule4,
                                                   self.rule5, self.rule6, self.rule7, self.rule8,
                                                   self.rule9, self.rule10, self.rule11, self.rule12,
                                                   self.rule13, self.rule14, self.rule15, self.rule16,
                                                   self.rule2_1, self.rule2_2, self.rule2_3, self.rule2_4, self.rule2_5])
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
