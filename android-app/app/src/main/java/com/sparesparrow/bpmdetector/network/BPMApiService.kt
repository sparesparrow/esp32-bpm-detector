package com.sparesparrow.bpmdetector.network

import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.models.BPMHealth
import com.sparesparrow.bpmdetector.models.BPMSettings
import retrofit2.Response
import retrofit2.http.GET

/**
 * Retrofit API service interface for ESP32 BPM detector
 */
interface BPMApiService {

    /**
     * Get current BPM data
     */
    @GET("/api/bpm")
    suspend fun getBPMData(): Response<BPMData>

    /**
     * Get firmware settings
     */
    @GET("/api/settings")
    suspend fun getSettings(): Response<BPMSettings>

    /**
     * Health check
     */
    @GET("/api/health")
    suspend fun getHealth(): Response<BPMHealth>

    companion object {
        const val DEFAULT_TIMEOUT_MS = 5000L
        const val DEFAULT_RETRY_ATTEMPTS = 3
    }
}

