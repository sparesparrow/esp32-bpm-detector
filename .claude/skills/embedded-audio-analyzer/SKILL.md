---
name: embedded-audio-analyzer
description: Optimize ESP32 audio processing, improve beat detection accuracy, debug signal processing issues
tags: ["esp32", "audio", "embedded", "fft", "signal-processing"]
---

# Embedded Audio Analyzer Skill

## Phase 1: Performance Profiling
1. Analyze current FFT configuration:
   `get_prompt("esp32-fft-configuration-guide", {
     sampleRate: current_sample_rate,
     fftSize: current_fft_size,
     targetBPMRange: [80, 180],  # Common music BPM
     constraints: { maxMemory: 256KB, latency: 100ms }
   })`

2. Profile current performance:
   `start_dynamic_analysis(analyzer="esp32-profile",
     target="bpm_detector", options={
       cpuUsage: true,
       memoryTracking: true,
       latencyMeasurement: true
     })`

## Phase 2: Beat Detection Optimization
1. Test beat detection accuracy:
   `run_test_suite(framework="bpm-accuracy-test",
     input="sample_audio_files")`

2. Get optimization guidance:
   `get_prompt("beat-detection-optimization-strategies", {
     currentAccuracy: accuracy_metrics,
     audioCharacteristics: detected_genres,
     constraints: resource_constraints
   })`

3. Evaluate tradeoffs:
   `get_prompt("esp32-optimization-tradeoffs", {
     factor1: "fft_resolution",
     factor2: "latency",
     constraint: "memory_budget"
   })`

## Phase 3: Signal Processing Refinement
1. Analyze frequency response:
   `get_prompt("audio-signal-analysis-guide", {
     signal: captured_audio,
     analysisGoal: "beat_detection",
     noiseCharacteristics: detected_noise
   })`

2. Optimize preprocessing:
   - Should we add high-pass filter?
   - What's optimal filter order?
   - Get guidance: `get_prompt("audio-preprocessing-selector", {...})`

## Phase 4: Hardware Calibration
1. If accuracy varies by microphone:
   ```
   create_prompt(
     name: "bpm-calibration-${microphoneModel}",
     content: calibration_parameters,
     tags: ["esp32", "bpm-detector", "calibration", mic_model]
   )
   ```

2. Create device-specific optimizations:
   `create_prompt(name: "esp32-variant-optimization-${variant}", ...)`

## Phase 5: Cross-Device Learning
1. When different ESP32 variants show different behaviors:
   - Document variance
   - Create variant-specific prompts
   - Share across all devices

2. When audio preprocessing works well:
   `update_prompt("audio-preprocessing-selector", enhanced_content)`

## Knowledge Capture
- Every successful optimization → stored as prompt
- Every discovered limitation → documented in conditional knowledge
- Every microphone/variant combination → variant-specific parameters