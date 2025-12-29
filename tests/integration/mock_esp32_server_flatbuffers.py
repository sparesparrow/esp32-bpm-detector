#!/usr/bin/env python3
"""
Mock ESP32 BPM Detector API Server for Testing
Returns FlatBuffers binary data matching Android app expectations
"""

import time
import sys
import os
from flask import Flask, Response
import flatbuffers

# Add the generated Python classes to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../android-app/app/src/main/python'))

try:
    from sparetools.bpm import BPMUpdate, StatusUpdate, ConfigUpdate, BPMConfig
    from sparetools.bpm.DetectionStatus import DetectionStatus
except ImportError as e:
    print(f"Failed to import FlatBuffers classes: {e}")
    print("Make sure to run: flatc --python -o android-app/app/src/main/python schemas/bpm_protocol.fbs")
    sys.exit(1)

app = Flask(__name__)

def create_bpm_update():
    """Create a FlatBuffers BPMUpdate message"""
    builder = flatbuffers.Builder(1024)

    # Create BPMUpdate
    BPMUpdate.Start(builder)
    BPMUpdate.AddBpm(builder, 128.5)
    BPMUpdate.AddConfidence(builder, 0.87)
    BPMUpdate.AddSignalLevel(builder, 0.72)
    BPMUpdate.AddStatus(builder, DetectionStatus.DETECTING)
    # Skip analysis and quality for simplicity
    BPMUpdate.AddTimestamp(builder, int(time.time() * 1000))
    bpm_update = BPMUpdate.End(builder)

    builder.Finish(bpm_update)
    return builder.Output()

def create_config_update():
    """Create a FlatBuffers ConfigUpdate message"""
    builder = flatbuffers.Builder(1024)

    # Create BPMConfig
    BPMConfig.Start(builder)
    BPMConfig.AddMinBpm(builder, 60)
    BPMConfig.AddMaxBpm(builder, 200)
    BPMConfig.AddConfidenceThreshold(builder, 0.7)
    BPMConfig.AddStabilityWeight(builder, 0.3)
    BPMConfig.AddRegularityWeight(builder, 0.4)
    BPMConfig.AddQualityWeight(builder, 0.3)
    bpm_config = BPMConfig.End(builder)

    # Create ConfigUpdate
    ConfigUpdate.Start(builder)
    ConfigUpdate.AddBpmConfig(builder, bpm_config)
    # Skip other configs for simplicity
    config_update = ConfigUpdate.End(builder)

    builder.Finish(config_update)
    return builder.Output()

def create_status_update():
    """Create a FlatBuffers StatusUpdate message"""
    builder = flatbuffers.Builder(1024)

    # Create StatusUpdate
    StatusUpdate.Start(builder)
    StatusUpdate.AddUptimeSeconds(builder, int(time.time()))
    StatusUpdate.AddFreeHeapBytes(builder, 245760)
    StatusUpdate.AddMinFreeHeapBytes(builder, 240000)
    StatusUpdate.AddCpuUsagePercent(builder, 15)
    StatusUpdate.AddWifiRssi(builder, -50)
    # Skip audio_status for simplicity
    StatusUpdate.AddTemperatureCelsius(builder, 25.0)
    StatusUpdate.AddBatteryLevelPercent(builder, 85)
    status_update = StatusUpdate.End(builder)

    builder.Finish(status_update)
    return builder.Output()

@app.route('/api/bpm', methods=['GET'])
def get_bpm():
    """Return BPM data as FlatBuffers binary"""
    data = create_bpm_update()
    return Response(bytes(data), mimetype='application/octet-stream')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Return settings as FlatBuffers binary"""
    data = create_config_update()
    return Response(bytes(data), mimetype='application/octet-stream')

@app.route('/api/health', methods=['GET'])
def get_health():
    """Return health status as FlatBuffers binary"""
    data = create_status_update()
    return Response(bytes(data), mimetype='application/octet-stream')

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify server is working"""
    return {
        "status": "Mock ESP32 server running",
        "endpoints": [
            "/api/bpm - BPM data (FlatBuffers)",
            "/api/settings - Settings (FlatBuffers)",
            "/api/health - Health status (FlatBuffers)"
        ],
        "timestamp": int(time.time() * 1000)
    }

if __name__ == '__main__':
    print("Starting Mock ESP32 BPM Detector API Server (FlatBuffers)...")
    print("Endpoints:")
    print("  GET /api/bpm - BPM data (FlatBuffers binary)")
    print("  GET /api/settings - Settings (FlatBuffers binary)")
    print("  GET /api/health - Health status (FlatBuffers binary)")
    print("  GET /api/test - Test endpoint (JSON)")
    print("")
    print("Android app should connect to: http://127.0.0.1:9090")
    app.run(host='0.0.0.0', port=9090, debug=False)