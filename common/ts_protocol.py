"""Serialização binária para TelemetryStream (TCP)"""

import struct

TS_LENGTH = 35 #(bytes)

ROVER_STATE = { #Códigos para serializar os estados do rover
    'M' : 'ON_MISSION',
    'c' : 'ON_THE_WAY',
    'I' : 'IDLE',
    'E' : 'ERROR'
}

def get_state_code(state_name: str):
    for code, data in ROVER_STATE.items():
        if data == state_name:
            return code
    return None

def get_state_name(state_name: str):
    return ROVER_STATE.get(state_name, 'UNKNOWN')

class SerializationException(Exception):
    pass

class TSMessage:

    def __init__(self, rover_id, position, planet, state, power_level, orientation, temperature, speed, direction):
        self.rover_id = rover_id
        self.position = position
        self.planet = planet
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
        res += self.planet.encode('utf-8')
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

        rover_id = data[0:4].decode('utf-8').rstrip('\0')

        pos_dist = struct.unpack('>f', data[4:8])[0]
        pos_bearing = struct.unpack('>f', data[8:12])[0]
        position = [pos_dist, pos_bearing]

        planet = data[12:13].decode('utf-8').rstrip('\0')
        power_level = int.from_bytes(data[13:14], 'big')

        orient_azimuth = struct.unpack('>f', data[14:18])[0]
        orient_elevation = struct.unpack('>f', data[18:22])[0]
        orientation = [orient_azimuth, orient_elevation]

        temperature = struct.unpack('>f', data[22:26])[0]
        speed = struct.unpack('>f', data[26:30])[0]
        direction = struct.unpack('>f', data[30:34])[0]

        state_code = data[34:].decode('utf-8') 
        state = get_state_name(state_code)
        if(state == 'UNKNOWN'):
            raise SerializationException('Invalid state')

        return cls(rover_id, position, planet, power_level, orientation, temperature, speed, direction, state)