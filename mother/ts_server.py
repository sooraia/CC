import socket
import threading
import time
from common.ts_protocol import TS_LENGTH, SerializationException, TSMessage
from .Database import Database

class TelemetrySystemServer:

    def __init__(self, database, host: str, port: int = 0): # valor default 0 >>> o sistema encontra uma porta livre
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socket.bind((self.host, self.port))
        
        self.lock = threading.RLock()
        self.running = False
        self.database = database
        
    def start_server(self) -> None:
        self.running = True
        with self.lock:
            self.socket.listen()
            while self.running:
                client_socket, addr = self.socket.accept()
                connection_thread = threading.Thread(target=self._handle_client,  args=(client_socket, addr))
                connection_thread.start()

    def _handle_client(self, client_socket: socket.socket, addr: tuple):
        while self.running:
            try:
                data = client_socket.recv(TS_LENGTH)  # tamanho fixo
                if not data:
                    break 
                self._handle_message(data, addr)

            except (ConnectionResetError, BrokenPipeError):
                break 
            except Exception as e:
                print(f"Erro com cliente {addr}: {e}")
                break

    def send(self, data: bytes):
        if self.socket:
            self.socket.sendall(data)

    def _handle_message(self, data: bytes, addr: tuple):
        try:
            message = TSMessage.deserialize_telemetry(data)
            # print("....................................")
            # message.print_telemetry()
            # print("....................................")
            self.database.register_telemetry(message)
        except SerializationException as e:
            print(f'Ignoring SerializationException: {e}')

    def close(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None
            
if __name__ == "__main__":
    db = Database()
    server = TelemetrySystemServer(db, host="0.0.0.0", port=5001)
    server.start_server()
    