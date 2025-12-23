package com.sparesparrow.bpmdetector.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.services.ConnectionStatus
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber

/**
 * ViewModel for BPM detection functionality
 */
class BPMViewModel(application: Application) : AndroidViewModel(application) {

    // BPM Data
    private val _bpmData = MutableLiveData<BPMData>()
    val bpmData: LiveData<BPMData> = _bpmData

    // Connection Status
    private val _connectionStatus = MutableStateFlow<ConnectionStatus>(ConnectionStatus(ConnectionStatus.DISCONNECTED))
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatus.asStateFlow()

    // Service state
    private val _isServiceRunning = MutableStateFlow(false)
    val isServiceRunning: StateFlow<Boolean> = _isServiceRunning.asStateFlow()

    // Settings
    private val _serverIp = MutableStateFlow("192.168.1.100")
    val serverIp: StateFlow<String> = _serverIp.asStateFlow()

    private val _pollingInterval = MutableStateFlow(500L)
    val pollingInterval: StateFlow<Long> = _pollingInterval.asStateFlow()

    // Service reference (set when service is bound)
    private var bpmService: BPMService? = null

    init {
        // Initialize with loading state
        _bpmData.value = BPMData.createLoading()
    }

    /**
     * Set BPM service reference (called when service is bound)
     */
    fun setBPMService(service: BPMService) {
        Timber.d("BPM service bound to ViewModel")

        // Unbind previous service
        bpmService?.let {
            it.bpmData.removeObserver(bpmDataObserver)
            it.connectionStatus.removeObserver(connectionStatusObserver)
        }

        bpmService = service

        // Observe service LiveData
        service.bpmData.observeForever(bpmDataObserver)
        service.connectionStatus.observeForever(connectionStatusObserver)

        // Update service state
        _isServiceRunning.value = service.isPolling()

        // Sync settings with service
        _serverIp.value = service.getServerIp()
    }

    /**
     * Clear BPM service reference (called when service is unbound)
     */
    fun clearBPMService() {
        Timber.d("BPM service unbound from ViewModel")

        bpmService?.let {
            it.bpmData.removeObserver(bpmDataObserver)
            it.connectionStatus.removeObserver(connectionStatusObserver)
        }

        bpmService = null
        _isServiceRunning.value = false
    }

    /**
     * Start BPM monitoring
     */
    fun startMonitoring() {
        viewModelScope.launch {
            try {
                bpmService?.startPolling()
                _isServiceRunning.value = true
                Timber.d("BPM monitoring started")
            } catch (e: Exception) {
                Timber.e(e, "Failed to start BPM monitoring")
            }
        }
    }

    /**
     * Stop BPM monitoring
     */
    fun stopMonitoring() {
        viewModelScope.launch {
            try {
                bpmService?.stopPolling()
                _isServiceRunning.value = false
                Timber.d("BPM monitoring stopped")
            } catch (e: Exception) {
                Timber.e(e, "Failed to stop BPM monitoring")
            }
        }
    }

    /**
     * Update server IP address
     */
    fun updateServerIp(newIp: String) {
        if (_serverIp.value != newIp) {
            _serverIp.value = newIp
            bpmService?.setServerIp(newIp)
            Timber.d("Server IP updated to: $newIp")
        }
    }

    /**
     * Update polling interval
     */
    fun updatePollingInterval(intervalMs: Long) {
        val clampedInterval = intervalMs.coerceIn(100L, 2000L)
        if (_pollingInterval.value != clampedInterval) {
            _pollingInterval.value = clampedInterval
            bpmService?.setPollingInterval(clampedInterval)
            Timber.d("Polling interval updated to: ${clampedInterval}ms")
        }
    }

    /**
     * Get current BPM value as formatted string
     */
    fun getFormattedBpm(): String {
        return bpmData.value?.getFormattedBpm() ?: "--"
    }

    /**
     * Get current confidence as percentage
     */
    fun getConfidencePercentage(): Int {
        return bpmData.value?.getConfidencePercentage() ?: 0
    }

    /**
     * Get current signal level as percentage
     */
    fun getSignalLevelPercentage(): Int {
        return bpmData.value?.getSignalLevelPercentage() ?: 0
    }

    /**
     * Get status description
     */
    fun getStatusDescription(): String {
        return bpmData.value?.getStatusDescription() ?: "Disconnected"
    }

    /**
     * Check if currently detecting BPM
     */
    fun isDetecting(): Boolean {
        return bpmData.value?.isDetecting() ?: false
    }

    /**
     * Check if there's low signal
     */
    fun hasLowSignal(): Boolean {
        return bpmData.value?.hasLowSignal() ?: false
    }

    /**
     * Check if there's an error
     */
    fun hasError(): Boolean {
        return bpmData.value?.hasError() ?: false
    }

    /**
     * Get connection status description
     */
    fun getConnectionStatusDescription(): String {
        return when (connectionStatus.value.status) {
            ConnectionStatus.CONNECTED -> "Connected"
            ConnectionStatus.CONNECTING -> "Connecting..."
            ConnectionStatus.DISCONNECTED -> "Disconnected"
            ConnectionStatus.ERROR -> "Connection Error: ${connectionStatus.value.errorMessage ?: "Unknown error"}"
        }
    }

    // Observers for service LiveData
    private val bpmDataObserver = androidx.lifecycle.Observer<BPMData> { data ->
        _bpmData.postValue(data)
    }

    private val connectionStatusObserver = androidx.lifecycle.Observer<ConnectionStatus> { status ->
        _connectionStatus.value = status
    }

    override fun onCleared() {
        super.onCleared()
        clearBPMService()
    }
}

