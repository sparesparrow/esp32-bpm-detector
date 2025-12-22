package com.sparesparrow.bpmdetector.models

import com.google.gson.annotations.SerializedName

/**
 * BPM data model representing the response from ESP32 API
 */
data class BPMData(
    @SerializedName("bpm")
    val bpm: Float = 0.0f,

    @SerializedName("confidence")
    val confidence: Float = 0.0f,

    @SerializedName("signal_level")
    val signalLevel: Float = 0.0f,

    @SerializedName("status")
    val status: String = "unknown",

    @SerializedName("timestamp")
    val timestamp: Long = 0L
) {
    /**
     * Check if BPM detection is active
     */
    fun isDetecting(): Boolean = status == "detecting"

    /**
     * Check if there's low signal
     */
    fun hasLowSignal(): Boolean = status == "low_signal"

    /**
     * Check if there's an error
     */
    fun hasError(): Boolean = status == "error"

    /**
     * Get confidence as percentage (0-100)
     */
    fun getConfidencePercentage(): Int = (confidence * 100).toInt()

    /**
     * Get signal level as percentage (0-100)
     */
    fun getSignalLevelPercentage(): Int = (signalLevel * 100).toInt()

    /**
     * Get formatted BPM string
     */
    fun getFormattedBpm(): String = if (bpm > 0) "%.1f".format(bpm) else "--"

    /**
     * Get status description for UI
     */
    fun getStatusDescription(): String = when (status) {
        "detecting" -> "Detecting BPM"
        "low_signal" -> "Low Audio Signal"
        "low_confidence" -> "Analyzing..."
        "error" -> "Connection Error"
        "initializing" -> "Initializing..."
        "buffering" -> "Buffering..."
        else -> "Unknown Status"
    }

    companion object {
        /**
         * Create error state BPM data
         */
        fun createError(): BPMData = BPMData(
            bpm = 0.0f,
            confidence = 0.0f,
            signalLevel = 0.0f,
            status = "error",
            timestamp = System.currentTimeMillis()
        )

        /**
         * Create loading state BPM data
         */
        fun createLoading(): BPMData = BPMData(
            bpm = 0.0f,
            confidence = 0.0f,
            signalLevel = 0.0f,
            status = "connecting",
            timestamp = System.currentTimeMillis()
        )
    }
}

/**
 * Settings/configuration data
 */
data class BPMSettings(
    @SerializedName("min_bpm")
    val minBpm: Int = 60,

    @SerializedName("max_bpm")
    val maxBpm: Int = 200,

    @SerializedName("sample_rate")
    val sampleRate: Int = 25000,

    @SerializedName("fft_size")
    val fftSize: Int = 1024,

    @SerializedName("version")
    val version: String = "1.0.0"
)

/**
 * Health check data
 */
data class BPMHealth(
    @SerializedName("status")
    val status: String = "unknown",

    @SerializedName("uptime")
    val uptime: Long = 0L,

    @SerializedName("heap_free")
    val heapFree: Long = 0L
) {
    /**
     * Check if ESP32 is healthy
     */
    fun isHealthy(): Boolean = status == "ok"

    /**
     * Get formatted uptime string
     */
    fun getFormattedUptime(): String {
        val seconds = uptime / 1000
        val minutes = seconds / 60
        val hours = minutes / 60

        return when {
            hours > 0 -> "${hours}h ${minutes % 60}m"
            minutes > 0 -> "${minutes}m ${seconds % 60}s"
            else -> "${seconds}s"
        }
    }

    /**
     * Get formatted heap free string
     */
    fun getFormattedHeap(): String {
        return when {
            heapFree > 1024 * 1024 -> "%.1f MB".format(heapFree / (1024.0 * 1024.0))
            heapFree > 1024 -> "%.1f KB".format(heapFree / 1024.0)
            else -> "$heapFree B"
        }
    }
}
