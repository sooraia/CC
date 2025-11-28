import socket
import threading
import time
from common.ts_protocol import TS_LENGTH, TSMessage
from rover.telemetry import RoverTelemetry

class TelemetrySystemClient:

    def __init__(self, rover_telemetry: RoverTelemetry, telemetry_interval: int, host: str, port: int = 0):
        self.host = host
        self.port = port
        
        self.rover_telemetry = rover_telemetry
        self.telemetry_interval = telemetry_interval
        self.connected = False
        
    def connect(self, server_host: str, server_port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.connect((server_host, server_port))
        
        self.connected_addr = server_host
        self.connected_port = server_port
        self.connected = True
        print("Connected to " + server_host + ":" + str(server_port))

    def send_telemetry_stream(self):
        while self.connected:
            self._send_telemetry()
            time.sleep(self.telemetry_interval)
    
    def _send_telemetry(self):
        telemetry_dict = self.rover_telemetry.get_current_telemetry()
        message = TSMessage(
            rover_id=telemetry_dict['rover_id'],
            position=telemetry_dict['position'],
            state=telemetry_dict['state'],
            power_level=telemetry_dict['power_level'],
            orientation=telemetry_dict['orientation'],
            temperature=telemetry_dict['temperature'],
            speed=telemetry_dict['speed'],
            direction=telemetry_dict['direction'])
        #message.print_telemetry()
        data = message.serialize_telemetry()
        self.socket.send(data)

    def send(self, data: bytes):
        if self.connected:
            self.socket.sendall(data)

    def close(self):
        self.connected = False
        if self.socket:
            self.socket.close()
            self.socket = None