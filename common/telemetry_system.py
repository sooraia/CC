import socket
import threading
import time
from common.ts_protocol import TS_LENGTH

class TelemetrySystem:

    def __init__(self, host: str, port: int = 0): # valor default 0 >>> o sistema encontra uma porta livre
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socket.bind((self.host, self.port))
        
        self.lock = threading.RLock()
        self.running = False
        
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
                    break  # Cliente desconectou
                
                self._handle_message(data, addr)

            except (ConnectionResetError, BrokenPipeError):
                break  # Cliente desconectou abruptamente
            except Exception as e:
                print(f"Erro com cliente {addr}: {e}")
                break

    def connect(self, host: str, port: int):
        print("1")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("2")
        #self.socket.settimeout(10.0)  # Timeout para connect()
        self.socket.connect((host, port))
        print("3")
        self.connected_addr = host
        self.connected_port = port
        print(f"Conectado a {host}:{port}")

    def send(self, data: bytes):
        if self.socket:
            self.socket.sendall(data)

    def _handle_message(self, data: bytes, addr: tuple):
        pass

    def close(self):
        self.running = False
        if self.socket:
            self.socket.close()
            self.socket = None