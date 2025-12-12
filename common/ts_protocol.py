import struct

TS_LENGTH = 38 #(bytes)

ROVER_STATE = { #Códigos para serializar os estados do rover
    'A' : 'ACTIVE',
    'W' : 'ON_THE_WAY',
    'I' : 'IDLE',
    'E' : 'ERROR'
}

def get_state_code(state_name: str):
    for code, data in ROVER_STATE.items():
        if data == state_name:
            return code
    return None

def get_state_name(state_code: str):
    return ROVER_STATE.get(state_code, 'UNKNOWN')

class SerializationException(Exception):
    pass

class TSMessage:

    def __init__(self, rover_id, position, state, power_level, orientation, ext_temperature, int_temperature, speed, direction):
        self.rover_id = rover_id
        self.position = position
        self.state = state
        self.power_level = str(int(power_level)).zfill(3)
        self.orientation = orientation
        self.ext_temperature = ext_temperature
        self.int_temperature = int_temperature
        self.speed = speed 
        self.direction = direction
 
    def serialize_telemetry(self):
        if len(self.rover_id) < 4:
            rover_id_number = "00" 
        else:
            rover_id_number = self.rover_id[2:4]
        res =rover_id_number.encode("utf-8")
        
        res += struct.pack('>f', round(self.position[0], 2))
        res += struct.pack('>f', round(self.position[1], 2))
        res += self.power_level.encode('utf-8')  # 000-100 3 bytes
        
        res += struct.pack('>f', round(self.orientation[0], 2)) 
        res += struct.pack('>f', round(self.orientation[1], 2))
        res += struct.pack('>f', round(self.ext_temperature, 2))
        res += struct.pack('>f', round(self.int_temperature, 2))
        res += struct.pack('>f', round(self.speed, 2))
        res += struct.pack('>f', round(self.direction, 2))

        state_code = get_state_code(self.state)
        if state_code is None:
            raise SerializationException('Invalid state')
        
        res += state_code.encode('utf-8')
        return res

    @classmethod
    def deserialize_telemetry(cls, data):
        if len(data) != TS_LENGTH:
            raise SerializationException(f'Invalid data length: {len(data)} bytes, expected 36')
        
        rover_id_number = data[0:2].decode('utf-8')
        rover_id = 'R-' + rover_id_number

        pos_x = round(struct.unpack('>f', data[2:6])[0], 2)
        pos_y = round(struct.unpack('>f', data[6:10])[0], 2) 
        position = [pos_x, pos_y]

        power_level = data[10:13].decode('utf-8')

        orient_x = round(struct.unpack('>f', data[13:17])[0], 2)
        orient_y = round(struct.unpack('>f', data[17:21])[0], 2)
        orientation = [orient_x, orient_y]
        
        ext_temperature = round(struct.unpack('>f', data[21:25])[0], 2) 
        int_temperature = round(struct.unpack('>f', data[25:29])[0], 2) 
        
        speed = round(struct.unpack('>f', data[29:33])[0], 2)
        direction = round(struct.unpack('>f', data[33:37])[0], 2)
        
        state_code = data[37:38].decode('utf-8')
        state = get_state_name(state_code)
        if state == 'UNKNOWN':
            raise SerializationException('Invalid state')
        
        return cls(rover_id, position, state, power_level, orientation, ext_temperature, int_temperature, speed, direction)
    
    def print_telemetry(self):
        print(f'Rover ID: {self.rover_id}')
        print(f'Position: ({self.position[0]}, {self.position[1]})')
        print(f'State: {self.state}')
        print(f'Power Level: {self.power_level} %')
        print(f'Solar Orientation: ({self.orientation[0]}, {self.orientation[1]})')
        print(f'External Temperature: {self.ext_temperature} °C')
        print(f'Internal Temperature: {self.int_temperature} °C')
        print(f'Speed: {self.speed} km/h')
        print(f'Direction: {self.direction}º')
