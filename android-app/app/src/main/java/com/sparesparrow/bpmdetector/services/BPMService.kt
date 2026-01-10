package com.sparesparrow.bpmdetector.services

import android.app.Service
import android.content.Intent
import android.os.Binder
import android.os.IBinder
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.network.BPMApiClient
import kotlinx.coroutines.*
import timber.log.Timber
import java.util.concurrent.atomic.AtomicBoolean

/**
 * Background service for polling BPM data from ESP32
 */
class BPMService : Service() {

    private val binder = LocalBinder()
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    // LiveData for BPM data
    private val _bpmData = MutableLiveData<BPMData>()
    val bpmData: LiveData<BPMData> = _bpmData

    // Connection status
    private val _connectionStatus = MutableLiveData<ConnectionStatus>()
    val connectionStatus: LiveData<ConnectionStatus> = _connectionStatus

    // Service state
    private val isRunning = AtomicBoolean(false)
    private var pollingJob: Job? = null
    private var apiClient: BPMApiClient? = null

    // Configuration
    private var pollingIntervalMs: Long = 500L // Default 500ms
    private var serverIp: String = "192.168.4.1" // Default IP - matches ESP32 AP mode gateway IP

    override fun onCreate() {
        super.onCreate()
        Timber.d("BPMService created")
        updateConnectionStatus(ConnectionStatus.DISCONNECTED)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Timber.d("BPMService started")

        // Get server IP from intent if provided
        intent?.getStringExtra(EXTRA_SERVER_IP)?.let { ip ->
            setServerIp(ip)
        }

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }

    override fun onDestroy() {
        super.onDestroy()
        Timber.d("BPMService destroyed")
        stopPolling()
        serviceScope.cancel()
    }

    /**
     * Start polling BPM data
     */
    fun startPolling() {
        if (isRunning.get()) {
            Timber.w("BPM service already running")
            return
        }

        Timber.d("Starting BPM polling service")
        isRunning.set(true)

        // Create API client
        apiClient = BPMApiClient.createWithIp(serverIp)

        // Start polling job
        pollingJob = serviceScope.launch {
            while (isRunning.get() && isActive) {
                try {
                    pollBPMData()
                } catch (e: Exception) {
                    Timber.e(e, "Error in polling loop")
                    updateConnectionStatus(ConnectionStatus.ERROR, e.message ?: "Unknown error")
                }

                delay(pollingIntervalMs)
            }
        }

        updateConnectionStatus(ConnectionStatus.CONNECTING)
    }

    /**
     * Stop polling BPM data
     */
    fun stopPolling() {
        Timber.d("Stopping BPM polling service")
        isRunning.set(false)
        pollingJob?.cancel()
        pollingJob = null
        updateConnectionStatus(ConnectionStatus.DISCONNECTED)
    }

    /**
     * Set server IP address
     */
    fun setServerIp(ipAddress: String) {
        if (serverIp != ipAddress) {
            Timber.d("Changing server IP from $serverIp to $ipAddress")
            serverIp = ipAddress

            // Restart service if running
            if (isRunning.get()) {
                stopPolling()
                apiClient = BPMApiClient.createWithIp(serverIp)
                startPolling()
            } else {
                apiClient = BPMApiClient.createWithIp(serverIp)
            }
        }
    }

    /**
     * Set polling interval
     */
    fun setPollingInterval(intervalMs: Long) {
        pollingIntervalMs = intervalMs.coerceIn(100L, 2000L) // Clamp to reasonable range
        Timber.d("Polling interval set to ${pollingIntervalMs}ms")
    }

    /**
     * Check if service is currently polling
     */
    fun isPolling(): Boolean = isRunning.get()

    /**
     * Get current server IP
     */
    fun getServerIp(): String = serverIp

    /**
     * Poll BPM data from ESP32
     */
    private suspend fun pollBPMData() {
        val client = apiClient ?: run {
            updateConnectionStatus(ConnectionStatus.ERROR, "API client not initialized")
            return
        }

        val result = client.getBPMDataWithRetry()

        result.fold(
            onSuccess = { bpmData: com.sparesparrow.bpmdetector.models.BPMData ->
                _bpmData.postValue(bpmData)
                updateConnectionStatus(ConnectionStatus.CONNECTED)
                Timber.d("BPM data received: ${bpmData.bpm} BPM, confidence: ${bpmData.confidence}")
            },
            onFailure = { error ->
                Timber.e(error, "Failed to get BPM data")
                val errorMessage = when (error) {
                    is java.net.UnknownHostException -> "Cannot reach ESP32 server"
                    is java.net.SocketTimeoutException -> "Connection timeout"
                    else -> error.message ?: "Unknown network error"
                }
                updateConnectionStatus(ConnectionStatus.ERROR, errorMessage)

                // Post error state to LiveData
                _bpmData.postValue(BPMData.createError())
            }
        )
    }

    /**
     * Update connection status
     */
    private fun updateConnectionStatus(status: ConnectionStatus, errorMessage: String? = null) {
        _connectionStatus.postValue(status)
        Timber.d("Connection status: ${status.name}${errorMessage?.let { " ($it)" } ?: ""}")
    }

    /**
     * Local binder for service binding
     */
    inner class LocalBinder : Binder() {
        fun getService(): BPMService = this@BPMService
    }

    companion object {
        const val EXTRA_SERVER_IP = "extra_server_ip"

        /**
         * Create intent for starting the service
         */
        fun createIntent(context: android.content.Context, serverIp: String? = null): Intent {
            return Intent(context, BPMService::class.java).apply {
                serverIp?.let { putExtra(EXTRA_SERVER_IP, it) }
            }
        }
    }
}

/**
 * Connection status enum
 */
enum class ConnectionStatus {
    DISCONNECTED,
    SEARCHING,
    CONNECTING,
    CONNECTED,
    ERROR;

    fun isConnected(): Boolean = this == CONNECTED
    fun hasError(): Boolean = this == ERROR
    fun isConnecting(): Boolean = this == CONNECTING
    fun isSearching(): Boolean = this == SEARCHING
}


