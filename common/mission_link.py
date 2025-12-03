import socket
import threading
import time

from common.ml_protocol import MLMessage, MLAck, MLRequest

ML_TIMEOUT = 5 
ML_MAX_RETRANSMISSIONS = 3
BUFFER_SIZE = 20 #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class MissionLink:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.pending_acks = {}  # (mission_id, seq): (packet, retries, addr)
        self.acks_lock = threading.Lock()
        self.received_seqs = {}  # mission_id: seqs recebidos
        self.seqs_lock = threading.Lock()
        
    def send_packet(self, packet: MLMessage, dest_addr: tuple):
        data = packet.serialize()
        self.socket.sendto(data, dest_addr)

    def _add_to_pending_acks(self, packet : MLMessage, dest_addr: tuple):
        with self.acks_lock:
            self.pending_acks[(packet.mission_id, packet.sequence_num)] = (packet, 0, dest_addr)

    def _add_received_seq(self, mission_id: int, seq_num: int):
        with self.seqs_lock:
            if mission_id not in self.received_seqs:
                self.received_seqs[mission_id] = set()
            self.received_seqs[mission_id].add(seq_num)

    def has_received_seq(self, mission_id: int, seq_num: int) -> bool:
        with self.seqs_lock:
            return mission_id in self.received_seqs and seq_num in self.received_seqs[mission_id]

    def receive_packet(self): #retorna True se pacote for válido(ack em pending acks/mission para rover/...), False caso contrário
        try:
            data, addr = self.socket.recvfrom(1024)
            packet = MLMessage.from_bytes(data)

            if isinstance(packet, MLAck):
                return self._handle_ack(packet)
            else:
                if getattr(packet, 'mission_id', None) is not None:
                    if self.has_received_seq(packet.mission_id, packet.sequence_num): #ignorar dups
                        return False
                    else:
                        self._add_received_seq(packet.mission_id, packet.sequence_num)

                return self._handle_packet(packet, addr)

        except socket.timeout:
            return False
    
    def _handle_ack(self, ack: MLAck):
        acks_to_remove = []
        found = False
        with self.acks_lock:
            for key in self.pending_acks.keys():
                mission_id, seq = key
                if mission_id == ack.mission_id and seq <= ack.sequence_num:
                    if seq == ack.sequence_num:
                        found = True
                    acks_to_remove.append((mission_id, seq))
            if (found):
                for key in acks_to_remove:
                    del self.pending_acks[key]
                print('------------------------------------------------------')
                print(f"Received MLAck for Mission ID: {ack.mission_id}, Seq: {ack.sequence_num}")
                print('------------------------------------------------------')
                return True
            else:
                return False

    def check_timeouts(self):
        current_time = time.time()
        timed_out = []

        with self.acks_lock:
            for key in list(self.pending_acks.keys()):
                packet, retries, addr = self.pending_acks[key]
                
                if current_time - packet.timestamp > ML_TIMEOUT:
                    if retries >= ML_MAX_RETRANSMISSIONS: # adicionar à lista de timed out as que atingiram o max de retries
                        timed_out.append(key)
                        print(f"Mission {packet.mission_id} timed out after {ML_MAX_RETRANSMISSIONS} retries")#DEBUG!!!!!!!!!!!!!!!!!!11
                    else:                                   # retransmitir
                        packet.timestamp = current_time
                        self.send_packet(packet, addr)
                        self.pending_acks[key] = (packet, retries + 1, addr)
                        print(f"Retransmitting packet from mission {packet.mission_id}, retry {retries + 1}, seq {packet.sequence_num}")#DEBUG!!!!!!!!!!!!!!!!!!11
            
            for key in timed_out:
                del self.pending_acks[key]

    def _check_timeouts_loop(self):
        while self.running:
            time.sleep(1)  # verifica a cada 1s**************************
            self.check_timeouts()

    def _handle_packet(self, packet: MLMessage, addr: tuple):
        """Processa pacote recebido (implementação específica)"""
        pass
    
