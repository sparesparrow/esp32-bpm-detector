#!/usr/bin/env python3
"""
Simple mock ESP32 HTTP server for testing Android app connection.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
import random

class MockESP32Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/bpm":
            # Mock BPM data response
            bpm = random.uniform(60, 200)
            confidence = random.uniform(0.3, 0.95)
            signal_level = random.uniform(0.2, 0.9)

            response = {
                "bpm": round(bpm, 1),
                "confidence": round(confidence, 2),
                "signal_level": round(signal_level, 2),
                "status": "detecting",
                "timestamp": int(time.time() * 1000)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        elif self.path == "/api/settings":
            # Mock settings response
            response = {
                "min_bpm": 60,
                "max_bpm": 200,
                "sample_rate": 25000,
                "fft_size": 1024,
                "version": "1.0.0-test"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    server_address = ('127.0.0.1', 8080)
    httpd = HTTPServer(server_address, MockESP32Handler)

    print(f"🎯 Mock ESP32 API server starting on {server_address[0]}:{server_address[1]}")
    print("📡 Serving BPM data at /api/bpm")
    print("⚙️ Serving settings at /api/settings")
    print("🛑 Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    main()