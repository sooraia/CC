from threading import Thread
from common.__init__ import TS_DEFAULT_PORT, ML_DEFAULT_PORT
from common.__init__ import TS_DEFAULT_PORT
from common.Database import Database
import sys
from mother.ml_server import MLServerHandler
from mother.ts_server import TelemetrySystemServer
from mother.mission_generator import MissionGenerator

def main(argv: list[str]) -> None:
    threads : list = list()
    database : Database = Database()
    mission_generator = MissionGenerator()

    telemetrysystem = TelemetrySystemServer(database, '0.0.0.0', TS_DEFAULT_PORT)
    missionlink = MLServerHandler('0.0.0.0', ML_DEFAULT_PORT, database, mission_generator)

    threads.append(Thread(target=telemetrysystem.start_server))
    threads.append(Thread(target=missionlink.run_server))
    print("Servers created.\n")
    for thread in threads:
        thread.start()
        print("Server started")
    print("Server started.")
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main(sys.argv)