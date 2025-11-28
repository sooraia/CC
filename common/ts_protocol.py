"""Serialização binária para TelemetryStream (TCP)"""

import struct

TS_LENGTH = 36 #(bytes)

ROVER_STATE = { #Códigos para serializar os estados do rover
    'M' : 'ON_MISSION',
    'c' : 'ON_THE_WAY', # a caminho ??
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

    def __init__(self, rover_id, position, state, power_level, orientation, temperature, speed, direction):
        self.rover_id = rover_id
        self.position = position
        self.state = state
        self.power_level = power_level
        self.orientation = orientation
        self.temperature = temperature
        self.speed = speed 
        self.direction = direction
 
    def serialize_telemetry(self):

        res = self.rover_id.encode('utf-8')
        res += struct.pack('>f', self.position[0])
        res += struct.pack('>f', self.position[1])
        res += self.power_level.encode('utf-8') #000-100 3 bytes
        res += struct.pack('>f', self.orientation[0]) 
        res += struct.pack('>f', self.orientation[1])
        res += struct.pack('>f', self.temperature)
        res += struct.pack('>f', self.speed)
        res += struct.pack('>f', self.direction)

        state_code = get_state_code(self.state)
        if(state_code is None):
            raise SerializationException('Invalid state')
        
        res += state_code.encode('utf-8')

        return res

    @classmethod
    def deserialize_telemetry(cls, data):
        if len(data) != TS_LENGTH:
            raise SerializationException(f'Invalid data length: {len(data)} bytes, expected 36')
        
        rover_id = data[0:4].decode('utf-8')

        pos_dist = struct.unpack('>f', data[4:8])[0]
        pos_bearing = struct.unpack('>f', data[8:12])[0]
        position = [pos_dist, pos_bearing]

        power_level = data[12:15].decode('utf-8')

        orient_x = struct.unpack('>f', data[15:19])[0]
        orient_y = struct.unpack('>f', data[19:23])[0]
        orientation = [orient_x, orient_y]
        
        temperature = struct.unpack('>f', data[23:27])[0]
        speed = struct.unpack('>f', data[27:31])[0]
        direction = struct.unpack('>f', data[31:35])[0]
        
        state_code = data[35:36].decode('utf-8')
        state = get_state_name(state_code)
        if state == 'UNKNOWN':
            raise SerializationException('Invalid state')
        
        return cls(rover_id, position, state, power_level, orientation, temperature, speed, direction)
    
    def print_telemetry(self):
        print(f'Rover ID: {self.rover_id}')
        print(f'Position: [ {self.position[0]}, Bearing {self.position[1]} ]')
        print(f'State: {self.state}')
        print(f'Power Level: {self.power_level} %')
        print(f'Orientation: Azimuth {self.orientation[0]} degrees, Elevation {self.orientation[1]} degrees')
        print(f'Temperature: {self.temperature} °C')
        print(f'Speed: {self.speed} km/h')
        print(f'Direction: {self.direction} degrees')
