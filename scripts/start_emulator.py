#!/usr/bin/env python3
"""
Start hardware emulator for Docker container.
"""

import sys
import os
import asyncio
import threading
import socket
import time
import random
from typing import List, Dict, Any

class HardwareEmulator:
    """TCP/IP-based hardware emulator for testing without physical devices."""

    def __init__(self, host: str = "127.0.0.1", port: int = 12345, device_type: str = "esp32"):
        self.host = host
        self.port = port
        self.device_type = device_type
        self.server_socket = None
        self.running = False
        self.clients: List[socket.socket] = []
        self.client_threads: List[threading.Thread] = []
        self.status = "stopped"
        self.connected_clients = 0

        # Device-specific configurations
        self.device_configs = {
            "esp32": {
                "bpm_range": (60, 200),
                "sensor_types": ["microphone", "accelerometer", "temperature"],
                "response_delay": 0.1,
                "error_rate": 0.02
            },
            "esp32s3": {
                "bpm_range": (60, 200),
                "sensor_types": ["microphone", "accelerometer", "temperature", "gyroscope"],
                "response_delay": 0.08,
                "error_rate": 0.01
            },
            "arduino": {
                "bpm_range": (60, 180),
                "sensor_types": ["microphone"],
                "response_delay": 0.2,
                "error_rate": 0.05
            }
        }

        self.config = self.device_configs.get(device_type, self.device_configs["esp32"])

    def start(self) -> bool:
        """Start the hardware emulator server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            self.status = "running"

            # Start the main server loop in a separate thread
            server_thread = threading.Thread(target=self._run_loop, daemon=True)
            server_thread.start()

            print(f"Hardware emulator started on {self.host}:{self.port} for {self.device_type}")
            return True
        except Exception as e:
            print(f"Failed to start hardware emulator: {e}")
            self.status = "error"
            return False

    def _run_loop(self):
        """Main server loop running in separate thread."""
        print("Hardware emulator server loop started")

        while self.running:
            try:
                # Accept new connections with timeout
                self.server_socket.settimeout(1.0)
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(f"New client connected: {client_address}")
                    self.connected_clients += 1

                    # Start client handler thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()
                    self.client_threads.append(client_thread)

                except socket.timeout:
                    continue  # Expected timeout, continue loop
                except OSError:
                    break  # Socket closed

            except Exception as e:
                print(f"Error in server loop: {e}")
                break

        print("Hardware emulator server loop ended")

    def _handle_client(self, client_socket: socket.socket, client_address: tuple):
        """Handle individual client connections."""
        try:
            client_socket.settimeout(5.0)  # 5 second timeout for operations

            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(1024)
                    if not data:
                        break  # Client disconnected

                    # Process the request
                    response = self._process_request(data.decode('utf-8', errors='ignore').strip())

                    # Send response
                    if response:
                        client_socket.send(response.encode('utf-8'))

                    # Simulate device response delay
                    time.sleep(self.config["response_delay"])

                except socket.timeout:
                    continue  # Expected timeout, continue listening
                except ConnectionResetError:
                    break  # Client disconnected
                except Exception as e:
                    print(f"Error handling client {client_address}: {e}")
                    break

        except Exception as e:
            print(f"Client handler error for {client_address}: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            self.connected_clients = max(0, self.connected_clients - 1)
            print(f"Client {client_address} disconnected")

    def _process_request(self, request: str) -> str:
        """Process incoming requests and generate realistic responses."""
        try:
            # Simulate occasional communication errors
            if random.random() < self.config["error_rate"]:
                return "ERROR: Communication failure\n"

            # Parse request (simple protocol: COMMAND [PARAMS])
            parts = request.split()
            command = parts[0].upper() if parts else ""

            if command == "GET_BPM":
                # Simulate BPM detection
                bpm_min, bpm_max = self.config["bpm_range"]
                bpm = random.uniform(bpm_min, bpm_max)
                confidence = random.uniform(0.3, 0.95)
                signal_level = random.uniform(0.2, 0.9)

                return f"BPM:{bpm:.1f}|CONF:{confidence:.2f}|SIG:{signal_level:.2f}|STATUS:OK\n"

            elif command == "GET_STATUS":
                # Return device status
                uptime = int(time.time() - getattr(self, 'start_time', time.time()))
                return f"STATUS:OK|UPTIME:{uptime}|TYPE:{self.device_type}|CLIENTS:{self.connected_clients}\n"

            elif command == "GET_SENSORS":
                # Return available sensors
                sensors = ",".join(self.config["sensor_types"])
                return f"SENSORS:{sensors}\n"

            elif command == "SET_CONFIG":
                # Simulate configuration change
                if len(parts) >= 3:
                    param = parts[1]
                    value = parts[2]
                    return f"CONFIG_SET:{param}={value}|STATUS:OK\n"
                else:
                    return "ERROR: Invalid config command\n"

            elif command == "PING":
                return "PONG\n"

            elif command == "RESET":
                # Simulate device reset
                time.sleep(0.5)
                return "RESET:OK\n"

            else:
                return f"UNKNOWN_COMMAND:{command}\n"

        except Exception as e:
            print(f"Error processing request '{request}': {e}")
            return "ERROR: Internal error\n"

    def stop(self):
        """Stop the hardware emulator server."""
        print("Stopping hardware emulator...")
        self.running = False
        self.status = "stopped"

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None

        # Wait for client threads to finish (with timeout)
        for thread in self.client_threads:
            thread.join(timeout=2.0)

        self.client_threads.clear()
        self.clients.clear()
        self.connected_clients = 0
        print("Hardware emulator stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current emulator status."""
        return {
            "status": self.status,
            "host": self.host,
            "port": self.port,
            "device_type": self.device_type,
            "connected_clients": self.connected_clients,
            "config": self.config
        }


def main():
    print("🧪 Starting ESP32 Hardware Emulator...")

    emulator = HardwareEmulator(host="0.0.0.0", port=12345, device_type="esp32")
    if emulator.start():
        print("✅ Hardware emulator started on port 12345")
        try:
            while emulator.running:
                time.sleep(1)
        except KeyboardInterrupt:
            emulator.stop()
    else:
        print("❌ Failed to start hardware emulator")
        sys.exit(1)

if __name__ == "__main__":
    main()