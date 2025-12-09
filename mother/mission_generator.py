import json
import math
import random
import threading
import time
from common.mission_types import MISSION_TYPES
from common.__init__ import MAX_X, MAX_Y, MIN_X, MIN_Y

class MissionGenerator:
    def __init__(self):
        self.mission_counter = 0
        self.counter_lock = threading.Lock()
        
        if self.load_config() == False:
            self.min_distance = 0 # valores default
            self.max_distance = 5
            self.min_duration = 60
            self.max_duration = 190
            self.min_update_interval = 20
            self.max_update_interval = 30


    def load_config(self):
        with open('config/mission_paramaters.json', 'r') as f:
            config = json.load(f)
        if not config:
            return False
        else:
            self.min_distance = config["min distance (km)"]
            self.max_distance = config["max distance (km)"]
            self.min_duration = config["min duration (s)"]
            self.max_duration = config["max duration (s)"]
            self.min_update_interval = config["min update interval (s)"]
            self.max_update_interval = config["max update interval (s)"]
            return True

    def get_mission_id(self):
        with self.counter_lock:
            self.mission_counter += 1
            return f"M-{self.mission_counter:03d}"  # capped a 999 missões
            
    def generate_random_mission(self, mission_id, rover_telemetry, mission_codes):
        mission_codes_list = list(mission_codes)
        task = mission_codes_list[random.randrange(0, len(mission_codes_list))]

        if rover_telemetry is None:
            rover_x = random.uniform(MIN_X, MAX_X)
            rover_y = random.uniform(MIN_Y, MAX_Y)
        else:
            rover_x = rover_telemetry['position'][0]
            rover_y = rover_telemetry['position'][1]

        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(self.min_distance, self.max_distance) # área gerada aleatoriamente e limitada a uma distância de x km da sua posição atual

        area_x = max(MIN_X + 0.5, min(MAX_X - 0.5,rover_x + distancia * math.cos(angulo)))
        area_y = max(MIN_Y + 0.5, min(MAX_Y - 0.5, rover_y + distancia * math.sin(angulo)))

        area = [[round(max(MIN_X, area_x-0.5),2), round(max(MIN_Y, area_y-0.5),2)],
            [round(min(MAX_X, area_x +0.5),2), round(min(MAX_Y, area_y+ 0.5),2)]]
        
        task_param = None
        if MISSION_TYPES[task].get('param'):
            param_keys = list(MISSION_TYPES[task]['param'].keys())
            task_param_idx = random.randrange(0, len(param_keys))
            task_param = param_keys[task_param_idx]

        duration = int(random.uniform(self.min_duration, self.max_duration))
        update_interval = int(random.uniform(self.min_update_interval, self.max_update_interval))

        return {
            'mission_id': mission_id,
            'area': area,
            'task': task,
            'task_param': task_param,
            'duration': duration,
            'update_interval': update_interval
        }

    def get_mission(self, database, rover_id):
        rover_telemetry = database.get_rover_telemetry(rover_id)
        mission_codes = MISSION_TYPES.keys()
        mission_id = self.get_mission_id()

        if rover_telemetry and rover_telemetry['state'] == 'ERROR':
            mission_idx = 'A' # diagnóstico caso o rover esteja em caso de erro
            return {
                'mission_id': mission_id,
                'area': [rover_telemetry['position'], rover_telemetry['position']],
                'task': mission_idx,
                'task_param': None,
                'duration': 300,
                'update_interval': 120
            }
        else: 
            return self.generate_random_mission(mission_id, rover_telemetry, mission_codes)