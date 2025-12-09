import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from .Database import Database

class MotherRequestHandler(BaseHTTPRequestHandler):
    db = None

    @classmethod
    def set_database(self, database: Database):
        self.db = database

    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self): #cors
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS, POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400") 
        self.end_headers()

    def do_GET(self):
        if self.path == "/rovers/active":
            self._send_json(self.db.get_active_rovers())
        elif self.path == "/missions":
            self._send_json(self.db.get_missions())
        elif self.path == "/telemetry":
            data = self.db.get_last_telemetry()
            if data is None:
                self._send_json({"error": "No telemetry for this rover"}, status=404)
            else:
                self._send_json(data)
        else:
            self._send_json({"error": "Not found"}, status=404)

def run_api_server(host, port, database: Database):
    MotherRequestHandler.set_database(database)
    server = HTTPServer((host, port), MotherRequestHandler)
    print(f"Serving HTTP on {host}:{port}")
    server.serve_forever()