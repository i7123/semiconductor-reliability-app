from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/test":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "working", "message": "Test endpoint works!"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Default response
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"error": "Not found"}
        self.wfile.write(json.dumps(response).encode())