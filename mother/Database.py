import time
import threading
from common.mission_types import get_mission_name, get_param_name, get_event_name
from common.ml_protocol import MLMission

class Database:
    dados : dict
    quantos : int
    lock : threading.Lock


    def __init__(self):
        self.dados = {
            "rovers": {},#rover_id >> state
            "last_telemetries": {}, # rover_id ->> telemetry_dict
            "missions": {} # mission_id >> mission_dict,
        }
        self.quantos = 0
        self.lock = threading.Lock()
    
    def insere(self, mensagem : str):
        try:
            self.lock.acquire()
            self.quantos += 1
            self.dados[mensagem] = self.quantos
        finally:
            self.lock.release()

    def apaga(self, mensagem : str):
        if mensagem in self.dados:
            self.dados.pop(mensagem)
            self.quantos -= 1

    def show(self):
       
        try:
            self.lock.acquire()
            novo = dict(self.dados)   
        finally:
            self.lock.release()

        for mensagem, quantos in novo.items():
            print(f"mensagem {quantos}: {mensagem}")
            time.sleep(2)  

    def get_active_rovers(self): 
        try:
            self.lock.acquire()
            if "rovers" not in self.dados:
                return []
            return self.dados["rovers"]
        finally:
            self.lock.release()

    def register_telemetry(self, msg):
        print("DATABASE.register_telemetry chamado")
        telemetry_dict = {
            "rover_id": msg.rover_id,
            "position": msg.position,
            "state": msg.state,        
            "power_level": msg.power_level,
            "orientation": msg.orientation,
            "temperature": msg.temperature,
            "speed": msg.speed,
            "direction": msg.direction
        }
        try:
            self.lock.acquire()
            if "rovers" not in self.dados:
                self.dados["rovers"] = {}
            self.dados["rovers"][msg.rover_id] = msg.state
            self.dados["last_telemetries"][msg.rover_id] = telemetry_dict #para a função da ultima telemetria
        finally:
            self.lock.release()



    def add_mission(self, ml_mission, rover_id: str):
        print("DATABASE.add_mission chamado")
        mission_id = ml_mission.mission_id
        mission_type_name = get_mission_name(ml_mission.task)
        param_name = get_param_name(ml_mission.task, ml_mission.task_param)
        mission_dict = {
            "mission_id": mission_id,
            "rover_id": rover_id,
            "status": "ACTIVE",         
            "progress": 0,             
            "mission_type": mission_type_name,  
            "task_code": ml_mission.task,      
            "task_param_code": ml_mission.task_param,
            "task_param": param_name,         
            "area": ml_mission.area,         
            "duration": ml_mission.duration,
            "update_interval": ml_mission.update_interval,
            "created_at": ml_mission.timestamp,
            "last_update": ml_mission.timestamp,
        }
        try:
            self.lock.acquire()
            self.dados["missions"][mission_id] = mission_dict
        finally:
            self.lock.release()


    def update_mission(self, report):
        print("DATABASE.update_mission chamado")
        #report é o nome dado ao packet   
        STATUS_MAP = {
            '1': "IN_PROGRESS",
            '2': "COMPLETED",
            '3': "FAILED"
        }
        try:
            self.lock.acquire()
            missions = self.dados.get("missions", {})
            mission = missions.get(report.mission_id)
            if mission is None:
                return 
            
            mission["progress"] = report.progress
            mission["status"] = STATUS_MAP.get(report.status, "UNKNOWN")
            mission["last_update"] = report.timestamp
            mission["last_event"] = get_event_name (
                mission["task_code"],  
            report.status 
            )
        finally:
            self.lock.release()
            
    
    def get_missions(self):
        try:
            self.lock.acquire()
            missions_dict = self.dados.get("missions", {})
            return missions_dict
        finally:
            self.lock.release()


    def get_last_telemetry(self):
        try:
            self.lock.acquire()
            return self.dados.get("last_telemetries")
        finally:
            self.lock.release()

    def get_rover_telemetry(self, rover_id: str):
        try:
            self.lock.acquire()
            return self.dados["last_telemetries"][rover_id]
        finally:
            self.lock.release()

