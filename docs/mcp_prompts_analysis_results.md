# MCP Prompts Analysis Results - ESP32 BPM Detector

## Analysis Date: 2025-12-31

This document contains analysis results using working mcp-prompts templates applied to the ESP32 BPM detector codebase.

## Prompt: `/analysis` - Analysis Assistant

**Applied Variables**:
- Query: "Analyze the ESP32 BPM detector FFT implementation for performance bottlenecks and memory usage patterns"

**Result**: Analysis Assistant prompt retrieved successfully

### Performance Bottleneck Analysis

#### 1. FFT Computation (`performFFT()`)

**Location**: `src/bpm_detector.cpp:445-495`

**Findings**:
- ✅ **Good**: Pre-allocated buffers when `FFT_PREALLOCATE_BUFFERS` is enabled
- ⚠️ **Issue**: Dynamic allocation fallback (`new double[fft_size_]`) can cause heap fragmentation
- ✅ **Good**: Performance monitoring with `PERF_MONITOR_FFT_TIME`
- ⚠️ **Issue**: FFT object created on stack each call - could be member variable

**Memory Usage**:
- FFT buffers: `2 * fft_size_ * sizeof(double)` = 2 * 1024 * 8 = **16KB** (when pre-allocated)
- Sample buffer: `fft_size_ * sizeof(float)` = 1024 * 4 = **4KB**
- FFT magnitude buffer: `(fft_size_/2) * sizeof(float)` = 512 * 4 = **2KB**
- **Total**: ~22KB for FFT processing

**Performance Metrics**:
- FFT computation time tracked: `fft_compute_time_us_`
- Average FFT time: `average_fft_time_ms_` (exponential moving average)
- Window function: Blackman-Harris (good frequency resolution)

#### 2. Buffer Management

**Location**: `src/bpm_detector.cpp:273-290`

**Findings**:
- ⚠️ **Issue**: Linear buffer shift operation - O(n) complexity
  ```cpp
  for (size_t i = 1; i < sample_buffer_.size(); ++i) {
      sample_buffer_[i - 1] = sample_buffer_[i];
  }
  ```
- 💡 **Optimization**: Use circular buffer with index pointer (O(1) insertion)

**Memory Pattern**:
- Buffer pre-allocated with zeros
- `samples_added_` counter tracks actual samples (good design)
- Buffer ready check: `samples_added_ >= fft_size_` (correct)

#### 3. Beat Detection Algorithm

**Location**: `src/bpm_detector.cpp:497-600+`

**Findings**:
- ✅ **Good**: Dual detection modes (basic/advanced)
- ✅ **Good**: Adaptive debounce and threshold
- ✅ **Good**: Beat history tracking for BPM calculation
- ⚠️ **Issue**: `beat_times_` vector can grow (though capped at `BEAT_HISTORY_SIZE`)

**Memory**:
- Beat history: `BEAT_HISTORY_SIZE * sizeof(unsigned long)` = 32 * 4 = **128 bytes**

### Memory Usage Summary

| Component | Size | Notes |
|-----------|------|-------|
| Sample Buffer | 4KB | Pre-allocated, fixed size |
| FFT Real Buffer | 8KB | Pre-allocated when enabled |
| FFT Imag Buffer | 8KB | Pre-allocated when enabled |
| FFT Magnitude Buffer | 2KB | Half-size for real signals |
| Beat History | 128B | Capped at 32 beats |
| **Total FFT Processing** | **~22KB** | Acceptable for ESP32-S3 (512KB RAM) |

### Performance Recommendations

1. **Replace Linear Buffer Shift with Circular Buffer**
   - Current: O(n) per sample insertion
   - Proposed: O(1) with index pointer
   - Impact: Significant for 25kHz sample rate

2. **Make FFT Object a Member Variable**
   - Current: Created on stack each `performFFT()` call
   - Proposed: Reuse FFT object instance
   - Impact: Reduce object construction overhead

3. **Consider Fixed-Point Arithmetic**
   - Current: Floating-point (double precision for FFT)
   - Proposed: Fixed-point for sample processing
   - Impact: Faster computation, less memory

4. **Optimize Window Function**
   - Current: Blackman-Harris (good but computationally expensive)
   - Consider: Hamming (faster, config mentions it)
   - Impact: Faster FFT preprocessing

---

## Prompt: `/code-review` - Code Review Assistant

**Applied Variables**:
- Language: "C++"
- Code: "BPM detector implementation with FFT-based beat detection on ESP32-S3"
- Context: "Real-time audio processing, memory-constrained environment, 25kHz sample rate"

**Result**: Code Review Assistant prompt retrieved successfully

### Code Review Findings

#### 1. Memory Management ✅

**Strengths**:
- Pre-allocation of buffers in constructor
- RAII pattern with vector management
- Conditional compilation for platform differences
- Buffer size validation

**Issues**:
- ⚠️ Dynamic allocation fallback in `performFFT()` (lines 456-457)
  ```cpp
  double* vReal = new double[fft_size_];
  double* vImag = new double[fft_size_];
  ```
  - Should always use pre-allocated buffers on ESP32
  - Consider making `FFT_PREALLOCATE_BUFFERS` mandatory for ESP32

#### 2. Performance ✅

**Strengths**:
- Performance monitoring enabled
- FFT time tracking
- Exponential moving average for metrics

**Issues**:
- ⚠️ Linear buffer shift (O(n)) in `addSample()` (lines 276-279)
  - Should use circular buffer for O(1) insertion
- ⚠️ FFT object recreation on each call
  - Should be member variable

#### 3. Code Quality ✅

**Strengths**:
- Clear separation of concerns
- Interface-based design (`IAudioInput`, `ITimer`)
- Platform abstraction
- Comprehensive logging

**Issues**:
- ⚠️ Magic numbers in envelope detection (0.9f, 0.1f, etc.)
  - Should be configurable constants
- ⚠️ String comparisons for status (line 408)
  - Should use enum for status

#### 4. Real-Time Constraints ✅

**Strengths**:
- Fixed buffer sizes
- Pre-allocated memory
- Performance monitoring

**Issues**:
- ⚠️ Buffer shift operation may cause timing jitter
- ⚠️ FFT computation not interruptible
- Consider: Task priority and CPU affinity

#### 5. Security & Robustness ✅

**Strengths**:
- Null pointer checks
- Buffer bounds checking
- Initialization validation

**Issues**:
- ⚠️ No overflow protection for `samples_added_` counter
- ⚠️ No validation of FFT size constraints

### Code Review Recommendations

#### High Priority

1. **Implement Circular Buffer**
   ```cpp
   // Replace linear shift with circular buffer
   size_t buffer_index_ = 0;
   void addSample(float value) {
       sample_buffer_[buffer_index_] = value;
       buffer_index_ = (buffer_index_ + 1) % fft_size_;
   }
   ```

2. **Make FFT Object Member Variable**
   ```cpp
   // In header
   ArduinoFFT<double>* fft_;  // Or std::unique_ptr
   
   // In constructor
   fft_ = new ArduinoFFT<double>(fft_real_buffer_.data(), 
                                  fft_imag_buffer_.data(), 
                                  fft_size_, sample_rate_);
   ```

3. **Remove Dynamic Allocation Fallback**
   ```cpp
   // Make FFT_PREALLOCATE_BUFFERS mandatory for ESP32
   #ifdef PLATFORM_ESP32
   #ifndef FFT_PREALLOCATE_BUFFERS
   #define FFT_PREALLOCATE_BUFFERS 1
   #endif
   #endif
   ```

#### Medium Priority

4. **Extract Magic Numbers to Constants**
   ```cpp
   // In config.h
   #define ENVELOPE_SMOOTHING_FACTOR 0.9f
   #define ENVELOPE_ATTACK_FACTOR 0.1f
   ```

5. **Use Enum for Status**
   ```cpp
   enum class DetectionStatus {
       INITIALIZING,
       DETECTING,
       LOW_SIGNAL,
       NO_SIGNAL,
       ERROR,
       CALIBRATING
   };
   ```

#### Low Priority

6. **Add Overflow Protection**
   ```cpp
   if (samples_added_ < UINT32_MAX) {
       samples_added_++;
   }
   ```

7. **Validate FFT Size**
   ```cpp
   static_assert((FFT_SIZE & (FFT_SIZE - 1)) == 0, 
                 "FFT_SIZE must be power of 2");
   ```

---

## Configuration Analysis

### Current Configuration (`src/config.h`)

**FFT Settings**:
- `SAMPLE_RATE`: 25000 Hz ✅ (Good for ESP32-S3)
- `FFT_SIZE`: 1024 ✅ (Good balance)
- `FFT_WINDOW_TYPE`: "HAMMING" (config) but code uses Blackman-Harris ⚠️
- `FFT_OVERLAP_RATIO`: 0.5f (not currently used) ⚠️

**BPM Detection**:
- `MIN_BPM`: 60 ✅
- `MAX_BPM`: 200 ✅
- `DETECTION_THRESHOLD`: 0.5 ✅
- `CONFIDENCE_THRESHOLD`: 0.3 ✅

**Memory**:
- `BEAT_HISTORY_SIZE`: 32 ✅
- Buffer pre-allocation: Enabled ✅

### Configuration Recommendations

1. **Align Window Function**
   - Config says "HAMMING" but code uses Blackman-Harris
   - Either update config or make window configurable

2. **Implement Overlap**
   - `FFT_OVERLAP_RATIO` is defined but not used
   - Consider implementing overlap for better temporal resolution

3. **Make Window Configurable**
   ```cpp
   #ifndef FFT_WINDOW_TYPE
   #define FFT_WINDOW_TYPE FFT_WIN_TYP_BLACKMAN_HARRIS
   #endif
   ```

---

## Integration with MCP Prompts

### Using Prompts for Optimization

1. **Query Development Knowledge**:
   ```python
   mcp_unified-dev-tools_query_development_knowledge(
       domain="esp32",
       topic="circular buffer optimization",
       context={"project": "esp32-bpm-detector", "use_case": "audio sampling"}
   )
   ```

2. **Apply Refactoring Prompt**:
   ```
   /refactoring Replace linear buffer shift with circular buffer in BPM detector
   ```

3. **Apply Architecture Prompt**:
   ```
   /architecture Design optimized buffer management for real-time audio processing
   ```

### Capturing Learnings

After implementing optimizations, capture successful patterns:

```python
mcp_unified-dev-tools_capture_development_learning(
    domain="esp32",
    pattern="Circular buffer for O(1) audio sample insertion",
    context="ESP32 BPM detector, 25kHz sample rate, memory-constrained",
    tags=["esp32", "optimization", "circular-buffer", "audio"]
)
```

---

## Summary

### Key Findings

1. **Performance**: FFT implementation is good but buffer management can be optimized
2. **Memory**: Usage is acceptable (~22KB) for ESP32-S3
3. **Code Quality**: Well-structured with good abstractions
4. **Real-Time**: Mostly suitable but buffer shift is a bottleneck

### Priority Actions

1. ✅ **High**: Implement circular buffer (O(1) vs O(n))
2. ✅ **High**: Make FFT object member variable
3. ✅ **Medium**: Remove dynamic allocation fallback
4. ✅ **Medium**: Extract magic numbers to config
5. ✅ **Low**: Add overflow protection and validation

### MCP Prompts Integration

- ✅ `/analysis` - Successfully retrieved and applied
- ✅ `/code-review` - Successfully retrieved and applied
- ✅ Can use `/refactoring` for implementation guidance
- ✅ Can use `/architecture` for design improvements
- ✅ Can query development knowledge for ESP32-specific patterns

---

## Next Steps

1. **Implement Circular Buffer**: Replace linear shift with O(1) circular buffer
2. **Optimize FFT Object**: Make it a member variable
3. **Apply Refactoring Prompt**: Use `/refactoring` for detailed implementation
4. **Test Performance**: Measure improvement after optimizations
5. **Capture Learnings**: Save successful patterns to mcp-prompts


