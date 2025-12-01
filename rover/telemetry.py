import random
import threading
import time
import math
from typing import List, Tuple
from common.mission_types import MISSION_TYPES, get_mission_by_name, get_event_name, get_mission_name, get_param_name
from common.__init__ import MAX_X, MAX_Y, MIN_X, MIN_Y

speed_limit = 10000 #200 m/h

class RoverTelemetry:
    
    def __init__(self, rover_id: str):
        self.rover_id = rover_id
        
        # Estado inicial
        self.position = [
            random.uniform(MIN_X, MAX_X),
            random.uniform(MIN_Y, MAX_Y)
        ]
        self.speed = 0.0  # km/h
        self.direction = 0.0  # graus (0==Norte)
        self.power_level = 100  # 0-100%
        self.operational_state = 'IDLE'
        self._update_temperature(time.time())
        self._optimize_solar_orientation(time.time())
        
        #Missão atual
        self.reset_mission_paramaters()

        self.lock = threading.Lock() #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    def add_mission(self, mission_id: str, area: list, task: str, task_param: str, duration: int, update_interval: int):
        self.current_mission_id = mission_id
        self.current_mission_area = area
        self.current_mission_task = task
        self.current_mission_task_param = task_param
        self.current_mission_duration = duration
        self.current_mission_update_interval = update_interval
        self.current_mission_progress = 0

    def reset_mission_paramaters(self):
        self.operational_state = 'IDLE'
        self.current_mission_id = None
        self.current_mission_area = None
        self.current_mission_task = None
        self.current_mission_task_param = None
        self.current_mission_duration = 0
        self.current_mission_update_interval = 0
        self.current_mission_start_time = None
        self.current_mission_progress = 0
        self.current_mission_status = ''
        
    def get_current_telemetry(self) -> dict:
        return {
            'rover_id' : self.rover_id,
            'position': [round(self.position[0], 2), round(self.position[1], 2)],
            'state': self.operational_state,
            'power_level': round(self.power_level,2),
            'orientation': [round(self.solar_orientation[0], 2), round(self.solar_orientation[1], 2)],
            'ext_temperature': round(self.ext_temperature,2),
            'int_temperature': round(self.int_temperature,2),
            'speed': round(self.speed, 2),
            'direction': round(self.direction,2)
        }
    
    def update_telemetry_loop(self):
        last_update = time.time()
        
        while True:
            current_time = time.time()
            time_dif = current_time - last_update
            last_update = current_time
            
            with self.lock:
                self._update_temperature(current_time)
                self._update_power_level(time_dif, current_time)
                if self.operational_state == 'IDLE':
                    self._optimize_solar_orientation(current_time)
                
            time.sleep(1)

    def _update_temperature(self, current_time):
        hour_of_day = (current_time % 86400) / 3600  # 0-23 horas
        base_temp = 10 + 19 * math.sin((hour_of_day - 6) * math.pi / 12)
        variation = random.uniform(-0.5, 0.5)
        self.ext_temperature = base_temp + variation

        if self.operational_state == 'ACTIVE':
            internal = self.ext_temperature + 15.0
        elif self.speed > 0:
            internal = self.ext_temperature + 8.0
        elif self.operational_state == 'IDLE':
            internal = self.ext_temperature + 5.0

        self.int_temperature = internal

    def _calculate_sun_position(self, current_time):
        hour = (current_time % 86400) / 3600  # 0-23 horas
        sun_direction = (hour / 24) * 360  # 0° a 360°
        
        sun_elevation = 90 * math.sin(math.radians((hour - 6) * 15))  # 6h=0°, 12h=90°, 18h=0°
        sun_elevation = max(0, min(90, sun_elevation))  # Limitar entre 0-90°
        return sun_direction, sun_elevation

    def _panel_efficiency(self, current_time):
        sun_direction, sun_elevation = self._calculate_sun_position(current_time)
        
        if sun_elevation <= 0: #(noite)
            return 0.0
        
        direction_diff = abs(self.solar_orientation[0] - sun_direction)
        direction_diff = min(direction_diff, 360 - direction_diff)
        direction_efficiency = 1.0 - (direction_diff / 180.0)
        
        tilt_diff = abs(self.solar_orientation[1] - sun_elevation) #eficiência da inclinação
        tilt_efficiency = 1.0 - (tilt_diff / 90.0)
        
        solar_intensity = sun_elevation / 90.0 #intensidade segundo a elevação
        
        efficiency = direction_efficiency * tilt_efficiency * solar_intensity
        return max(0.0, efficiency)

    def _update_power_level(self, delta_time, current_time):
        current_power = int(self.power_level)
        base_consumption = 0.5  # %/min
        
        if self.operational_state == 'ACTIVE': #consumo maior quando active
            state_consumption = 2.0
        elif self.speed > 0:
            state_consumption = 1.5 + (self.speed / speed_limit) * 1.0
        else:
            state_consumption = 0.5
        
        solar_efficiency= self._panel_efficiency(current_time)
        solar_generation= solar_efficiency *3.0  #% /min
        
        dif = (base_consumption + state_consumption -solar_generation) *(delta_time/60)
        power = max(0, min(100, current_power -dif))
        
        self.power_level = int(power)
        
    def _optimize_solar_orientation(self, current_time):
        sun_direction, sun_elevation = self._calculate_sun_position(current_time)
        self.direction = sun_direction
        self.solar_orientation = [sun_direction, sun_elevation]

    def go_to_pos(self, target):
        target[0] = max(MIN_X , min(MAX_X, target[0]))
        target[1] = max(MIN_Y, min(MAX_Y, target[1]))

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
            
            self.position[0] = start_x + (dx * progress)
            self.position[1] = start_y + (dy * progress)
            
            # Painéis solares
            self.solar_orientation = [direction, 45.0]
            
            # consumo de energia proporcional à distância percorrida
            power_used = int(progress * 15)  # 15% da bateria para viagem total
            self.power_level = max(0, 100 - power_used)
            
            time.sleep(1)
    
        self.position = [target[0], target[1]]
        self.speed = 0.0
        print(f"Arrived at position: {self.position}")

    def go_to_area(self, area : list):
        # Vai para o centro da área
        avg_distance = sum(pos[0] for pos in area) / 2
        avg_bearing = sum(pos[1] for pos in area) / 2
        target_position = [avg_distance, avg_bearing]

        self.go_to_pos(target_position)

    
    def execute_current_mission(self):
        mission_config = MISSION_TYPES[self.current_mission_task]
        mission_events = mission_config['events']
        duration = self.current_mission_duration
        self.current_mission_start_time = time.time()
        
        event_sequence = [
            ('1', 0),  # evento 1 ao iniciar
            ('2', 50),  # evento 2 aos 50%
            ('3', 100),  # """ 3 aos 100%
            ('4', -1)   # """ 4 (erro) - aleatório
        ]
        
        completed = set()
        
        while time.time() - self.current_mission_start_time < duration and self.current_mission_progress < 100:
            elapsed = time.time() - self.current_mission_start_time
            self.current_mission_progress = int((elapsed / duration) * 100)
            
            for event, event_progress in event_sequence:
                if event in completed:
                    continue
                    
                if event == '4':  # (erro -> 5% de chances de ser triggered durante toda a missão)
                    prob = 1 - (1 - 0.05) ** (1 / duration)
                    if random.random() < prob:
                        self.current_mission_status = event
                        self.current_mission_progress = 100
                        self.operational_state = 'IDLE'
                        print(f"debug: erro: {self.current_mission_status}")
                        return
                elif self.current_mission_progress >= event_progress:
                    self.current_mission_status = event
                    completed.add(event)
                    print(f"debug: {self.current_mission_progress}%: {self.current_mission_status}")
            
            time.sleep(1)
            
        self.current_mission_progress = 100
        self.current_mission_status = '3'  # missão concluída
        print(f"mission completed")