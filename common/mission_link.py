import socket
import time

from common.ml_protocol import MLMessage, MLAck

ML_TIMEOUT = 20
ML_MAX_RETRANSMISSIONS = 20
BUFFER_SIZE = 20 #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class MissionLink:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pending_acks = {}  # (mission_id, seq): (packet, retries, addr)
        
    def send_packet(self, packet: MLMessage, dest_addr: tuple):
        data = packet.serialize()
        self.socket.sendto(data, dest_addr)

    def _add_to_pending_acks(self, packet : MLMessage, dest_addr: tuple):
        self.pending_acks[(packet.mission_id, packet.sequence_num)] = (packet, 0, dest_addr)

    def receive_packet(self): #retorna True se pacote for válido(ack em pending acks/mission para rover/...), False caso contrário
        try:
            data, addr = self.socket.recvfrom(1024)
            packet = MLMessage.from_bytes(data)

            if isinstance(packet, MLAck):
                return self._handle_ack(packet)
            else:
                return self._handle_packet(packet, addr)

        except socket.timeout:
            return False
    
    def _handle_ack(self, ack: MLAck):
        if (ack.mission_id, ack.sequence_num) in self.pending_acks:
            del self.pending_acks[(ack.mission_id, ack.sequence_num)]
            return True
        else:
            return False

    def check_timeouts(self):
        for key,(packet, retries, addr) in self.pending_acks:  #!!!!!!!not safe alterar (?)
            if time.time() - packet.timestamp > ML_TIMEOUT:
                if(retries==ML_MAX_RETRANSMISSIONS):
                    pass
                    #to do
                else:
                    packet.timestamp = time.time()
                    self.send_packet(packet, addr)
                    self.pending_acks[key] = (packet, retries + 1, addr)

    def _handle_packet(self, packet: MLMessage, addr: tuple):
        """Processa pacote recebido (implementação específica)"""
        pass
        #verificar se o nºseq é duplicado?
    
