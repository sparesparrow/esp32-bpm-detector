package com.sparesparrow.bpmdetector.network

import com.sparesparrow.bpmdetector.models.BPMMonitor
import com.sparesparrow.bpmdetector.models.BPMData
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import timber.log.Timber
import java.io.IOException
import java.util.concurrent.TimeUnit
import org.json.JSONArray
import org.json.JSONObject

/**
 * API client for monitor management
 * Generated from ESP32-BPM Android integration and monitor spawning prompts
 */
class MonitorApiClient(private val baseUrl: String) {

    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(5, TimeUnit.SECONDS)
        .writeTimeout(5, TimeUnit.SECONDS)
        .build()

    /**
     * List all monitors
     */
    suspend fun listMonitors(): Result<List<BPMMonitor>> {
        return try {
            val request = Request.Builder()
                .url("$baseUrl/api/v1/monitors")
                .get()
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val body = response.body?.string() ?: return Result.failure(IOException("Empty response"))
                val monitors = parseMonitorsList(body)
                Result.success(monitors)
            } else {
                Result.failure(IOException("HTTP ${response.code}: ${response.message}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to list monitors")
            Result.failure(e)
        }
    }

    /**
     * Get specific monitor data
     */
    suspend fun getMonitor(monitorId: Int): Result<BPMMonitor> {
        return try {
            val request = Request.Builder()
                .url("$baseUrl/api/v1/monitors/get?id=$monitorId")
                .get()
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val body = response.body?.string() ?: return Result.failure(IOException("Empty response"))
                val monitor = parseMonitor(body)
                if (monitor != null) {
                    Result.success(monitor)
                } else {
                    Result.failure(IOException("Failed to parse monitor data"))
                }
            } else {
                Result.failure(IOException("HTTP ${response.code}: ${response.message}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to get monitor $monitorId")
            Result.failure(e)
        }
    }

    /**
     * Spawn a new monitor
     */
    suspend fun spawnMonitor(name: String = ""): Result<BPMMonitor> {
        return try {
            val json = JSONObject().apply {
                if (name.isNotEmpty()) {
                    put("name", name)
                }
            }
            
            val requestBody = json.toString().toRequestBody("application/json".toMediaType())
            
            val request = Request.Builder()
                .url("$baseUrl/api/v1/monitors/spawn")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                val body = response.body?.string() ?: return Result.failure(IOException("Empty response"))
                val monitor = parseMonitor(body)
                if (monitor != null) {
                    Result.success(monitor)
                } else {
                    Result.failure(IOException("Failed to parse spawned monitor"))
                }
            } else {
                Result.failure(IOException("HTTP ${response.code}: ${response.message}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to spawn monitor")
            Result.failure(e)
        }
    }

    /**
     * Remove a monitor
     */
    suspend fun removeMonitor(monitorId: Int): Result<Boolean> {
        return try {
            val request = Request.Builder()
                .url("$baseUrl/api/v1/monitors/remove?id=$monitorId")
                .delete()
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(IOException("HTTP ${response.code}: ${response.message}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to remove monitor $monitorId")
            Result.failure(e)
        }
    }

    /**
     * Update monitor (activate/deactivate, rename)
     */
    suspend fun updateMonitor(monitorId: Int, active: Boolean? = null, name: String? = null): Result<BPMMonitor> {
        return try {
            val urlBuilder = StringBuilder("$baseUrl/api/v1/monitors/update?id=$monitorId")
            if (active != null) {
                urlBuilder.append("&active=$active")
            }
            if (name != null) {
                urlBuilder.append("&name=$name")
            }
            
            val request = Request.Builder()
                .url(urlBuilder.toString())
                .put("".toRequestBody("application/json".toMediaType()))
                .build()

            val response = client.newCall(request).execute()
            
            if (response.isSuccessful) {
                // Re-fetch monitor to get updated data
                getMonitor(monitorId)
            } else {
                Result.failure(IOException("HTTP ${response.code}: ${response.message}"))
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to update monitor $monitorId")
            Result.failure(e)
        }
    }

    /**
     * Parse monitors list from JSON
     */
    private fun parseMonitorsList(json: String): List<BPMMonitor> {
        val monitors = mutableListOf<BPMMonitor>()
        try {
            val array = JSONArray(json)
            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                val monitor = BPMMonitor.fromJson(obj.toMap())
                if (monitor != null) {
                    monitors.add(monitor)
                }
            }
        } catch (e: Exception) {
            Timber.e(e, "Failed to parse monitors list")
        }
        return monitors
    }

    /**
     * Parse single monitor from JSON
     */
    private fun parseMonitor(json: String): BPMMonitor? {
        return try {
            val obj = JSONObject(json)
            BPMMonitor.fromJson(obj.toMap())
        } catch (e: Exception) {
            Timber.e(e, "Failed to parse monitor")
            null
        }
    }

    companion object {
        /**
         * Create monitor API client with default base URL
         */
        fun createDefault(): MonitorApiClient {
            return MonitorApiClient("http://192.168.4.1")
        }

        /**
         * Create monitor API client with custom IP
         */
        fun createWithIp(ipAddress: String): MonitorApiClient {
            val baseUrl = "http://$ipAddress"
            return MonitorApiClient(baseUrl)
        }
    }
}

/**
 * Extension to convert JSONObject to Map
 */
private fun JSONObject.toMap(): Map<String, Any?> {
    val map = mutableMapOf<String, Any?>()
    val keys = this.keys()
    while (keys.hasNext()) {
        val key = keys.next()
        val value = this.get(key)
        map[key] = when (value) {
            is JSONObject -> value.toMap()
            is JSONArray -> value.toList()
            JSONObject.NULL -> null
            else -> value
        }
    }
    return map
}

/**
 * Extension to convert JSONArray to List
 */
private fun JSONArray.toList(): List<Any?> {
    val list = mutableListOf<Any?>()
    for (i in 0 until this.length()) {
        val value = this.get(i)
        list.add(when (value) {
            is JSONObject -> value.toMap()
            is JSONArray -> value.toList()
            JSONObject.NULL -> null
            else -> value
        })
    }
    return list
}
