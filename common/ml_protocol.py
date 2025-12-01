"""Serialização binária para Mission Link (UDP)"""

from abc import ABC
from typing import ClassVar
import time
import struct
import threading


class SerializationException(Exception):
    pass


class MLMessage(ABC):
    _sequence_counter: ClassVar[int] = 0
     
    def __init__(self, timestamp: int, sequence_num: int = 0):
        self.sequence_num = sequence_num    # número de sequência
        self.timestamp = timestamp

    def get_message_type(self) -> str:      # códigos para cada tipo de mensagem
        if isinstance(self, MLRequest):
            return '1'
        elif isinstance(self, MLMission):
            return '2'
        elif isinstance(self, MLAck):
            return '3'
        elif isinstance(self, MLReport):
            return '4'
        else:
            raise SerializationException("Unknown message subclass")

    def serialize_payload(self) -> bytes:
        raise NotImplementedError

    def serialize(self) -> bytes:
        header = self.get_message_type().encode('utf-8')

        # timestamp em que a mensagem é enviada
        timestamp = int(time.time())
        header += timestamp.to_bytes(4, 'big')

        header += self.sequence_num.to_bytes(4, 'big')

        payload = self.serialize_payload()

        return header + payload
 
    @classmethod
    def from_bytes(cls, data: bytes):
        if len(data) < 9:
            raise SerializationException("Message too short")

        message_type = data[0:1].decode('utf-8')
        timestamp = int.from_bytes(data[1:5], "big")
        sequence_num = int.from_bytes(data[5:9], "big")
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
            raise SerializationException(f"Unknown message type: {message_type}")


class MLRequest(MLMessage):  # mensagem ML do tipo Pedido
    def __init__(self, rover_id: str, timestamp: int, sequence_num: int = 0):
        super().__init__(timestamp, sequence_num)
        self.rover_id = rover_id

    def serialize_payload(self) -> bytes:
        return self.rover_id.encode("utf-8")
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if len(payload) < 1:
            raise SerializationException("MLRequest payload too short")
        rover_id = payload.decode('utf-8').rstrip('\0')
        return cls(rover_id, timestamp, sequence_num)


class MLAck(MLMessage):  # mensagem ML do tipo Ack
    def __init__(self, mission_id: str, timestamp: int, sequence_num: int = 0):
        super().__init__(timestamp, sequence_num)
        self.mission_id = mission_id  # ex: "M-001"

    def serialize_payload(self) -> bytes:
        # 5 bytes "M-xxx"
        return self.mission_id.encode('utf-8')

    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if len(payload) < 5:
            raise SerializationException("MLAck payload too short")
        mission_id = payload[0:5].decode('utf-8')
        return cls(mission_id, timestamp, sequence_num)


def validate_polar_coords(coord):
    """Valida coordenadas polares [distance, bearing]"""
    if not isinstance(coord, list) or len(coord) != 2:
        return True  # inválido
    return False


class MLMission(MLMessage):  # mensagem ML do tipo Missão

    def __init__(
        self,
        area: list,
        task: str,
        task_param: str,
        duration: int,
        update_interval: int,
        timestamp: int,
        mission_id: str,
        sequence_num: int = 0
    ):
        super().__init__(timestamp, sequence_num)

        self.mission_id = mission_id 
        
        if (
            not isinstance(area, list)
            or len(area) != 2
        ):
            raise ValueError("Invalid Area")
        
        if(task_param is None):
            task_param = '0'

        self.area = area  # [[r1,a1],[r2,a2]]
        self.task = task              # 1 byte
        self.task_param = task_param  # 1 byte
        self.duration = duration
        self.update_interval = update_interval

    def serialize_payload(self) -> bytes:
        res = self.mission_id.encode('utf-8')  # 5 bytes M-xxx

        res += struct.pack('>f', round(self.area[0][0], 2))
        res += struct.pack('>f', round(self.area[0][1], 2))
        res += struct.pack('>f', round(self.area[1][0], 2))
        res += struct.pack('>f', round(self.area[1][1], 2))

        res += self.task.encode('utf-8')        # 1 byte
        res += self.task_param.encode('utf-8')  # 1 byte
        res += self.duration.to_bytes(4, 'big')
        res += self.update_interval.to_bytes(4, 'big')

        return res
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if len(payload) < 31:
            raise SerializationException("MLMission payload too short")

        mission_id = payload[0:5].decode('utf-8')

        area = [[round(struct.unpack('>f', payload[5:9])[0], 2),
            round(struct.unpack('>f', payload[9:13])[0], 2)],
            [round(struct.unpack('>f', payload[13:17])[0], 2),
            round(struct.unpack('>f', payload[17:21])[0], 2)]]
        
        task = payload[21:22].decode('utf-8')
        task_param = payload[22:23].decode('utf-8')
        duration = int.from_bytes(payload[23:27], 'big')
        update_interval = int.from_bytes(payload[27:31], 'big')

        return cls(
            area,
            task,
            task_param, 
            duration,
            update_interval,
            timestamp,
            mission_id,
            sequence_num
        )
    
    def print_mission(self):
        print(f"Mission ID: {self.mission_id}")
        print(f"Area: {self.area}")
        print(f"Task: {self.task}")
        print(f"Task Param: {self.task_param}")
        print(f"Duration: {self.duration} seconds")
        print(f"Update Interval: {self.update_interval} seconds")


class MLReport(MLMessage):  # mensagem ML do tipo Report (atualização)
    def __init__(self, mission_id: str, status: str, progress: int, timestamp: int, sequence_num: int = 0):
        super().__init__(timestamp, sequence_num)
        self.mission_id = mission_id   # "M-xxx"
        self.status = status           # 1 byte, ex: '1'=em curso, '2'=concluída, '3'=falha
        self.progress = progress       # 0-100

    def serialize_payload(self) -> bytes:
        self.print_report()
        res = self.mission_id.encode('utf-8')      # 5 bytes
        res += self.status.encode('utf-8')         # 1 byte
        res += self.progress.to_bytes(1, 'big')    # 1 byte
        return res

    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if len(payload) < 7:
            raise SerializationException("MLReport payload too short: {len(payload)} bytes")
        mission_id = payload[0:5].decode('utf-8')
        status = payload[5:6].decode('utf-8')
        progress = int.from_bytes(payload[6:7], 'big')
        return cls(mission_id, status, progress, timestamp, sequence_num)
    
    def print_report(self):
        print(f"Mission ID: {self.mission_id}, number of bytes: {len(self.mission_id.encode('utf-8'))}")
        print(f"Status: {self.status}, number of bytes: {len(self.status.encode('utf-8'))}")
        print(f"Progress: {self.progress}%, number of bytes: {len(self.progress.to_bytes(1, 'big'))}")

