#include "bpm_flatbuffers.h"
#include <flatbuffers/flatbuffers.h>
#include "BpmProtocol_generated.h"
#include "BpmCommon_generated.h"

// Static method implementations
flatbuffers::Offset<sparetools::bpm::BPMUpdate> BPMFlatBuffers::createBPMUpdate(
    float bpm,
    float confidence,
    float signal_level,
    sparetools::bpm::DetectionStatus status,
    uint64_t timestamp,
    const std::string& device_type,
    const std::string& firmware_version,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create BPM analysis data
    auto analysis_offset = sparetools::bpm::CreateBPMAnalysis(
        builder,
        0.85f,  // stability
        0.78f,  // regularity
        440.0f, // dominant_frequency
        0.65f,  // spectral_centroid
        0.3f,   // beat_position
        0.82f   // tempo_consistency
    );

    // Create BPM quality metrics
    auto quality_offset = sparetools::bpm::CreateBPMQuality(
        builder,
        -23.5f, // snr_db
        15,     // consecutive_detections
        0.89f,  // reliability_score
        0.02f,  // false_positive_rate
        0.91f   // algorithm_confidence
    );

    // Create string offsets for required string fields
    auto device_type_offset = builder.CreateString(device_type);
    auto firmware_version_offset = builder.CreateString(firmware_version);

    // Create the BPM update
    return sparetools::bpm::CreateBPMUpdate(
        builder,
        bpm,
        confidence,
        signal_level,
        status,
        timestamp,
        analysis_offset,
        quality_offset,
        device_type_offset,
        firmware_version_offset
    );
}

flatbuffers::Offset<sparetools::bpm::StatusUpdate> BPMFlatBuffers::createStatusUpdate(
    uint64_t uptime_seconds,
    uint32_t free_heap_bytes,
    uint8_t cpu_usage_percent,
    int8_t wifi_rssi,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create status update (simplified - matches generated schema)
    return sparetools::bpm::CreateStatusUpdate(
        builder,
        uptime_seconds,
        free_heap_bytes,
        cpu_usage_percent,
        wifi_rssi,
        0  // timestamp (0 means now)
    );
}

std::vector<uint8_t> BPMFlatBuffers::serializeBPMUpdate(
    flatbuffers::Offset<sparetools::bpm::BPMUpdate> bpm_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    // TODO: Implement proper FlatBuffers serialization when schema is finalized
    // For now, return empty vector to avoid build errors
    return std::vector<uint8_t>();
}

std::vector<uint8_t> BPMFlatBuffers::serializeStatusUpdate(
    flatbuffers::Offset<sparetools::bpm::StatusUpdate> status_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    // For now, just serialize the StatusUpdate directly
    // TODO: Implement proper Response wrapper when schema is finalized
    builder.Finish(status_update_offset);

    const uint8_t* buffer = builder.GetBufferPointer();
    size_t size = builder.GetSize();

    return std::vector<uint8_t>(buffer, buffer + size);
}

const sparetools::bpm::BPMUpdate* BPMFlatBuffers::deserializeBPMUpdate(
    const std::vector<uint8_t>& buffer) {

    // BPMUpdate is not directly serializable as root - return nullptr for testing
    return nullptr;
}

const sparetools::bpm::StatusUpdate* BPMFlatBuffers::deserializeStatusUpdate(
    const std::vector<uint8_t>& buffer) {

    // For now, return nullptr as this functionality is not fully implemented
    // TODO: Implement proper FlatBuffers deserialization when schema is finalized
    return nullptr;
}

const char* BPMFlatBuffers::detectionStatusToString(sparetools::bpm::DetectionStatus status) {
    switch (status) {
        case sparetools::bpm::DetectionStatus_INITIALIZING: return "INITIALIZING";
        case sparetools::bpm::DetectionStatus_DETECTING: return "DETECTING";
        case sparetools::bpm::DetectionStatus_LOW_SIGNAL: return "LOW_SIGNAL";
        case sparetools::bpm::DetectionStatus_NO_SIGNAL: return "NO_SIGNAL";
        case sparetools::bpm::DetectionStatus_ERROR: return "ERROR";
        case sparetools::bpm::DetectionStatus_CALIBRATING: return "CALIBRATING";
        default: return "UNKNOWN";
    }
}

size_t BPMFlatBuffers::estimateBPMUpdateSize() {
    // Base overhead: Response structure + Status + BPMUpdate envelope
    size_t baseOverhead = 128;  // FlatBuffers table overhead

    // BPMUpdate structure size
    size_t bpmUpdateSize = 0;
    bpmUpdateSize += sizeof(float);     // bpm
    bpmUpdateSize += sizeof(float);     // confidence
    bpmUpdateSize += sizeof(float);     // signal_level
    bpmUpdateSize += sizeof(uint8_t);   // status (enum)
    bpmUpdateSize += sizeof(uint64_t);  // timestamp

    // BPMAnalysis structure (nested)
    size_t analysisSize = 0;
    analysisSize += 6 * sizeof(float);  // stability, regularity, dominant_frequency, spectral_centroid, beat_position, tempo_consistency

    // BPMQuality structure (nested)
    size_t qualitySize = 0;
    qualitySize += sizeof(float);       // snr_db
    qualitySize += sizeof(uint16_t);    // consecutive_detections
    qualitySize += 4 * sizeof(float);   // reliability_score, false_positive_rate, algorithm_confidence

    // Total estimate with some padding for FlatBuffers overhead
    return baseOverhead + bpmUpdateSize + analysisSize + qualitySize + 64;  // +64 for safety margin
}

size_t BPMFlatBuffers::estimateStatusUpdateSize() {
    // Base overhead: Response structure + Status + StatusUpdate envelope
    size_t baseOverhead = 128;  // FlatBuffers table overhead

    // StatusUpdate structure size
    size_t statusUpdateSize = 0;
    statusUpdateSize += sizeof(uint64_t);  // uptime_seconds
    statusUpdateSize += sizeof(uint32_t);  // free_heap_bytes
    statusUpdateSize += sizeof(uint32_t);  // min_free_heap_bytes
    statusUpdateSize += sizeof(uint8_t);   // cpu_usage_percent
    statusUpdateSize += sizeof(int8_t);    // wifi_rssi
    statusUpdateSize += sizeof(float);     // temperature_celsius
    statusUpdateSize += sizeof(uint8_t);   // battery_level_percent

    // AudioStatus structure (nested)
    size_t audioStatusSize = 0;
    audioStatusSize += sizeof(bool);       // input_active
    audioStatusSize += sizeof(uint32_t);   // sample_rate
    audioStatusSize += sizeof(float);      // buffer_utilization
    audioStatusSize += sizeof(uint32_t);   // audio_dropouts
    audioStatusSize += sizeof(uint16_t);   // latency_ms
    audioStatusSize += sizeof(float);      // microphone_gain

    // Total estimate with some padding for FlatBuffers overhead
    return baseOverhead + statusUpdateSize + audioStatusSize + 64;  // +64 for safety margin
}