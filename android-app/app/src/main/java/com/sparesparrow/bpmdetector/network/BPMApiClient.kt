package com.sparesparrow.bpmdetector.network

import com.google.gson.GsonBuilder
import com.sparesparrow.bpmdetector.models.*
import kotlinx.coroutines.delay
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
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
        val gson = GsonBuilder()
            .setLenient()
            .create()

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
            .addConverterFactory(GsonConverterFactory.create(gson))
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
                    response.body()?.let { Result.success(it) }
                        ?: Result.failure(IOException("Empty response body"))
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
                response.body()?.let { Result.success(it) }
                    ?: Result.failure(IOException("Empty response body"))
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
                response.body()?.let { Result.success(it) }
                    ?: Result.failure(IOException("Empty response body"))
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

    companion object {
        /**
         * Create API client with default base URL
         */
        fun createDefault(): BPMApiClient {
            return BPMApiClient("http://192.168.1.100") // Default ESP32 IP
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

