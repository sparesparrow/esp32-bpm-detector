# ESP32 BPM Detector - API Contracts

This document defines the API contracts for the ESP32 BPM Detector embedded system, including safety-critical interfaces, performance guarantees, and error handling protocols.

## Table of Contents
1. [Safety Manager API](#safety-manager-api)
2. [Error Handling API](#error-handling-api)
3. [Memory Safety API](#memory-safety-api)
4. [Watchdog API](#watchdog-api)
5. [Power Management API](#power-management-api)
6. [Performance Profiler API](#performance-profiler-api)
7. [Platform Abstraction API](#platform-abstraction-api)

## Safety Manager API

### Class: `SafetyManager`

**Purpose**: Central coordinator for all safety-critical functions in the embedded system.

#### Constructor
```cpp
SafetyManager();
```

#### Initialization
```cpp
bool initialize(ITimer* timer, LogManager* log_manager, const Config& config = Config{});
```

**Parameters**:
- `timer`: Timer interface for time-based operations (must not be null)
- `log_manager`: Logging interface for error reporting (can be null)
- `config`: Safety configuration (uses defaults if not provided)

**Returns**: `true` if initialization successful, `false` otherwise

**Preconditions**:
- System must be in a stable state
- Timer interface must be functional

**Postconditions**:
- Safety monitoring is active
- Error handler is registered
- Watchdog is initialized (if available)

**Error Handling**:
- Returns `false` if timer is null
- Returns `false` if critical components cannot be allocated

#### Safety Checks Execution
```cpp
bool executeSafetyChecks();
```

**Returns**: `true` if all safety checks pass, `false` if any check fails

**Thread Safety**: Must be called from a single thread (typically main loop)

**Performance**: O(1) - constant time execution

#### Error Reporting
```cpp
bool reportError(ErrorCode code, ErrorSeverity severity, const char* message,
                const char* file = nullptr, int line = 0);
```

**Parameters**:
- `code`: Specific error code from ErrorHandling::ErrorCode
- `severity`: Error severity level
- `message`: Human-readable error description
- `file`: Source file name (optional)
- `line`: Source line number (optional)

**Returns**: `true` if error was handled successfully

**Side Effects**:
- May trigger fail-safe mode for critical errors
- Logs error through logging system
- Updates error statistics

## Error Handling API

### Class: `ErrorHandling`

**Purpose**: Structured error reporting and recovery system.

#### Error Codes
```cpp
enum class ErrorCode : uint16_t {
    SUCCESS = 0,
    MEMORY_ALLOCATION_FAILED = 100,
    AUDIO_INIT_FAILED = 200,
    PLATFORM_INIT_FAILED = 300,
    WATCHDOG_TIMEOUT = 600,
    SYSTEM_RESET_REQUIRED = 603
};
```

#### Error Severities
```cpp
enum class ErrorSeverity : uint8_t {
    DEBUG = 0,      // No action required
    INFO = 1,       // Log only
    WARNING = 2,    // Monitor situation
    ERROR = 3,      // Attempt recovery
    CRITICAL = 4,   // Enter fail-safe mode
    FATAL = 5       // System reset required
};
```

#### Recovery Strategies
```cpp
enum class RecoveryStrategy : uint8_t {
    NONE = 0,           // No recovery possible
    RETRY = 1,          // Retry operation
    RESET_COMPONENT = 2, // Reset affected component
    FAIL_SAFE = 4,      // Enter fail-safe mode
    SYSTEM_RESET = 5    // Full system reset
};
```

## Memory Safety API

### Class: `MemorySafety`

**Purpose**: RAII-based memory management with safety guarantees.

#### Aligned Buffer
```cpp
template<typename T>
class AlignedBuffer {
public:
    explicit AlignedBuffer(size_t count, size_t alignment = MEMORY_ALIGNMENT);
    T* data();
    const T* data() const;
    size_t size() const;
    bool valid() const;
};
```

**Guarantees**:
- Memory is aligned to specified boundary
- Automatic cleanup on destruction
- Null on allocation failure

#### Safe Vector
```cpp
template<typename T>
class SafeVector {
public:
    explicit SafeVector(size_t capacity = 0);
    bool push_back(const T& value);
    T* at(size_t index);
    size_t size() const;
    size_t capacity() const;
    bool full() const;
};
```

**Safety Properties**:
- Bounds checking on all access
- Capacity limits prevent overflow
- Returns nullptr for out-of-bounds access

## Watchdog API

### Interface: `IWatchdog`

**Purpose**: Hardware-independent watchdog timer abstraction.

#### Key Methods
```cpp
virtual bool initialize(uint32_t timeout_ms) = 0;
virtual void feed() = 0;
virtual void forceReset() = 0;
virtual uint32_t getTimeRemaining() const = 0;
virtual bool isActive() const = 0;
```

**Contract**:
- `initialize()` must be called before other methods
- `feed()` must be called regularly to prevent reset
- `forceReset()` will reset the system immediately
- Thread-safe for single-writer, multiple-reader access

## Power Management API

### Class: `PowerManager`

**Purpose**: Intelligent power optimization based on system activity.

#### Power Modes
```cpp
enum class PowerMode {
    PERFORMANCE = 0,    // Maximum performance
    BALANCED = 1,       // Balanced performance/power
    POWERSAVE = 2,      // Power saving
    ULTRA_LOW_POWER = 3 // Extreme power saving
};
```

#### Activity Levels
```cpp
enum class ActivityLevel {
    IDLE = 0,       // System idle
    LOW = 1,        // Low activity
    MODERATE = 2,   // Moderate activity
    HIGH = 3,       // High activity
    CRITICAL = 4    // Critical operations
};
```

#### Key Methods
```cpp
bool initialize(ITimer* timer, const Config& config = Config{});
void updateActivity(ActivityLevel level);
void setPowerMode(PowerMode mode);
void executePowerManagement();
PowerStats getPowerStats() const;
```

**Performance Impact**:
- Mode changes take effect within 1-2 seconds
- CPU frequency scaling: 40-240 MHz range
- Power consumption reduction: up to 80% in low-power mode

## Performance Profiler API

### Class: `PerformanceProfiler`

**Purpose**: Comprehensive performance monitoring and bottleneck detection.

#### Scope Timer (RAII)
```cpp
class ScopeTimer {
public:
    explicit ScopeTimer(PerformanceProfiler* profiler, const char* scope_name);
    ~ScopeTimer(); // Automatically records timing
    void addCheckpoint(const char* checkpoint_name);
};
```

#### Usage Macros
```cpp
#define PERFORMANCE_SCOPE(name) \
    PerformanceProfiler::ScopeTimer scope_timer(g_performance_profiler, name)

#define PERFORMANCE_EVENT(name, value) \
    if (g_performance_profiler) g_performance_profiler->recordEvent(name, value)
```

#### Performance Metrics
```cpp
struct Metrics {
    uint32_t execution_time_us;
    uint32_t memory_used;
    float cpu_utilization;
    uint32_t context_switches;
};
```

**Accuracy**: ±1 microsecond timing resolution

## Platform Abstraction API

### Interface: `IPlatform`

**Purpose**: Hardware-independent platform operations.

#### Result Codes
```cpp
enum class Result {
    SUCCESS = 0,
    ERROR_INVALID_PARAMETER = -1,
    ERROR_HARDWARE_FAILURE = -3,
    ERROR_TIMEOUT = -4,
    ERROR_NOT_SUPPORTED = -5
};
```

#### Key Methods
```cpp
virtual Result initialize() = 0;
virtual bool isInitialized() const = 0;
virtual Result getLastError() const = 0;
virtual void clearError() = 0;
virtual uint32_t getFreeHeap() = 0;
virtual uint64_t getChipId() = 0;
```

**Error Handling**:
- All methods return error codes or safe defaults
- `getLastError()` provides detailed error information
- `clearError()` resets error state
- Methods are fail-safe (never crash on invalid input)

## Thread Safety Guarantees

### Single-Writer, Multiple-Reader (SWMR)
- SafetyManager: SWMR for status access
- ErrorHandling: Thread-safe for error reporting
- MemorySafety: Thread-local or SWMR
- Watchdog: SWMR with atomic operations

### Main Loop Only
- PowerManager: Execute only from main loop
- PerformanceProfiler: Monitoring from single thread
- Platform: Hardware access from single thread

## Memory Management Contracts

### RAII Principle
All resource management follows RAII:
- Automatic cleanup on scope exit
- Exception-safe resource handling
- No manual memory management required

### Memory Limits
- Heap usage: < 50% of total RAM
- Stack usage: < 75% of stack size
- Fragmentation: Monitored and reported

## Error Recovery Contracts

### Recovery Time Objectives (RTO)
- Error detection: < 100ms
- Recovery initiation: < 500ms
- Fail-safe activation: < 1 second
- System reset: < 5 seconds (hardware watchdog)

### Recovery Strategies by Error Type
- Memory errors: Component reset or system reset
- I/O errors: Retry with exponential backoff
- Timing errors: Fail-safe mode activation
- Critical errors: Immediate system reset

## Performance Contracts

### Timing Guarantees
- Audio sampling: 40μs intervals (25kHz)
- Safety checks: < 10ms execution time
- Error handling: < 5ms response time
- Power transitions: < 2 seconds

### Resource Utilization
- CPU: < 80% average utilization
- Memory: < 60% heap utilization
- Flash: < 70% storage utilization
- Power: Adaptive based on activity

## Testing and Validation

### Unit Test Coverage
- All safety-critical functions: 100% branch coverage
- Error handling paths: Complete coverage
- Memory management: Bounds and error case coverage
- Performance profiling: Accuracy validation

### Integration Testing
- End-to-end safety scenarios
- Power management state transitions
- Performance under load conditions
- Error injection and recovery validation

## LED Controller API

### Interface: `ILEDController`

**Purpose**: Abstract interface for LED strip control providing visual feedback for system status and BPM detection.

#### Status Patterns
```cpp
enum class LedStatus {
    LED_STATUS_BOOTING,        // Rainbow cycle during boot
    LED_STATUS_WIFI_CONNECTING, // Blue pulsing during WiFi connection
    LED_STATUS_WIFI_CONNECTED,  // Solid blue when WiFi connected
    LED_STATUS_CLIENT_CONNECTED, // Green pulsing when client connected
    LED_STATUS_ERROR,          // Red blinking on error
    LED_STATUS_BPM_DETECTING   // Normal operation, ready for BPM flash
};
```

#### Initialization
```cpp
virtual bool begin() = 0;
```

**Returns**: `true` if LED controller initialized successfully, `false` otherwise

**Preconditions**:
- GPIO pins must be available for LED control
- Sufficient memory for LED data structures
- FastLED library must be available

**Postconditions**:
- LED strip is configured and ready for use
- Default brightness is set

#### Status Display
```cpp
virtual void showStatus(LedStatus status) = 0;
```

**Parameters**:
- `status`: Current system status to display

**Behavior**:
- Immediately switches to the specified status pattern
- Updates LED display according to pattern timing
- Non-blocking operation

#### BPM Flash
```cpp
virtual void showBPMFlash(int bpm, float confidence) = 0;
```

**Parameters**:
- `bpm`: Current BPM value (60-200 typical range)
- `confidence`: Detection confidence (0.0-1.0)

**Behavior**:
- Flashes white LEDs synchronized to BPM rhythm
- Only flashes when confidence >= CONFIDENCE_THRESHOLD
- Calculates flash timing based on BPM value
- Non-blocking operation

#### Brightness Control
```cpp
virtual void setBrightness(uint8_t brightness) = 0;
```

**Parameters**:
- `brightness`: Brightness level (0-255, where 255 is maximum)

**Behavior**:
- Immediately applies new brightness to all LEDs
- Affects all subsequent LED operations
- Scales all color values by brightness factor

#### Clear LEDs
```cpp
virtual void clear() = 0;
```

**Behavior**:
- Turns off all LEDs immediately
- Clears any active patterns
- Sets LEDs to black/off state

#### Update Patterns
```cpp
virtual void update() = 0;
```

**Purpose**: Updates animated LED patterns (call regularly in main loop)

**Behavior**:
- Advances rainbow cycles, blinking patterns, BPM flashes
- Should be called at ~20Hz (every 50ms) for smooth animation
- Non-blocking operation

### Implementation: `LEDStripController`

**Hardware Requirements**:
- WS2812B or compatible LED strip
- GPIO 21 (DIN pin) connected to LED strip data input
- Power supply capable of 7W maximum (23 LEDs × 60mA × 5V)

**Memory Usage**:
- CRGB array: 23 × 3 = 69 bytes
- Additional overhead: ~100 bytes
- FastLED library: ~2-3KB total

**Timing Constraints**:
- Update interval: 50ms maximum for smooth animation
- BPM flash precision: ±10ms for accurate rhythm
- Pattern switching: Immediate response required

**Error Handling**:
- Initialization failure: Returns false, logs error
- Memory allocation failure: Graceful degradation
- LED strip communication errors: Continues operation with error pattern

**Performance Characteristics**:
- CPU usage: <1% during normal operation
- Memory usage: Minimal (static allocation)
- Power consumption: Variable based on pattern and brightness
- Interrupt safety: Non-blocking operations only