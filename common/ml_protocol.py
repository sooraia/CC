"""Serialização binária para Mission Link (UDP)"""

from abc import ABC, abstractmethod
import struct
import threading
import time
from typing import ClassVar

# superclasse abstrata para mensagens ML, subclasses para cada tipo de mensagem
# tipo, timestamp, numseq - comum a qualquer mensagem missionlink (header aplicacional)

class SerializationException(Exception):
    pass


class MissionLink(ABC):

    _sequence_counter: ClassVar[int] = 0
     
    def __init__(self, timestamp, sequence_num: int = 0):
        self.sequence_num = sequence_num    #número de sequência
        self.timestamp = timestamp

    def get_message_type(self) -> str:      #códigos para cada tipo de mensagem
        if isinstance(self, MLRequest):
            return '1'
        elif isinstance(self, MLMission):
            return '2'
        elif isinstance(self, MLAck):
            return '3'
        elif isinstance(self, MLReport):
            return '4'
        else:
            return
    
    @abstractmethod
    def serialize_payload(self) -> bytes:
        pass

    def serialize(self) -> bytes:
        header = self.get_message_type().encode('utf-8')

        timestamp= int(time.time())   #timestamp em que a mensagem é enviada
        header += timestamp.to_bytes(4, 'big')

        header += self.sequence_num.to_bytes(4, 'big')

        payload = self.serialize_payload()

        return header + payload

    @abstractmethod
    def deserialize_payload(data):
        pass
 
    @classmethod
    def from_bytes(cls, data: bytes):

        if(bytes.__len__<9):
            raise SerializationException('Unknown message type') 

        message_type = data[0:1].decode('utf-8')
        timestamp = int.from_bytes(data[1:5], "big")
        sequence_num = int.from_bytes(data[5:9], "big")

        cls(timestamp, sequence_num)

        payload = data[9:]
        
        if message_type == '1':
            return MLRequest._deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '2':
            return MLMission._deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '3':
            return MLAck._deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '4':
            return MLReport._deserialize_payload(payload, timestamp, sequence_num)
        else:
            raise SerializationException('Unknown message type')
    

class MLRequest(MissionLink): #mensagem ML do tipo Pedido (subclasse de MissionLink)

    def __init__(self, rover_id, timestamp, sequence_num: int = 0):
        super().__init__(timestamp, sequence_num)
        self.rover_id = rover_id

    def serialize_payload(self):
        return self.rover_id.encode("utf-8")
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if(payload<2):
            raise SerializationException('Unknown message type') 

        rover_id = payload.decode('utf-8').rstrip('\0')
        message = cls(rover_id, timestamp, sequence_num)
        return message

class MLAck(MissionLink): #mensagem ML do tipo Ack

    def __init__(self, timestamp, sequence_num: int = 0):
        super().__init__(timestamp,sequence_num)
        #...

    def serialize_payload(self):
        #...
        return
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        #...
        message = cls(timestamp, sequence_num)
        return message


class MLMission(MissionLink): #mensagem ML do tipo Missão

    mission_counter: int = 0 # Para o mission_id
    _counter_lock = threading.Lock()

    def __init__(self, area : list, task : str, task_param : str, duration : int, update_interval : int, timestamp : int, sequence_num: int = 0, mission_id: str = None):
        super().__init__(timestamp,sequence_num)

        if mission_id is None:
            self.mission_id = self.get_mission_id()
        else:
            mission_id = mission_id
        
        if(not isinstance(area, list) or (len(area) != 2) or validate_polar_coords(area[0]) or validate_polar_coords(area[1])):
            raise ValueError("Invalid Area")
        
        self.area = area # [[r1,a1],[r2,a2]]
        self.task = task
        self.task_param = task_param
        self.duration = duration
        self.update_interval = update_interval

    @classmethod
    def get_mission_id(cls):
        with cls._counter_lock:
            cls._mission_counter += 1
        return f"M-{cls._mission_counter:03d}" #capped a 999 missões

    def serialize_payload(self):
        res = self.mission_id.encode('utf-8') # 5 bytes M-xxx

        res += struct.pack('>f', self.area[0][0])
        res += struct.pack('>f', self.area[0][1])
        res += struct.pack('>f', self.area[1][0])
        res += struct.pack('>f', self.area[1][1])

        res += self.task.encode('utf-8')        # 1 byte
        res += self.task_param.encode('utf-8')  # 1 byte
        res += self.duration.to_bytes(4, 'big')
        res += self.update_interval.to_bytes(4, 'big')

        return res
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        mission_id = payload[0:5].decode('utf-8')

        area = [
            [struct.unpack('>f', payload[5:9])[0],    # ponto1 distance
            struct.unpack('>f', payload[9:13])[0]],  # ponto1 bearing
            [struct.unpack('>f', payload[13:17])[0],  # ponto2 distance  
            struct.unpack('>f', payload[17:21])[0]]  # ponto2 bearing
        ]
        
        task = payload[21:22].decode('utf-8')
        task_param = payload[22:23].decode('utf-8')
        duration = int.from_bytes(payload[23:27], 'big')
        update_interval = int.from_bytes(payload[27:31], 'big')

        message = cls(
            area,
            task,
            task_param, 
            duration,
            update_interval,
            timestamp,
            sequence_num,
            mission_id
        )
        return message

class MLReport(MissionLink): #mensagem ML do tipo Report (atualização)

    def __init__(self, timestamp, sequence_num: int = 0):
        super().__init__(timestamp,sequence_num)
        #...

    def serialize_payload(self):
        #...
        return

    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        #...
        message = cls(timestamp, sequence_num)
        return message
    
