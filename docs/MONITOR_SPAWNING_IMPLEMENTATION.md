# Monitor Spawning Implementation

This document describes the implementation of the monitor spawning system for the ESP32-BPM detector project, generated from ESP32-BPM Android integration and monitor spawning prompt templates.

## Overview

The monitor spawning system allows the ESP32 firmware to manage multiple BPM monitor instances simultaneously, and the Android app to discover, connect to, and manage these monitors.

## Architecture

### ESP32 Firmware Side

#### BPMMonitorManager (`src/bpm_monitor_manager.h` / `.cpp`)

The `BPMMonitorManager` class manages multiple BPM monitor instances:

- **Monitor Spawning**: Create new monitor instances with unique IDs
- **Monitor Management**: Activate/deactivate, rename, and remove monitors
- **Data Access**: Retrieve BPM data from specific monitors
- **Update Callbacks**: Register callbacks for monitor data updates

**Key Features:**
- Each monitor has its own `BPMDetector` and `AudioInput` instance
- Monitors are identified by unique 32-bit IDs
- Monitors can be named for easier identification
- Active/inactive state management

#### API Endpoints (`src/api_endpoints.cpp`)

New REST API endpoints for monitor management:

- `GET /api/v1/monitors` - List all monitors
- `GET /api/v1/monitors/get?id=X` - Get specific monitor data
- `POST /api/v1/monitors/spawn` - Spawn new monitor (with optional name)
- `DELETE /api/v1/monitors/remove?id=X` - Remove monitor
- `PUT /api/v1/monitors/update?id=X&active=true` - Update monitor (activate/deactivate, rename)

### Android App Side

#### BPMMonitor Model (`android-app/.../models/BPMMonitor.kt`)

Data class representing a monitor instance:
- Monitor ID, name, active state
- Current BPM data
- Connection status helpers

#### MonitorApiClient (`android-app/.../network/MonitorApiClient.kt`)

API client for monitor management:
- `listMonitors()` - Fetch all monitors from ESP32
- `getMonitor(id)` - Get specific monitor data
- `spawnMonitor(name)` - Create new monitor
- `removeMonitor(id)` - Delete monitor
- `updateMonitor(id, active, name)` - Update monitor state

#### MonitorManagerViewModel (`android-app/.../viewmodels/MonitorManagerViewModel.kt`)

ViewModel for managing monitors in the Android app:
- StateFlow for monitors list
- Loading and error states
- Methods for spawning, removing, updating monitors
- Automatic refresh after operations

## Usage Examples

### ESP32 Firmware

```cpp
#include "bpm_monitor_manager.h"

// Create monitor manager
sparetools::bpm::BPMMonitorManager monitorManager;

// Spawn a new monitor
uint32_t monitorId = monitorManager.spawnMonitor("Main Monitor");

// Update monitors in main loop
void loop() {
    monitorManager.updateAllMonitors();
    // ... rest of loop
}

// Get monitor data
auto data = monitorManager.getMonitorData(monitorId);
```

### Android App

```kotlin
// Initialize monitor manager
val monitorViewModel = MonitorManagerViewModel(application)
monitorViewModel.initialize("192.168.4.1")

// Spawn a new monitor
monitorViewModel.spawnMonitor("My Monitor") { result ->
    result.onSuccess { monitor ->
        Log.d("Monitor", "Spawned monitor ${monitor.id}")
    }
}

// Observe monitors list
monitorViewModel.monitors.collect { monitors ->
    monitors.forEach { monitor ->
        Log.d("Monitor", "${monitor.name}: ${monitor.getBpmString()} BPM")
    }
}
```

## Integration with Existing Code

### Updating main.cpp

To integrate the monitor manager into the firmware:

1. Include the monitor manager header:
```cpp
#include "bpm_monitor_manager.h"
```

2. Create monitor manager instance:
```cpp
sparetools::bpm::BPMMonitorManager* monitorManager = nullptr;
```

3. Initialize in setup():
```cpp
monitorManager = new sparetools::bpm::BPMMonitorManager();
// Spawn default monitor
monitorManager->spawnMonitor("Default Monitor");
```

4. Update API endpoints setup:
```cpp
setupApiEndpoints(server, bpmDetector, monitorManager);
```

5. Update monitors in loop():
```cpp
if (monitorManager) {
    monitorManager->updateAllMonitors();
}
```

## API Response Formats

### List Monitors
```json
[
  {
    "id": 1,
    "name": "Main Monitor",
    "active": true,
    "bpm": 128.5,
    "confidence": 0.85,
    "status": "detecting"
  }
]
```

### Get Monitor
```json
{
  "id": 1,
  "name": "Main Monitor",
  "active": true,
  "bpm": 128.5,
  "confidence": 0.85,
  "signal_level": 0.75,
  "status": "detecting",
  "timestamp": 1234567890
}
```

### Spawn Monitor Response
```json
{
  "id": 2,
  "name": "New Monitor",
  "status": "spawned"
}
```

## Future Enhancements

1. **WebSocket Support**: Real-time monitor data streaming
2. **Monitor Groups**: Organize monitors into groups
3. **Monitor Templates**: Pre-configured monitor settings
4. **Cross-Device Monitoring**: Monitor multiple ESP32 devices from one Android app
5. **Monitor Statistics**: Track monitor performance over time

## Testing

### ESP32 Firmware Tests

Test monitor spawning and management:
```cpp
// Test monitor spawning
uint32_t id1 = monitorManager.spawnMonitor("Test 1");
assert(id1 > 0);

// Test monitor data retrieval
auto data = monitorManager.getMonitorData(id1);
assert(data.status != "not_found");

// Test monitor removal
bool removed = monitorManager.removeMonitor(id1);
assert(removed);
```

### Android App Tests

Test monitor API client:
```kotlin
@Test
fun testSpawnMonitor() = runTest {
    val client = MonitorApiClient.createWithIp("192.168.4.1")
    val result = client.spawnMonitor("Test Monitor")
    assertTrue(result.isSuccess)
    val monitor = result.getOrNull()
    assertNotNull(monitor)
    assertTrue(monitor!!.id > 0)
}
```

## Related Documentation

- ESP32-BPM Android Integration: See Android app documentation
- API Endpoints: See `src/api_endpoints.h` for endpoint documentation
- BPM Detection: See `src/bpm_detector.h` for detection algorithm
