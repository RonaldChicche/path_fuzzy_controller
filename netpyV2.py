import serial

class SerialPort(serial.Serial):
    def __init__(self, port, baudrate, name="SERIAL"):
        super().__init__(port, 
                         baudrate,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS,
                         timeout=1)
        self.name = name
        self.trama = ''
    
    def hear(self):
        if self.in_waiting > 0:
            self.trama = self.readline()
            #print(self.trama)
            return self.trama
        return None
  
    
    def receive_state_variables(self):
        if self.is_open:
            data = ""
            while True:
                byte = self.read()
                #print(byte)
                if byte:
                    char = byte.decode('utf-8')
                    if char == '/':
                        data += char
                        if data.endswith('//'):
                            self.trama = data
                            break
                    else:
                        data += char

    def send_state_variables(self, state_variables, console=True):
        if isinstance(state_variables, dict):  # Verificar si es un diccionario
            trama = '/'.join([str(x) for x in state_variables.values()])
            trama = trama + '//'
        elif isinstance(state_variables, str):  # Verificar si es una cadena
            trama = state_variables
        else:
            raise ValueError("Invalid input format. Use a dictionary or a string.")

        if console: 
            print('SENDED -> ', trama)
        self.write(trama.encode())

    def close_port(self):
        if self.is_open:
            self.close()
            print('PORT CLOSED ->', self.name)