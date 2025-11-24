import threading
import time
from common.mission_link import MissionLink
from common.ml_protocol import MLReport, MLRequest, MLMission, MLAck
from mother.mission_generator import get_mission
from mother import Database

class MLServerHandler(MissionLink):

    def __init__(self, db : Database):
        self.database = db
        self.running = False
        super().__init__()

    def _handle_packet(self, packet, addr):
        if isinstance(packet, MLRequest):
            mission = get_mission(packet.rover_id) 
            msg = MLMission(
                area=mission['area'],
                task=mission['task'], 
                task_param=mission['task_param'],
                duration=mission['duration'],
                update_interval=mission['update_interval'],
                timestamp=mission['timestamp'],
                sequence_num=packet.sequence_num+1,
                mission_id = mission['mission_id']
                )
            self.send_packet(msg, addr)
            self._add_to_pending_acks(msg)
            self.database.add_mission(mission)
            return True
        
        elif isinstance(packet, MLReport):
            self.database.update_mission(packet.mission_id)
            ack = MLAck(packet.mission_id, time.now(), packet.sequence_num)
            self.send_packet(ack, addr)
            return True
        
        else:
            return False

    def _check_timeouts_loop(self):
        while self.running:
            time.sleep(1)  # verifica a cada 1s**************************
            self.check_timeouts()

    def _receive_packets_loop(self):
        while True:
            self.receive_packet()

    def run_server(self):
        self.running= True
        #start check timeout thread
        timeout_thread = threading.Thread(target=self._check_timeouts_loop)
        timeout_thread.daemon = True
        timeout_thread.start()

        #start receiver thread
        receiver_thread = threading.Thread(target=self._receive_packets_loop)
        receiver_thread.daemon = True
        receiver_thread.start()
