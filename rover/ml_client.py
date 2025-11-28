import random
import threading
import time
from common.mission_link import MissionLink, ML_TIMEOUT, ML_MAX_RETRANSMISSIONS
from common.ml_protocol import MLReport, MLRequest, MLMission, MLAck
from rover.telemetry import RoverTelemetry

BACKOFF = 30

class MLClientHandler(MissionLink):

    def __init__(self, state: RoverTelemetry):
        self.telemetry = state
        super().__init__()
        self.socket.settimeout(ML_TIMEOUT)

    def send_request_loop(self, server_addr : tuple):
        self.server_addr = server_addr
        while True:
            retries = 0
            pending_request = False
            print
            if(self.telemetry.operational_state == 'IDLE'):
                request = MLRequest(rover_id= self.telemetry.rover_id, timestamp= time.time(), sequence_num=1) #numero de seq começa em 1 para cada "conexão"
                pending_request = True
                self.send_packet(request, server_addr) 
                print(f"Sent MLRequest (seq: {request.sequence_num}) to {server_addr[0]}:{server_addr[1]}")

            while pending_request == True and retries < ML_MAX_RETRANSMISSIONS: #reenvio do request após o timeout enquanto não receber o mlmission
                if (self.receive_packet()!=False):
                    pending_request = False 
                else:
                    retries+=1
                    if retries < ML_MAX_RETRANSMISSIONS:
                        request.timestamp = time.time()
                        self.send_packet(request, server_addr) 

            interval = random.uniform(1, 10)  # intervalo entre requests variavel
            if (pending_request==True):
                interval = BACKOFF #esperar tempo=backoff no caso de não ter conseguido receber o mlmission dentro do nº max de retries
            time.sleep(interval)

    def _handle_packet(self, packet, addr): #!!!!!verificar se vem do mesmo endereço que se estava à espera!!
        if isinstance(packet, MLMission):
            print("Received MLMission:")
            packet.print_mission()#!!!!!!!!!!!!!!!!!debug

            if addr!=self.server_addr:
                return False
            
            self.telemetry.add_mission(packet.mission_id, packet.area, packet.task, packet.task_param, packet.duration, packet.update_interval)

            ack = MLAck(packet.mission_id, time.time(), packet.sequence_num)
            print('Sending MLAck for Mission ID:', packet.mission_id)
            self.send_packet(ack, addr)
            print('Sent MLAck for Mission ID:', packet.mission_id)
            self._start_mission(packet)
            return True
        else:
            return False

    def _start_mission(self, packet : MLMission):
        self.telemetry.mission_start_time = time.time()
        self.telemetry.operational_state = 'ON_THE_WAY'

        self.telemetry.go_to_area(self.telemetry.current_mission_area)

        self.telemetry.operational_state = 'ON_MISSION'

        execution_thread = threading.Thread(target=self.telemetry.execute_current_mission)
        execution_thread.start()

        self._report_sender(packet.sequence_num, packet.update_interval)


    def _send_report(self, seq, addr):
        report = MLReport(self.telemetry.current_mission_id,
                          self.telemetry.current_mission_status, 
                          self.telemetry.current_mission_progress, time.time(), seq)
        self.send_packet(report, addr)
        self._add_to_pending_acks(report, addr)
    
    def _report_sender(self, seq : int, interval : int):
        while self.telemetry.operational_state == 'ON_MISSION': #só quando chegar ao local da missão ou a caminho também?
            seq += 1
            self._send_report(seq, self.server_addr)
            time.sleep(interval)

        if self.telemetry.current_mission_progress=='100': #envia um último report no final
            seq += 1
            self._send_report(seq, self.server_addr)

        self.telemetry.reset_mission_paramaters()

    def run_client(self, server_addr : tuple):
        self.running= True
        request_thread = threading.Thread(target=self.send_request_loop, args=(server_addr,))
        request_thread.daemon = True
        request_thread.start()

        #start check timeout thread
        timeout_thread = threading.Thread(target=self._check_timeouts_loop)
        timeout_thread.daemon = True
        timeout_thread.start()
