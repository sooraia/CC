"""Serialização binária para Mission Link (UDP)"""

from abc import ABC, abstractmethod
import struct
import time
from typing import ClassVar

# superclasse abstrata para mensagens ML, subclasses para cada tipo de mensagem
# tipo, timestamp, numseq - comum a qualquer mensagem missionlink (header aplicacional)

class MissionLink(ABC):

    _sequence_counter: ClassVar[int] = 0
     
    def __init__(self, sequence_num: int = 0):
        self.sequence_num = sequence_num    #número de sequência

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
    def deserialize(cls, data: bytes):

        message_type = data[0:1].decode('utf-8')
        timestamp = int.from_bytes(data[1:5], "big")
        sequence_num = int.from_bytes(data[5:9], "big")

        payload = data[9:]
        
        if message_type == '1':
            return MLRequest.deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '2':
            return MLMission.deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '3':
            return MLAck.deserialize_payload(payload, timestamp, sequence_num)
        elif message_type == '4':
            return MLReport.deserialize_payload(payload, timestamp, sequence_num)
        else:
            raise ValueError(f"Tipo desconhecido: {message_type}")
    

class MLRequest(MissionLink): #mensagem ML do tipo Pedido (subclasse de MissionLink)

    def __init__(self, sequence_num: int = 0):
        super().__init__(sequence_num)

    def serialize_payload(self):
        #...
        return
    
    def deserialize_payload(data):
        #...
        return


class MLAck(MissionLink): #mensagem ML do tipo Ack

    def __init__(self, sequence_num: int = 0):
        super().__init__(sequence_num)
        #...

    def serialize_payload(self):
        #...
        return
    
    def deserialize_payload(data):
        #...
        return


class MLMission(MissionLink): #mensagem ML do tipo Missão

    def __init__(self, sequence_num: int = 0):
        super().__init__(sequence_num)
        #...

    def serialize_payload(self):
        #...
        return

    def serialize(self):
        res=super.serialize_header()
        #...
        return
    
    def deserialize_payload(data):
        #...
        return

class MLReport(MissionLink): #mensagem ML do tipo Report (atualização)

    def __init__(self, sequence_num: int = 0):
        super().__init__(sequence_num)
        #...

    def serialize_payload(self):
        #...
        return

    def deserialize_payload(data):
        #...
        return
    
