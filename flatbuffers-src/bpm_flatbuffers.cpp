#include "bpm_flatbuffers.h"
#include <flatbuffers/flatbuffers.h>
#include "bpm_protocol_generated.h"

// Static method implementations
flatbuffers::Offset<IcdBpm::BPMUpdate> BPMFlatBuffers::createBPMUpdate(
    float bpm,
    float confidence,
    float signal_level,
    IcdBpm::DetectionStatus status,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create BPM analysis data
    auto analysis_offset = IcdBpm::CreateBPMAnalysis(
        builder,
        0.85f,  // stability
        0.78f,  // regularity
        440.0f, // dominant_frequency
        0.65f,  // spectral_centroid
        0.3f,   // beat_position
        0.82f   // tempo_consistency
    );

    // Create BPM quality metrics
    auto quality_offset = IcdBpm::CreateBPMQuality(
        builder,
        -23.5f, // snr_db
        15,     // consecutive_detections
        0.89f,  // reliability_score
        0.02f,  // false_positive_rate
        0.91f   // algorithm_confidence
    );

    // Create the BPM update
    return IcdBpm::CreateBPMUpdate(
        builder,
        bpm,
        confidence,
        signal_level,
        status,
        analysis_offset,
        quality_offset
    );
}

flatbuffers::Offset<IcdBpm::StatusUpdate> BPMFlatBuffers::createStatusUpdate(
    uint64_t uptime_seconds,
    uint32_t free_heap_bytes,
    uint8_t cpu_usage_percent,
    int8_t wifi_rssi,
    flatbuffers::FlatBufferBuilder& builder) {

    // Create audio status
    auto audio_status_offset = IcdBpm::CreateAudioStatus(
        builder,
        true,   // input_active
        25000,  // sample_rate
        0.75f,  // buffer_utilization
        0,      // audio_dropouts
        45,     // latency_ms
        0.8f    // microphone_gain
    );

    // Create status update
    return IcdBpm::CreateStatusUpdate(
        builder,
        uptime_seconds,
        free_heap_bytes,
        free_heap_bytes / 4, // min_free_heap
        cpu_usage_percent,
        wifi_rssi,
        audio_status_offset,
        28.5f // temperature_celsius
    );
}

std::vector<uint8_t> BPMFlatBuffers::serializeBPMUpdate(
    flatbuffers::Offset<IcdBpm::BPMUpdate> bpm_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    builder.Finish(bpm_update_offset);

    const uint8_t* buffer = builder.GetBufferPointer();
    size_t size = builder.GetSize();

    return std::vector<uint8_t>(buffer, buffer + size);
}

std::vector<uint8_t> BPMFlatBuffers::serializeStatusUpdate(
    flatbuffers::Offset<IcdBpm::StatusUpdate> status_update_offset,
    flatbuffers::FlatBufferBuilder& builder) {

    builder.Finish(status_update_offset);

    const uint8_t* buffer = builder.GetBufferPointer();
    size_t size = builder.GetSize();

    return std::vector<uint8_t>(buffer, buffer + size);
}

const IcdBpm::BPMUpdate* BPMFlatBuffers::deserializeBPMUpdate(
    const std::vector<uint8_t>& buffer) {

    return IcdBpm::GetBPMUpdate(buffer.data());
}

const IcdBpm::StatusUpdate* BPMFlatBuffers::deserializeStatusUpdate(
    const std::vector<uint8_t>& buffer) {

    return IcdBpm::GetStatusUpdate(buffer.data());
}


const char* BPMFlatBuffers::detectionStatusToString(IcdBpm::DetectionStatus status) {
    switch (status) {
        case IcdBpm::DetectionStatus::INITIALIZING: return "INITIALIZING";
        case IcdBpm::DetectionStatus::DETECTING: return "DETECTING";
        case IcdBpm::DetectionStatus::LOW_SIGNAL: return "LOW_SIGNAL";
        case IcdBpm::DetectionStatus::NO_SIGNAL: return "NO_SIGNAL";
        case IcdBpm::DetectionStatus::ERROR: return "ERROR";
        case IcdBpm::DetectionStatus::CALIBRATING: return "CALIBRATING";
        default: return "UNKNOWN";
    }
}

size_t BPMFlatBuffers::estimateBPMUpdateSize() {
    // BPMUpdate structure size estimate
    return 256; // BPM data + analysis + quality metrics + timestamp
}

size_t BPMFlatBuffers::estimateStatusUpdateSize() {
    // StatusUpdate structure size estimate
    return 128; // Device status + audio status + metadata
}