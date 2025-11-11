from threading import Thread
from common.__init__ import TS_DEFAULT_PORT
from common.telemetry_system import TelemetrySystem
from common.ts_protocol import TSMessage, SerializationException
from Database import Database

class ServerTSHandler(TelemetrySystem):
    
    def __init__(self, host, port, database):
        self.database = database
        super().__init__(self, host, port)

    def _handle_message(self, data: bytes, addr: tuple):
        try:
            message = TSMessage.deserialize_telemetry(data)
            self.database.register_telemetry(message)
        except SerializationException as e:
            print(f'Ignoring SerializationException: {e}')


def main(argv: list[str]) -> None:
    threads : list = list()
    database : Database = Database()

    telemetrysystem = ServerTSHandler('server', TS_DEFAULT_PORT, database)
    threads.append(Thread(target=telemetrysystem.start_server))
    
    #threads.append(Thread(target=arranca_servico2, args=(database,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()