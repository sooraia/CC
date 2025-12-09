from socket import gethostname
import sys
from threading import Thread
from common.__init__ import TS_DEFAULT_PORT, ML_DEFAULT_PORT
from rover.ml_client import MLClientHandler
from rover.telemetry import RoverTelemetry
from rover.ts_client import TelemetrySystemClient
import json

telemetry_interval = 5

def main(argv: list[str]) -> None:
    threads : list = list()

    output = sys.stdout
    hostname = gethostname()
    rover_id = f"R-{hostname.split('-')[-1]}" if '-' in hostname else f"R-{hostname}"

    if len(argv) > 1 and argv[1] == '-l':
        logfile = ('temp/' + argv[2]) if len(argv) > 2 else f'temp/{rover_id}_log.txt'
        output = open(logfile, 'w', buffering=1)
    
    with open('config/nodes.json', 'r') as file:
        nodes_config = json.load(file)
    current_hostname = gethostname()
    rover_config = nodes_config.get(current_hostname)
    server_address = nodes_config['nave-mae']['interfaces'][rover_config['mother_interface']]

    rover_state = RoverTelemetry(rover_id=f"R-{current_hostname.split('-')[1]}")

    telemetrysystem = TelemetrySystemClient(rover_state, telemetry_interval, '', 0)
    missionlink = MLClientHandler(rover_state, output)

    telemetrysystem.connect(server_address, TS_DEFAULT_PORT)

    threads.append(Thread(target=rover_state.update_telemetry_loop))
    threads.append(Thread(target=telemetrysystem.send_telemetry_stream))
    threads.append(Thread(target=missionlink.run_client, args=((server_address, ML_DEFAULT_PORT),)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main(sys.argv)