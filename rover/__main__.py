from socket import gethostname
from threading import Thread
from time import sleep
from common.telemetry_system import TelemetrySystem
from common.ts_protocol import TSMessage, TS_DEFAULT_PORT, SerializationException
from rover.telemetry import RoverTelemetry

server_address = '10.0.3.20'
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

        data = message.serialize_telemetry
        TSconnection.send(data)
        sleep(telemetry_interval)


def main(argv: list[str]) -> None:
    threads : list = list()
    rover_state = RoverTelemetry(argv[0])

    telemetrysystem = TelemetrySystem(gethostname())
    telemetrysystem.connect(server_address, TS_DEFAULT_PORT)
    threads.append(Thread(target=send_telemetry(telemetrysystem, rover_state)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()