import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from .Database import Database

db = Database()

class MotherRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/rovers/active":
            self._send_json(db.get_active_rovers())
        elif self.path == "/missions":
            self._send_json(db.get_missions())
        elif self.path == "/telemetry":
            data = db.get_last_telemetry()
            if data is None:
                self._send_json({"error": "No telemetry for this rover"}, status=404)
            else:
                self._send_json(data)
        else:
            self._send_json({"error": "Not found"}, status=404)

def run_server(host="0.0.0.0", port=5000):
    server = HTTPServer((host, port), MotherRequestHandler)
    print(f"Serving HTTP on {host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
