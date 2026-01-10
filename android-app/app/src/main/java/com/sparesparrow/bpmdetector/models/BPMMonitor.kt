package com.sparesparrow.bpmdetector.models

/**
 * BPM Monitor model representing a single monitor instance
 * Generated from ESP32-BPM Android integration and monitor spawning prompts
 */
data class BPMMonitor(
    val id: Int,
    val name: String,
    val isActive: Boolean,
    val bpmData: BPMData? = null,
    val serverIp: String? = null
) {
    /**
     * Get formatted display name
     */
    fun getDisplayName(): String {
        return if (name.isNotEmpty()) name else "Monitor $id"
    }

    /**
     * Check if monitor is connected and receiving data
     */
    fun isConnected(): Boolean {
        return isActive && bpmData != null && !bpmData.hasError()
    }

    /**
     * Get current BPM value as string
     */
    fun getBpmString(): String {
        return bpmData?.getFormattedBpm() ?: "--"
    }

    /**
     * Get connection status description
     */
    fun getStatusDescription(): String {
        return when {
            !isActive -> "Inactive"
            bpmData == null -> "No data"
            bpmData.hasError() -> "Error"
            bpmData.isDetecting() -> "Detecting"
            else -> "Connected"
        }
    }

    companion object {
        /**
         * Create a monitor from JSON response
         */
        fun fromJson(json: Map<String, Any?>): BPMMonitor? {
            return try {
                val id = (json["id"] as? Number)?.toInt() ?: return null
                val name = (json["name"] as? String) ?: ""
                val active = (json["active"] as? Boolean) ?: false
                
                val bpmData = if (json.containsKey("bpm")) {
                    BPMData(
                        bpm = (json["bpm"] as? Number)?.toFloat() ?: 0f,
                        confidence = (json["confidence"] as? Number)?.toFloat() ?: 0f,
                        signalLevel = (json["signal_level"] as? Number)?.toFloat() ?: 0f,
                        status = (json["status"] as? String) ?: "unknown",
                        timestamp = (json["timestamp"] as? Number)?.toLong() ?: 0L
                    )
                } else null
                
                BPMMonitor(
                    id = id,
                    name = name,
                    isActive = active,
                    bpmData = bpmData
                )
            } catch (e: Exception) {
                null
            }
        }
    }
}
