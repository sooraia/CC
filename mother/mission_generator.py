import math
import random
import threading
import time
from common.mission_types import MISSION_TYPES

class MissionGenerator:
    def __init__(self):
        self.mission_counter = 0
        self.counter_lock = threading.Lock()

    def get_mission_id(self):
        with self.counter_lock:
            self.mission_counter += 1
            return f"M-{self.mission_counter:03d}"  # capped a 999 missões
            
    def generate_random_mission(self, mission_id, rover_telemetry, mission_codes):
        mission_codes_list = list(mission_codes)
        task = mission_codes_list[random.randrange(0, len(mission_codes_list))]

        rover_x = rover_telemetry['position'][0]
        rover_y = rover_telemetry['position'][1]

        angulo = random.uniform(0, 2 * math.pi)
        distancia = random.uniform(0, 5) # área gerada aleatoriamente limitada a uma distância de 5km da sua posição atual

        area_x = rover_x + distancia * math.cos(angulo)
        area_y = rover_y + distancia * math.sin(angulo)

        area = [ #500x500m
            [area_x - 0.5, area_y - 0.5],
            [area_x + 0.5, area_y + 0.5]
        ]

        task_param = None
        if MISSION_TYPES[task].get('param'):
            param_keys = list(MISSION_TYPES[task]['param'].keys())
            task_param_idx = random.randrange(0, len(param_keys))
            task_param = param_keys[task_param_idx]

        duration = random.randrange(60, 190) # 5 a 60 minutos
        update_interval = random.randrange(20, 30)

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