from threading import Thread
from common.__init__ import TS_DEFAULT_PORT
from mother.Database import Database
import sys
from mother.ts_server import TelemetrySystemServer

def main(argv: list[str]) -> None:
    threads : list = list()
    database : Database = Database()

    telemetrysystem = TelemetrySystemServer(database, '0.0.0.0', TS_DEFAULT_PORT)
    threads.append(Thread(target=telemetrysystem.start_server))
    print("Server created.\n")
    for thread in threads:
        thread.start()
    print("Server started.")
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main(sys.argv)