import time
import math
from typing import List, Tuple

class RoverTelemetry:
    
    def __init__(self, rover_id: str, planet: str = '1'):
        self.rover_id = rover_id
        self.planet = planet
        
        # Estado inicial
        self.position = [0.0, 0.0]  # [distance_from_base, bearing] em km e graus
        self.speed = 0.0  # km/h
        self.direction = 0.0  # graus (0=Norte, 90=Este)
        self.power_level = '100'  # 0-100%
        self.temperature = 20.0  # °C
        self.operational_state = 'IDLE'
        
        # Painéis solares
        self.solar_orientation = [0.0, 0.0]  # [azimuth, elevation] em graus
        
        # Missão atual
        # self.current_mission = None
        # self.mission_start_time = None
        # self.waypoints = []  # Lista de waypoints para a missão atual
        # self.current_waypoint_index = 0
        
    def get_current_telemetry(self) -> dict:
        return {
            'rover_id' : self.rover_id,
            'planet' : self.planet,
            'position': self.position.copy(),
            'state': self.operational_state,
            'power_level': self.power_level,
            'orientation': self.solar_orientation.copy(),
            'temperature': self.temperature,
            'speed': self.speed,
            'direction': self.direction
        }