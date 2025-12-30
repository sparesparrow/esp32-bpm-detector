#!/usr/bin/env python3
"""
Mock ESP32 API and WebSocket services for testing.
"""

import http.server
import socketserver
import asyncio
import websockets
import json
import time
import random
from urllib.parse import urlparse, parse_qs


class MockESP32Handler(http.server.BaseHTTPRequestHandler):
    """Mock ESP32 HTTP API handler."""

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/bpm":
            # Simulate BPM data
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
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        elif parsed_path.path == "/api/settings":
            response = {
                "min_bpm": 60,
                "max_bpm": 200,
                "sample_rate": 25000,
                "fft_size": 1024,
                "version": "1.0.0-test"
            }
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass


async def mock_websocket_handler(websocket, path):
    """Mock WebSocket handler."""
    print(f"WebSocket connection from {websocket.remote_address}")
    try:
        async for message in websocket:
            # Echo back with simulated data
            bpm = random.uniform(60, 200)
            response = {
                "type": "bpm_update",
                "bpm": round(bpm, 1),
                "timestamp": int(time.time() * 1000)
            }
            await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed:
        pass


def start_http_server():
    """Start the HTTP server."""
    print("✅ Mock ESP32 API server starting on port 8080")
    with socketserver.TCPServer(("", 8080), MockESP32Handler) as httpd:
        httpd.serve_forever()


def start_websocket_server():
    """Start the WebSocket server."""
    print("✅ Mock WebSocket server starting on port 8000")
    start_server = websockets.serve(mock_websocket_handler, "0.0.0.0", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    import sys
    import threading

    print("🔧 Starting Mock Services...")

    # Start HTTP server in a separate thread
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start WebSocket server in main thread
    try:
        start_websocket_server()
    except KeyboardInterrupt:
        print("🛑 Mock services stopped")