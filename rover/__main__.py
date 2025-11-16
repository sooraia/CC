from socket import gethostname
import sys
from threading import Thread
from common.__init__ import TS_DEFAULT_PORT
from rover.telemetry import RoverTelemetry
from rover.ts_client import TelemetrySystemClient

telemetry_interval = 5

def main(argv: list[str]) -> None:
    threads : list = list()
    rover_state = RoverTelemetry(rover_id='R-01', planet='1') #rover_id=gethostname() ??
    
    server_address = ''
    if(len(argv)>1):
        print("server address: " + argv[1])
        server_address = argv[1]

    telemetrysystem = TelemetrySystemClient(rover_state, telemetry_interval, '', 0)
    telemetrysystem.connect(server_address, TS_DEFAULT_PORT)
    print(f"Connected to server at {server_address}:{TS_DEFAULT_PORT}...")
    threads.append(Thread(target=telemetrysystem.send_telemetry_stream()))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main(sys.argv)