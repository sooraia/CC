"""Serialização binária para TelemetryStream (TCP)"""

import struct

def serialize_telemetry(rover_id, position, planet, state, power_level, orientation, temperature, speed, direction):

    res = rover_id.encode('utf-8').ljust(5, b'\0') # é preciso levar em conta o alinhamento de bytes?
    res += struct.pack('>f', position[0])          # not sure se é suposto usar este package, mas pytho não tem nenhum método para converter floats em bytes
    res += struct.pack('>f', position[1])
    res += planet.encode('utf-8').ljust(1, b'\0')
    res += power_level.encode('utf-8').ljust(3, b'\0') #000-100%
    res += struct.pack('>f', orientation[0]) 
    res += struct.pack('>f', orientation[1])
    res += struct.pack('>f', temperature)
    res += struct.pack('>f', speed)
    res += struct.pack('>f', direction)

    res += state.encode('utf-8') # tamanho variavél (last element)

    return res

def deserialize_telemetry(data):

    rover_id = data[0:4].decode('utf-8').rstrip('\0')
    pos_dist = struct.unpack('>f', data[4:8])[0]
    pos_bearing = struct.unpack('>f', data[8:12])[0]
    planet = data[12:13].decode('utf-8').rstrip('\0')
    power_level = int.from_bytes(data[13:14], 'big')
    orient_azimuth = struct.unpack('>f', data[14:18])[0]
    orient_elevation = struct.unpack('>f', data[18:22])[0]
    temperature = struct.unpack('>f', data[22:26])[0]
    speed = struct.unpack('>f', data[26:30])[0]
    direction = struct.unpack('>f', data[30:34])[0]

    state = data[34:].decode('utf-8')  # do byte 34 até ao fim

    return {
        'rover_id': rover_id,
        'position': {'distance': pos_dist, 'bearing': pos_bearing},
        'planet': planet,
        'power_level': power_level,
        'orientation': {'azimuth': orient_azimuth, 'elevation': orient_elevation},
        'temperature': temperature,
        'speed': speed,
        'direction': direction,
        'state': state  # tamanho variável
    }