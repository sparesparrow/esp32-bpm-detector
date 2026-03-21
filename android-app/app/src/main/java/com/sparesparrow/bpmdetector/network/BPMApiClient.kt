package com.sparesparrow.bpmdetector.network

import android.util.Log
import com.google.gson.GsonBuilder
import com.sparesparrow.bpmdetector.BuildConfig
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.models.BPMSettings
import com.sparesparrow.bpmdetector.models.BPMHealth
import kotlinx.coroutines.delay
import okhttp3.OkHttpClient
import okhttp3.ResponseBody
import okhttp3.logging.HttpLoggingInterceptor
import org.json.JSONObject
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import timber.log.Timber
import java.io.IOException
import java.net.SocketTimeoutException
import java.net.UnknownHostException
import java.util.concurrent.TimeUnit

/**
 * API client for communicating with ESP32 BPM detector
 */
class BPMApiClient(private val baseUrl: String) {

    private val apiService: BPMApiService by lazy { createApiService() }

    private fun createApiService(): BPMApiService {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(BPMApiService.DEFAULT_TIMEOUT_MS, TimeUnit.MILLISECONDS)
            .readTimeout(BPMApiService.DEFAULT_TIMEOUT_MS, TimeUnit.MILLISECONDS)
            .writeTimeout(BPMApiService.DEFAULT_TIMEOUT_MS, TimeUnit.MILLISECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .build()

        return retrofit.create(BPMApiService::class.java)
    }

    /**
     * Get BPM data with retry logic
     */
    suspend fun getBPMDataWithRetry(retryAttempts: Int = BPMApiService.DEFAULT_RETRY_ATTEMPTS): Result<BPMData> {
        return executeWithRetry(retryAttempts) {
            apiService.getBPMData()
        }.fold(
            onSuccess = { response ->
                if (response.isSuccessful) {
                    response.body()?.let { body ->
                        try {
                            val bpmData = deserializeBPMData(body)
                            Result.success(bpmData)
                        } catch (e: Exception) {
                            Timber.e(e, "Failed to deserialize BPM data")
                            Result.failure(IOException("Failed to deserialize response: ${e.message}"))
                        }
                    } ?: Result.failure(IOException("Empty response body"))
                } else {
                    Result.failure(HttpException("HTTP ${response.code()}: ${response.message()}"))
                }
            },
            onFailure = { Result.failure(it) }
        )
    }

    /**
     * Get settings data
     */
    suspend fun getSettings(): Result<BPMSettings> {
        return try {
            val response = apiService.getSettings()
            if (response.isSuccessful) {
                response.body()?.let { body ->
                    try {
                        val settings = deserializeBPMSettings(body)
                        Result.success(settings)
                    } catch (e: Exception) {
                        Timber.e(e, "Failed to deserialize settings")
                        Result.failure(IOException("Failed to deserialize response: ${e.message}"))
                    }
                } ?: Result.failure(IOException("Empty response body"))
            } else {
                Result.failure(HttpException("HTTP ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Error getting settings")
            Result.failure(e)
        }
    }

    /**
     * Get health data
     */
    suspend fun getHealth(): Result<BPMHealth> {
        return try {
            val response = apiService.getHealth()
            if (response.isSuccessful) {
                response.body()?.let { body ->
                    try {
                        val health = deserializeBPMHealth(body)
                        Result.success(health)
                    } catch (e: Exception) {
                        Timber.e(e, "Failed to deserialize health data")
                        Result.failure(IOException("Failed to deserialize response: ${e.message}"))
                    }
                } ?: Result.failure(IOException("Empty response body"))
            } else {
                Result.failure(HttpException("HTTP ${response.code()}: ${response.message()}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Error getting health data")
            Result.failure(e)
        }
    }

    /**
     * Execute network call with retry logic
     */
    private suspend fun <T> executeWithRetry(
        maxAttempts: Int,
        block: suspend () -> retrofit2.Response<T>
    ): Result<retrofit2.Response<T>> {
        var lastException: Exception? = null

        for (attempt in 1..maxAttempts) {
            try {
                val response = block()
                return Result.success(response)
            } catch (e: Exception) {
                lastException = e
                Timber.w(e, "Network attempt $attempt/$maxAttempts failed")

                // Don't retry on certain errors
                when (e) {
                    is UnknownHostException -> break
                    is SecurityException -> break
                    is IllegalArgumentException -> break
                }

                // Wait before retry (exponential backoff)
                if (attempt < maxAttempts) {
                    delay(attempt * 1000L)
                }
            }
        }

        return Result.failure(lastException ?: IOException("Unknown error"))
    }

    /**
     * Check if server is reachable
     */
    suspend fun isServerReachable(): Boolean {
        return try {
            val result = getHealth()
            result.isSuccess && result.getOrNull()?.isHealthy() == true
        } catch (e: Exception) {
            Timber.d(e, "Server reachability check failed")
            false
        }
    }

    /**
     * Get connection info for debugging
     */
    fun getConnectionInfo(): String {
        return "Connected to: $baseUrl"
    }

    /**
     * Deserialize BPM data from JSON response
     * ESP32 /api/v1/bpm/current returns:
     *   {"bpm":120.0,"confidence":0.85,"signal_level":0.72,"status":"detecting","timestamp":12345}
     */
    private fun deserializeBPMData(responseBody: ResponseBody): BPMData {
        val json = JSONObject(responseBody.string())
        return BPMData(
            bpm = json.optDouble("bpm", 0.0).toFloat(),
            confidence = json.optDouble("confidence", 0.0).toFloat(),
            signalLevel = json.optDouble("signal_level", 0.0).toFloat(),
            status = json.optString("status", "unknown"),
            timestamp = json.optLong("timestamp", 0L)
        )
    }

    /**
     * Deserialize BPM settings from JSON response
     * ESP32 /api/v1/system/config returns:
     *   {"sample_rate":25000,"fft_size":1024,"min_bpm":60,"max_bpm":200,...}
     */
    private fun deserializeBPMSettings(responseBody: ResponseBody): BPMSettings {
        val json = JSONObject(responseBody.string())
        return BPMSettings(
            minBpm = json.optInt("min_bpm", 60),
            maxBpm = json.optInt("max_bpm", 200),
            sampleRate = json.optInt("sample_rate", 25000),
            fftSize = json.optInt("fft_size", 1024),
            version = json.optString("version", "1.0.0")
        )
    }

    /**
     * Deserialize BPM health from JSON response
     * ESP32 /api/v1/system/health returns:
     *   {"status":"ok","uptime":12345,"heap":200000,"wifi_connected":true}
     */
    private fun deserializeBPMHealth(responseBody: ResponseBody): BPMHealth {
        val json = JSONObject(responseBody.string())
        return BPMHealth(
            status = json.optString("status", "unknown"),
            uptime = json.optLong("uptime", 0L),
            heapFree = json.optLong("heap", 0L)
        )
    }

    companion object {
        /**
         * Create API client with default base URL
         */
        fun createDefault(): BPMApiClient {
            return BPMApiClient("http://192.168.4.1") // Default ESP32 IP
        }

        /**
         * Create API client with custom IP
         */
        fun createWithIp(ipAddress: String): BPMApiClient {
            val baseUrl = "http://$ipAddress"
            return BPMApiClient(baseUrl)
        }

        /**
         * Validate IP address format
         */
        fun isValidIpAddress(ip: String): Boolean {
            val ipRegex = Regex("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
            return ipRegex.matches(ip)
        }
    }
}

/**
 * Custom HTTP exception
 */
class HttpException(message: String) : IOException(message)

