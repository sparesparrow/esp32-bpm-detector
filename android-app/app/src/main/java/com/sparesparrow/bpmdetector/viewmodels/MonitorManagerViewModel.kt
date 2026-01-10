package com.sparesparrow.bpmdetector.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.sparesparrow.bpmdetector.models.BPMMonitor
import com.sparesparrow.bpmdetector.network.MonitorApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import timber.log.Timber

/**
 * ViewModel for managing multiple BPM monitors
 * Generated from ESP32-BPM Android integration and monitor spawning prompts
 */
class MonitorManagerViewModel(application: Application) : AndroidViewModel(application) {

    // Monitors list
    private val _monitors = MutableStateFlow<List<BPMMonitor>>(emptyList())
    val monitors: StateFlow<List<BPMMonitor>> = _monitors.asStateFlow()

    // Loading state
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Error state
    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    // API client
    private var apiClient: MonitorApiClient? = null
    private var serverIp: String = "192.168.4.1"

    /**
     * Initialize with server IP
     */
    fun initialize(ipAddress: String) {
        serverIp = ipAddress
        apiClient = MonitorApiClient.createWithIp(ipAddress)
        refreshMonitors()
    }

    /**
     * Refresh monitors list from server
     */
    fun refreshMonitors() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null

                val client = apiClient ?: MonitorApiClient.createWithIp(serverIp)
                val result = client.listMonitors()

                result.fold(
                    onSuccess = { monitorList ->
                        _monitors.value = monitorList
                        Timber.d("Refreshed ${monitorList.size} monitors")
                    },
                    onFailure = { error ->
                        Timber.e(error, "Failed to refresh monitors")
                        _error.value = error.message ?: "Failed to refresh monitors"
                    }
                )
            } catch (e: Exception) {
                Timber.e(e, "Error refreshing monitors")
                _error.value = e.message ?: "Unknown error"
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Spawn a new monitor
     */
    fun spawnMonitor(name: String = "", onComplete: (Result<BPMMonitor>) -> Unit = {}) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null

                val client = apiClient ?: MonitorApiClient.createWithIp(serverIp)
                val result = client.spawnMonitor(name)

                result.fold(
                    onSuccess = { monitor ->
                        // Refresh list to get updated data
                        refreshMonitors()
                        onComplete(Result.success(monitor))
                        Timber.d("Spawned monitor ${monitor.id}")
                    },
                    onFailure = { error ->
                        Timber.e(error, "Failed to spawn monitor")
                        _error.value = error.message ?: "Failed to spawn monitor"
                        onComplete(Result.failure(error))
                    }
                )
            } catch (e: Exception) {
                Timber.e(e, "Error spawning monitor")
                _error.value = e.message ?: "Unknown error"
                onComplete(Result.failure(e))
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Remove a monitor
     */
    fun removeMonitor(monitorId: Int, onComplete: (Result<Boolean>) -> Unit = {}) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null

                val client = apiClient ?: MonitorApiClient.createWithIp(serverIp)
                val result = client.removeMonitor(monitorId)

                result.fold(
                    onSuccess = { success ->
                        if (success) {
                            // Remove from local list
                            _monitors.value = _monitors.value.filter { it.id != monitorId }
                        }
                        onComplete(Result.success(success))
                        Timber.d("Removed monitor $monitorId")
                    },
                    onFailure = { error ->
                        Timber.e(error, "Failed to remove monitor")
                        _error.value = error.message ?: "Failed to remove monitor"
                        onComplete(Result.failure(error))
                    }
                )
            } catch (e: Exception) {
                Timber.e(e, "Error removing monitor")
                _error.value = e.message ?: "Unknown error"
                onComplete(Result.failure(e))
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Update monitor (activate/deactivate, rename)
     */
    fun updateMonitor(monitorId: Int, active: Boolean? = null, name: String? = null, onComplete: (Result<BPMMonitor>) -> Unit = {}) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                _error.value = null

                val client = apiClient ?: MonitorApiClient.createWithIp(serverIp)
                val result = client.updateMonitor(monitorId, active, name)

                result.fold(
                    onSuccess = { monitor ->
                        // Update local list
                        _monitors.value = _monitors.value.map { 
                            if (it.id == monitorId) monitor else it 
                        }
                        onComplete(Result.success(monitor))
                        Timber.d("Updated monitor ${monitor.id}")
                    },
                    onFailure = { error ->
                        Timber.e(error, "Failed to update monitor")
                        _error.value = error.message ?: "Failed to update monitor"
                        onComplete(Result.failure(error))
                    }
                )
            } catch (e: Exception) {
                Timber.e(e, "Error updating monitor")
                _error.value = e.message ?: "Unknown error"
                onComplete(Result.failure(e))
            } finally {
                _isLoading.value = false
            }
        }
    }

    /**
     * Get monitor by ID
     */
    fun getMonitor(monitorId: Int): BPMMonitor? {
        return _monitors.value.find { it.id == monitorId }
    }

    /**
     * Get active monitors
     */
    fun getActiveMonitors(): List<BPMMonitor> {
        return _monitors.value.filter { it.isActive }
    }

    /**
     * Clear error
     */
    fun clearError() {
        _error.value = null
    }
}
