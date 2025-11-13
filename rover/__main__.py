from socket import gethostname
import sys
from threading import Thread
from time import sleep
from common.telemetry_system import TelemetrySystem
from common.ts_protocol import TSMessage, SerializationException
from common.__init__ import TS_DEFAULT_PORT
from rover.telemetry import RoverTelemetry

server = '10.0.3.20'
telemetry_interval = 120

def send_telemetry(TSconnection, state : RoverTelemetry):
    while(True):

        telemetry_dict = state.get_current_telemetry()
    
        message = TSMessage(
            rover_id=telemetry_dict['rover_id'],
            position=telemetry_dict['position'],
            planet=telemetry_dict['planet'],
            state=telemetry_dict['state'],
            power_level=telemetry_dict['power_level'],
            orientation=telemetry_dict['orientation'],
            temperature=telemetry_dict['temperature'],
            speed=telemetry_dict['speed'],
            direction=telemetry_dict['direction'])
        message.print_telemetry()
        data = message.serialize_telemetry()
        TSconnection.send(data)
        sleep(telemetry_interval)


def main(argv: list[str]) -> None:
    threads : list = list()
    rover_state = RoverTelemetry(rover_id='R-01', planet='1') #rover_id=gethostname() ??
    
    server_address = server
    if(len(argv)>1):
        print("server address: " + argv[1])
        server_address = argv[1]

    telemetrysystem = TelemetrySystem('', 0)
    print(f"Connecting to server at {server_address}:{TS_DEFAULT_PORT}...")
    telemetrysystem.connect(server_address, TS_DEFAULT_PORT)
    print("Connected to server.")
    threads.append(Thread(target=send_telemetry(telemetrysystem, rover_state)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main(sys.argv)