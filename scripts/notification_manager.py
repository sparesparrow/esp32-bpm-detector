#!/usr/bin/env python3
"""
Notification Manager for Learning Loop Workflow

Provides multi-sensory feedback:
- Terminal windows for log monitoring
- scrcpy for Android device mirroring
- eSpeak for audio notifications
- Zigbee lights via MQTT (Zigbee2MQTT) or serial fallback
"""

import os
import sys
import subprocess
import time
import threading
import logging
from pathlib import Path
from typing import Optional, List, Dict
import json

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages notifications across multiple channels."""
    
    def __init__(
        self,
        zigbee_mqtt_broker: str = 'localhost',
        zigbee_mqtt_port: int = 1883,
        zigbee_serial_port: str = '/dev/ttyACM1',
        zigbee_serial_baud: int = 115200,
        light_names: Optional[List[str]] = None,
        enable_mqtt: bool = True,
        enable_serial: bool = False
    ):
        """
        Initialize NotificationManager.
        
        Args:
            zigbee_mqtt_broker: MQTT broker for Zigbee2MQTT
            zigbee_mqtt_port: MQTT broker port
            zigbee_serial_port: Serial port for direct Zigbee control (fallback)
            zigbee_serial_baud: Serial baud rate
            light_names: List of Zigbee light friendly names (auto-discovered if None)
            enable_mqtt: Enable MQTT-based Zigbee control
            enable_serial: Enable serial-based Zigbee control (fallback)
        """
        self.zigbee_mqtt_broker = zigbee_mqtt_broker
        self.zigbee_mqtt_port = zigbee_mqtt_port
        self.zigbee_serial_port = zigbee_serial_port
        self.zigbee_serial_baud = zigbee_serial_baud
        self.light_names = light_names or []
        self.enable_mqtt = enable_mqtt
        self.enable_serial = enable_serial
        
        # MQTT client (lazy-loaded)
        self.mqtt_client = None
        self.mqtt_connected = False
        
        # Serial connection (lazy-loaded)
        self.serial_conn = None
        
        # Terminal windows tracking
        self.terminal_windows = []
        
        # scrcpy process
        self.scrcpy_process = None
        
        # Initialize Zigbee if enabled
        if self.enable_mqtt:
            self._init_mqtt()
        elif self.enable_serial:
            self._init_serial()
    
    def _init_mqtt(self):
        """Initialize MQTT connection for Zigbee2MQTT."""
        try:
            import paho.mqtt.client as mqtt
            
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_mqtt_connect
            self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
            
            try:
                self.mqtt_client.connect(self.zigbee_mqtt_broker, self.zigbee_mqtt_port, 60)
                self.mqtt_client.loop_start()
                time.sleep(1)  # Wait for connection
                
                if self.mqtt_connected:
                    logger.info(f"Connected to MQTT broker at {self.zigbee_mqtt_broker}:{self.zigbee_mqtt_port}")
                    # Auto-discover lights if not provided
                    if not self.light_names:
                        self._discover_lights()
                else:
                    logger.warning("MQTT connection failed, falling back to serial")
                    self.enable_mqtt = False
                    if self.enable_serial:
                        self._init_serial()
            except Exception as e:
                logger.warning(f"MQTT initialization failed: {e}, falling back to serial")
                self.enable_mqtt = False
                if self.enable_serial:
                    self._init_serial()
        except ImportError:
            logger.warning("paho-mqtt not installed, MQTT disabled")
            self.enable_mqtt = False
            if self.enable_serial:
                self._init_serial()
    
    def _on_mqtt_connect(self, client, userdata, flags, rc, *args, **kwargs):
        """MQTT connection callback."""
        if rc == 0:
            self.mqtt_connected = True
            logger.info("MQTT connected successfully")
        else:
            self.mqtt_connected = False
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc, *args, **kwargs):
        """MQTT disconnection callback."""
        self.mqtt_connected = False
        logger.warning("MQTT disconnected")
    
    def _discover_lights(self):
        """Discover Zigbee lights via MQTT."""
        if not self.mqtt_connected:
            return
        
        try:
            # Request device list
            self.mqtt_client.publish("zigbee2mqtt/bridge/request/devices", "")
            time.sleep(2)  # Wait for response
            
            # Subscribe to device announcements
            self.mqtt_client.subscribe("zigbee2mqtt/bridge/devices")
            
            # For now, use a simple approach - in production, parse MQTT messages
            # This is a placeholder - you'd need to implement proper MQTT message handling
            logger.info("Light discovery initiated (check Zigbee2MQTT for available lights)")
        except Exception as e:
            logger.error(f"Light discovery failed: {e}")
    
    def _init_serial(self):
        """Initialize serial connection for direct Zigbee control."""
        try:
            import serial
            
            if os.path.exists(self.zigbee_serial_port):
                self.serial_conn = serial.Serial(
                    self.zigbee_serial_port,
                    self.zigbee_serial_baud,
                    timeout=1
                )
                logger.info(f"Connected to Zigbee serial port at {self.zigbee_serial_port}")
            else:
                logger.warning(f"Zigbee serial port {self.zigbee_serial_port} not found")
        except ImportError:
            logger.warning("pyserial not installed, serial control disabled")
        except Exception as e:
            logger.warning(f"Serial initialization failed: {e}")
    
    def speak(self, text: str, run_async: bool = True):
        """
        Announce text using eSpeak.
        
        Args:
            text: Text to speak
            run_async: Run in background thread (default: True)
        """
        def _speak():
            try:
                subprocess.run(
                    ['espeak', '-v', 'en', '-s', '150', text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10
                )
            except FileNotFoundError:
                logger.warning(f"eSpeak not found. Would say: '{text}'")
            except subprocess.TimeoutExpired:
                logger.warning("eSpeak command timed out")
            except Exception as e:
                logger.error(f"eSpeak error: {e}")
        
        if run_async:
            threading.Thread(target=_speak, daemon=True).start()
        else:
            _speak()
    
    def set_light_color(self, color: str, blink: bool = False, brightness: int = 254):
        """
        Set Zigbee light color.
        
        Args:
            color: Color name (red, green, blue, yellow, orange, purple, white) or RGB tuple
            blink: Whether to blink the light
            brightness: Brightness level (0-254)
        """
        if not self.light_names:
            logger.debug("No lights configured, skipping light control")
            return
        
        # Color name to RGB mapping
        color_map = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'white': (255, 255, 255),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
        }
        
        if isinstance(color, str):
            color = color.lower()
            rgb = color_map.get(color, (255, 255, 255))  # Default to white
        else:
            rgb = color
        
        if self.enable_mqtt and self.mqtt_connected:
            self._set_light_mqtt(rgb, blink, brightness)
        elif self.serial_conn:
            self._set_light_serial(rgb, blink, brightness)
        else:
            logger.debug("No Zigbee connection available for light control")
    
    def _set_light_mqtt(self, rgb: tuple, blink: bool, brightness: int):
        """Set light color via MQTT."""
        r, g, b = rgb
        
        payload = {
            'color': {'r': r, 'g': g, 'b': b},
            'brightness': brightness,
            'state': 'ON'
        }
        
        if blink:
            payload['effect'] = 'blink'
        
        for light_name in self.light_names:
            try:
                topic = f"zigbee2mqtt/{light_name}/set"
                self.mqtt_client.publish(topic, json.dumps(payload))
                logger.debug(f"Set light {light_name} to RGB({r},{g},{b}) via MQTT")
            except Exception as e:
                logger.error(f"Failed to set light {light_name} via MQTT: {e}")
    
    def _set_light_serial(self, rgb: tuple, blink: bool, brightness: int):
        """Set light color via serial (simple protocol)."""
        r, g, b = rgb
        command = f"BLINK {r},{g},{b}\n" if blink else f"COLOR {r},{g},{b}\n"
        
        try:
            self.serial_conn.write(command.encode('utf-8'))
            logger.debug(f"Set light to RGB({r},{g},{b}) via serial")
        except Exception as e:
            logger.error(f"Failed to set light via serial: {e}")
            # Try to reconnect
            self._init_serial()
    
    def start_scrcpy(self, max_size: int = 1024, window_title: str = "Android Device"):
        """
        Start scrcpy for Android device mirroring.
        
        Args:
            max_size: Maximum window size
            window_title: Window title
        """
        try:
            # Check if scrcpy is already running
            result = subprocess.run(
                ['pgrep', '-x', 'scrcpy'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:
                logger.debug("scrcpy already running")
                return
            
            # Check for connected Android devices
            try:
                adb_output = subprocess.check_output(
                    ['adb', 'devices'],
                    timeout=5
                ).decode().strip()
                
                lines = [l for l in adb_output.split('\n') if l.strip() and 'device' in l]
                if len(lines) <= 1:  # Only header line
                    logger.debug("No Android device connected for scrcpy")
                    return
                
                logger.info("Starting scrcpy...")
                self.scrcpy_process = subprocess.Popen(
                    [
                        'scrcpy',
                        '--no-audio',
                        f'--max-size={max_size}',
                        f'--window-title={window_title}'
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                logger.info("scrcpy started successfully")
            except subprocess.TimeoutExpired:
                logger.warning("ADB command timed out")
            except FileNotFoundError:
                logger.warning("adb or scrcpy not installed")
            except Exception as e:
                logger.error(f"Failed to start scrcpy: {e}")
        except FileNotFoundError:
            logger.warning("pgrep not found, cannot check for running scrcpy")
    
    def spawn_terminal(self, command: str, title: str = "Monitor", keep_open: bool = True):
        """
        Spawn a new terminal window running a command.
        
        Args:
            command: Command to run
            title: Window title
            keep_open: Keep terminal open after command completes
        """
        try:
            if keep_open:
                # Use bash to keep window open
                full_command = f"bash -c '{command}; exec bash'"
            else:
                full_command = command
            
            # Try different terminal emulators
            terminal_commands = [
                ['gnome-terminal', f'--title={title}', '--', 'bash', '-c', full_command],
                ['xterm', '-T', title, '-e', 'bash', '-c', full_command],
                ['x-terminal-emulator', '-T', title, '-e', 'bash', '-c', full_command],
            ]
            
            for term_cmd in terminal_commands:
                try:
                    process = subprocess.Popen(
                        term_cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    self.terminal_windows.append(process)
                    logger.info(f"Spawned terminal window: {title}")
                    return
                except FileNotFoundError:
                    continue
            
            logger.warning(f"Could not spawn terminal window. No terminal emulator found.")
        except Exception as e:
            logger.error(f"Failed to spawn terminal: {e}")
    
    def monitor_logs(self, log_file: str, title: str = "Log Monitor"):
        """
        Spawn a terminal window tailing a log file.
        
        Args:
            log_file: Path to log file
            title: Window title
        """
        log_path = Path(log_file)
        if not log_path.exists():
            logger.warning(f"Log file not found: {log_file}")
            return
        
        command = f"tail -f '{log_file}'"
        self.spawn_terminal(command, title)
    
    def monitor_serial(self, port: str, baud: int = 115200, title: str = "Serial Monitor"):
        """
        Spawn a terminal window monitoring a serial port.
        
        Args:
            port: Serial port path
            baud: Baud rate
            title: Window title
        """
        command = f"pio device monitor --port {port} --baud {baud}"
        self.spawn_terminal(command, title)
    
    def notify_phase_start(self, phase: str):
        """Notify that a phase has started."""
        self.speak(f"Starting {phase}")
        self.set_light_color("blue", blink=True)
        logger.info(f"Phase started: {phase}")
    
    def notify_success(self, message: str = "Operation completed successfully"):
        """Notify of success."""
        self.speak(message)
        self.set_light_color("green")
        logger.info(f"Success: {message}")
    
    def notify_failure(self, message: str = "Operation failed"):
        """Notify of failure."""
        self.speak(message)
        self.set_light_color("red", blink=True)
        logger.error(f"Failure: {message}")
    
    def notify_warning(self, message: str = "Warning"):
        """Notify of warning."""
        self.speak(message)
        self.set_light_color("yellow")
        logger.warning(f"Warning: {message}")
    
    def notify_learning_progress(self, phase: str, progress: float, total: int = None):
        """
        Notify learning loop progress.
        
        Args:
            phase: Current phase name
            progress: Progress value (0.0-1.0) or current step number
            total: Total steps (if progress is step number)
        """
        if total:
            progress_pct = (progress / total) * 100
            message = f"{phase}: {progress}/{total} ({progress_pct:.0f}%)"
        else:
            progress_pct = progress * 100
            message = f"{phase}: {progress_pct:.0f}% complete"
        
        # Use different colors based on progress
        if progress_pct < 33:
            color = "blue"
        elif progress_pct < 66:
            color = "cyan"
        else:
            color = "green"
        
        self.set_light_color(color, blink=False)
        logger.info(f"Learning progress: {message}")
    
    def notify_prompt_improvement(self, prompt_id: str, improvement_type: str = "enhanced"):
        """
        Notify when a prompt is improved.
        
        Args:
            prompt_id: ID of the improved prompt
            improvement_type: Type of improvement (enhanced, optimized, fixed)
        """
        message = f"Prompt {prompt_id} {improvement_type}"
        self.speak(message)
        self.set_light_color("purple", blink=True)
        logger.info(f"Prompt improvement: {message}")
    
    def monitor_learning_logs(self, log_dir: str, title: str = "Learning Logs"):
        """
        Spawn terminal window monitoring learning loop logs.
        
        Args:
            log_dir: Directory containing log files
            title: Window title
        """
        log_path = Path(log_dir)
        if not log_path.exists():
            logger.warning(f"Log directory not found: {log_dir}")
            return
        
        # Find most recent log file or tail all logs
        log_files = sorted(log_path.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_files:
            command = f"tail -f '{log_files[0]}'"
        else:
            command = f"tail -f {log_dir}/*.log 2>/dev/null || echo 'No log files found'"
        
        self.spawn_terminal(command, title)
    
    def notify_cycle_start(self, cycle_num: int, total_cycles: int = None):
        """Notify that a learning cycle has started."""
        if total_cycles:
            message = f"Starting learning cycle {cycle_num} of {total_cycles}"
        else:
            message = f"Starting learning cycle {cycle_num}"
        
        self.speak(message)
        self.set_light_color("blue", blink=True)
        logger.info(f"Cycle started: {message}")
    
    def notify_cycle_complete(self, cycle_num: int, success: bool, duration_seconds: float = None):
        """Notify that a learning cycle has completed."""
        if success:
            message = f"Cycle {cycle_num} completed successfully"
            if duration_seconds:
                message += f" in {duration_seconds:.1f} seconds"
            self.speak(message)
            self.set_light_color("green")
        else:
            message = f"Cycle {cycle_num} completed with errors"
            self.speak(message)
            self.set_light_color("red", blink=True)
        
        logger.info(f"Cycle complete: {message}")
    
    def notify_interaction_recorded(self, prompt_id: str, success: bool):
        """Notify when an interaction is recorded."""
        status = "successful" if success else "failed"
        logger.debug(f"Interaction recorded: {prompt_id} - {status}")
        # Don't speak every interaction to avoid spam, but log it
    
    def notify_analysis_complete(self, prompt_id: str, improvements: int = 0):
        """Notify when prompt analysis is complete."""
        if improvements > 0:
            message = f"Analysis complete for {prompt_id}, {improvements} improvements found"
            self.speak(message)
            self.set_light_color("purple", blink=True)
        else:
            logger.info(f"Analysis complete for {prompt_id}, no improvements needed")
    
    def cleanup(self):
        """Clean up resources."""
        # Stop scrcpy if running
        if self.scrcpy_process:
            try:
                self.scrcpy_process.terminate()
                self.scrcpy_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.scrcpy_process.kill()
            except Exception as e:
                logger.error(f"Error stopping scrcpy: {e}")
        
        # Disconnect MQTT
        if self.mqtt_client and self.mqtt_connected:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting MQTT: {e}")
        
        # Close serial
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except Exception as e:
                logger.error(f"Error closing serial: {e}")
        
        logger.info("NotificationManager cleaned up")
