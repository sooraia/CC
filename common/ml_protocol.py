from abc import ABC
from typing import ClassVar
import time
import struct
import threading

MISSION_CODES = {
    'S': 0b000,
    'I': 0b001,
    'E': 0b010,
    'D': 0b011,
    'M': 0b100,
    'A': 0b101,
}

PARAM_CODES = {
    'S': {'S': 0b00, 'R': 0b01, 'A': 0b10, 'W': 0b11},
    'I': {'P': 0b00, 'C': 0b01, 'M': 0b10},
    'E': {'T': 0b00, 'R': 0b01, 'P': 0b10, 'H': 0b11},
    'D': {'S': 0b00, 'W': 0b01, 'M': 0b10, 'C': 0b11},
    'M': {'H': 0b00, 'M': 0b01, 'L': 0b10},
    'A': {} 
}

def pack_mission_byte(mission_code, param_code=None):
    mission_bits = MISSION_CODES.get(mission_code, 0) # 3 bits
    
    has_param = param_code is not None # 1 bit
    param_flag = 0b1 if has_param else 0b0 # 1 bit
    
    if has_param and mission_code in PARAM_CODES:
        param_bits = PARAM_CODES[mission_code].get(param_code, 0)
    else:
        param_bits = 0
    
    fill_bits = 0b00
    
    packed = (mission_bits << 5) | (param_flag << 4) | (param_bits << 2) | fill_bits
    
    return bytes([packed])

def unpack_mission_byte(byte_val):
    mission_idx = (byte_val >> 5) & 0b111 # 7-5
    has_param = (byte_val >> 4) & 0b1 # 4
    param_bits = (byte_val >> 2) & 0b11 # 3-2
    fill = byte_val & 0b11
    
    mission_code = {v: k for k, v in MISSION_CODES.items()}[mission_idx]
    
    param_code = None
    if has_param and mission_code in PARAM_CODES:
        param_dict = PARAM_CODES[mission_code]
        for code, bits in param_dict.items():
            if bits == param_bits:
                param_code = code
                break
    
    return mission_code, param_code



class SerializationException(Exception):
    pass

class MLMessage(ABC):
     
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

        res += pack_mission_byte(self.task, self.task_param)
        res += self.duration.to_bytes(4, 'big')
        res += self.update_interval.to_bytes(4, 'big')

        return res
    
    @classmethod
    def _deserialize_payload(cls, payload: bytes, timestamp: int, sequence_num: int):
        if len(payload) < 30:
            raise SerializationException("MLMission payload too short")

        mission_id = payload[0:5].decode('utf-8')

        area = [[round(struct.unpack('>f', payload[5:9])[0], 2),
            round(struct.unpack('>f', payload[9:13])[0], 2)],
            [round(struct.unpack('>f', payload[13:17])[0], 2),
            round(struct.unpack('>f', payload[17:21])[0], 2)]]
        
        task, task_param = unpack_mission_byte(payload[21])
        duration = int.from_bytes(payload[22:26], 'big')
        update_interval = int.from_bytes(payload[26:30], 'big')

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

