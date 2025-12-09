import socket
import threading
import time
from common.mission_link import MissionLink
from common.ml_protocol import MLReport, MLRequest, MLMission, MLAck
from mother.mission_generator import MissionGenerator
from .Database import Database

class MLServerHandler(MissionLink):

    def __init__(self, host: str, port : int, db : Database, mg : MissionGenerator, output):
        self.database = db
        self.mission_generator = mg
        self.running = False
        self.port = port

        super().__init__(output)
        self.socket.bind((host, port))

    def _handle_packet(self, packet, addr):
        if isinstance(packet, MLRequest):
            self.print_log(f"Received MLRequest, seq={packet.sequence_num}: From {packet.rover_id} ({addr[0]}:{addr[1]})")

            pending_mission_id = self.database.has_pending_mission(packet.rover_id)
            if pending_mission_id is not None:
                if self.pending_acks.get((pending_mission_id, 2)) is not None:
                    self.print_log(f"Rover {packet.rover_id} already has a pending mission. Ignoring request.")
                    return True  # Ignorar requests de rovers com missão pendente
                else:
                    self.database.update_mission_lost_connection(pending_mission_id)

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
            self.send_packet(msg, addr)
            self.print_log(f"Sent MLMission, seq={msg.sequence_num}: {msg.mission_id}, To: {packet.rover_id}")
            self._add_to_pending_acks(msg, addr)
            self.database.add_mission(msg, packet.rover_id)
            return True
        
        elif isinstance(packet, MLReport):
            self.print_log(f"Received MLReport for Mission:{packet.mission_id}, seq={packet.sequence_num}: Progress: {packet.progress}, Status: {packet.status}")
            self.database.update_mission(packet)
            ack = MLAck(packet.mission_id, time.time(), packet.sequence_num)
            self.send_packet(ack, addr)
            self.print_log(f"Sent MLAck for Mission: {packet.mission_id}, ack={ack.sequence_num}")

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
        self.print_log("ML server running.")


if __name__ == "__main__":
    db = Database()
    server = MLServerHandler(db)
    server.run_server()