import random
import time
import math
from typing import List, Tuple
from common.mission_types import MISSION_TYPES, get_mission_by_name, get_event_name, get_mission_name, get_param_name
speed_limit = 5 #200 m/h

class RoverTelemetry:
    
    def __init__(self, rover_id: str):
        self.rover_id = rover_id
        
        # Estado inicial
        self.position = [0.0, 0.0]  # coordenadas cartesianas - distância à base
        self.speed = 0.0  # km/h
        self.direction = 0.0  # graus (0=Norte, 90=Este)
        self.power_level = '100'  # 0-100%
        self.temperature = 20.0  # °C
        self.operational_state = 'IDLE'
        self.solar_orientation = [0.0, 0.0] 
        
        #Missão atual
        self.current_mission = None
        self.mission_start_time = None
        self.mission_progress = 0
        self.mission_status = ''

    def reset_mission_paramaters(self):
        self.current_mission = None 
        self.mission_start_time = None
        self.mission_progress = 0
        self.mission_status = '' 
        
    def get_current_telemetry(self) -> dict:
        return {
            'rover_id' : self.rover_id,
            'position': self.position.copy(),
            'state': self.operational_state,
            'power_level': self.power_level,
            'orientation': self.solar_orientation.copy(),
            'temperature': self.temperature,
            'speed': self.speed,
            'direction': self.direction
        }
    
    def go_to_pos(self, target):
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx**2 + dy**2)  # distância ao target
        direction = math.degrees(math.atan2(dy, dx))  # redirecionar rover para target
        if distance == 0:
            return
        
        self.speed = speed_limit
        self.direction = direction
    
        travel_time = (distance / self.speed) * 3600  # segundos

        # movimento linear
        start_time = time.time()
        start_x, start_y = self.position[0], self.position[1]
        
        while time.time() - start_time < travel_time:
            progress = min(1.0, (time.time() - start_time) / travel_time)
            
            # Interpolação linear entre posição inicial e final
            self.position[0] = start_x + (dx * progress)
            self.position[1] = start_y + (dy * progress)
            
            # Painéis solares seguem a direção do movimento
            self.solar_orientation = [direction, 45.0]
            
            # Consumo de energia proporcional à distância percorrida
            power_used = int(progress * 15)  # 15% da bateria para viagem total
            self.power_level = str(max(0, 100 - power_used)).zfill(3)
            
            time.sleep(1)
    
        # Chegou ao destino
        self.position = [target[0], target[1]]
        self.speed = 0.0

    def go_to_area(self, area : list):
        # Vai para o centro da área
        avg_distance = sum(pos[0] for pos in area) / 2
        avg_bearing = sum(pos[1] for pos in area) / 2
        target_position = [avg_distance, avg_bearing]

        self.go_to_pos(self, target_position)


    def execute_current_mission(self):
        mission_config = MISSION_TYPES[self.mission.task]
        mission_events = mission_config['events']
        duration = self.mission.duration
        start_time = time.time()
        
        event_sequence = [
            ('1', 25),  # evento 1 aos 25%
            ('2', 50),  # evento 2 aos 50%
            ('3', 75),  # """ 3 aos 75%
            ('4', -1)   # """ 4 (erro) - aleatório
        ]
        
        completed = set()
        
        while time.time() - start_time < duration and self.mission_progress < 100:
            elapsed = time.time() - start_time
            self.mission_progress = min(95, (elapsed / duration) * 100)
            
            for event, event_progress in event_sequence:
                if event in completed:
                    continue
                    
                if event == '4':  # (erro -> 5% de chances de ser triggered)
                    if random.random() < 0.05: 
                        self.mission_status = mission_events[event]
                        self.mission_progress = 100
                        print(f"Debug: erro: {self.mission_status}")
                        return
                elif self.mission_progress >= event_progress:
                    self.mission_status = mission_events[event]
                    completed.add(event)
                    print(f"Debug: {self.mission_progress}%: {self.mission_status}")
            
            time.sleep(1)
        
            print(f"🎯 MISSÃO CONCLUÍDA: 100%")