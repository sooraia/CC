import socket
import threading
import time
from common.mission_link import MissionLink
from common.ml_protocol import MLReport, MLRequest, MLMission, MLAck
from mother.mission_generator import MissionGenerator
from .Database import Database

class MLServerHandler(MissionLink):

    def __init__(self, host: str, port : int, db : Database, mg : MissionGenerator):
        self.database = db
        self.mission_generator = mg
        self.running = False
        self.port = port

        super().__init__()
        self.socket.bind((host, port))

    def _handle_packet(self, packet, addr):
        if isinstance(packet, MLRequest):
            print(f"Received MLRequest: From {addr[0]}:{addr[1]}")
            print('\n')
            mission = self.mission_generator.get_mission(self.database, packet.rover_id) 
            msg = MLMission(
                area=mission['area'],
                task=mission['task'], 
                task_param=mission['task_param'],
                duration=mission['duration'],
                update_interval=mission['update_interval'],
                timestamp=time.time(),
                sequence_num=packet.sequence_num+1,
                mission_id = mission['mission_id']
                )
            msg.print_mission()#!!!!!!!!!!!!!!!!!debug
            self.send_packet(msg, addr)
            self._add_to_pending_acks(msg, addr)
            self.database.add_mission(msg, packet.rover_id)
            return True
        
        elif isinstance(packet, MLReport):
            print(f"Received MLReport: From {addr[0]}:{addr[1]}")
            print(f"Mission ID: {packet.mission_id}, Progress: {packet.progress}, Status: {packet.status}")
            print('\n')
            self.database.update_mission(packet)
            ack = MLAck(packet.mission_id, time.time(), packet.sequence_num)
            print('------------------------------------------------------')
            print('Sending MLAck for Mission ID:', packet.mission_id, 'to', addr[0], ':', addr[1])
            print('------------------------------------------------------')
            self.send_packet(ack, addr)
            return True
        
        else:
            return False

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
        print("ML server running...")


if __name__ == "__main__":
    db = Database()
    server = MLServerHandler(db)
    server.run_server()