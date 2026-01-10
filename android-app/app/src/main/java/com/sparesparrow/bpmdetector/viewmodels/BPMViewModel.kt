package com.sparesparrow.bpmdetector.viewmodels

import android.app.Application
import android.content.Context
import android.content.SharedPreferences
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.sparesparrow.bpmdetector.audio.LocalBPMDetector
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.services.ConnectionStatus
import com.sparesparrow.bpmdetector.network.WiFiManager
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch
import timber.log.Timber

/**
 * Detection mode enum
 */
enum class DetectionMode {
    ESP32,  // Use ESP32 device via network
    LOCAL   // Use phone's microphone
}

/**
 * ViewModel for BPM detection functionality
 */
class BPMViewModel(application: Application) : AndroidViewModel(application) {

    // BPM Data as StateFlow for Compose
    private val _bpmDataFlow = MutableStateFlow<BPMData?>(null)
    val bpmDataFlow: StateFlow<BPMData?> = _bpmDataFlow.asStateFlow()

    // Connection Status
    private val _connectionStatus = MutableStateFlow<ConnectionStatus>(ConnectionStatus.DISCONNECTED)
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatus.asStateFlow()

    // Service state
    private val _isServiceRunning = MutableStateFlow(false)
    val isServiceRunning: StateFlow<Boolean> = _isServiceRunning.asStateFlow()

    // Settings
    private val _serverIp = MutableStateFlow("192.168.4.1:80")
    val serverIp: StateFlow<String> = _serverIp.asStateFlow()

    private val _pollingInterval = MutableStateFlow(500L)
    val pollingInterval: StateFlow<Long> = _pollingInterval.asStateFlow()

    // Service reference (set when service is bound)
    private var bpmService: BPMService? = null

    // Local BPM detector (for phone microphone)
    private var localBPMDetector: LocalBPMDetector? = null
    private var localDetectionJob: kotlinx.coroutines.Job? = null

    // Detection mode
    private val _detectionMode = MutableStateFlow<DetectionMode>(DetectionMode.ESP32)
    val detectionMode: StateFlow<DetectionMode> = _detectionMode.asStateFlow()

    // SharedPreferences for persistence
    private val prefs: SharedPreferences = getApplication<Application>().getSharedPreferences("bpm_detector_prefs", Context.MODE_PRIVATE)

    // WiFi Manager
    private val wifiManager = WiFiManager(getApplication())

    // Network monitoring
    private val connectivityManager = getApplication<Application>().getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    private lateinit var networkCallback: ConnectivityManager.NetworkCallback

    // Local detector settings (default values)
    private val _localSampleRate = MutableStateFlow(16000)
    val localSampleRate: StateFlow<Int> = _localSampleRate.asStateFlow()
    
    private val _localFftSize = MutableStateFlow(1024)
    val localFftSize: StateFlow<Int> = _localFftSize.asStateFlow()
    
    private val _localMinBpm = MutableStateFlow(60)
    val localMinBpm: StateFlow<Int> = _localMinBpm.asStateFlow()
    
    private val _localMaxBpm = MutableStateFlow(200)
    val localMaxBpm: StateFlow<Int> = _localMaxBpm.asStateFlow()

    // Frequency spectrum for visualization
    private val _frequencySpectrum = MutableStateFlow<FloatArray?>(null)
    val frequencySpectrum: StateFlow<FloatArray?> = _frequencySpectrum.asStateFlow()

    // Recording state
    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()

    // WiFi state
    private val _isScanningWifi = MutableStateFlow(false)
    val isScanningWifi: StateFlow<Boolean> = _isScanningWifi.asStateFlow()

    private val _wifiScanResults = MutableStateFlow<List<android.net.wifi.ScanResult>>(emptyList())
    val wifiScanResults: StateFlow<List<android.net.wifi.ScanResult>> = _wifiScanResults.asStateFlow()

    private val _isConnectingToWifi = MutableStateFlow(false)
    val isConnectingToWifi: StateFlow<Boolean> = _isConnectingToWifi.asStateFlow()

    private val _esp32NetworkFound = MutableStateFlow(false)
    val esp32NetworkFound: StateFlow<Boolean> = _esp32NetworkFound.asStateFlow()

    init {
        // Load saved settings
        loadSavedSettings()

        // Initialize with loading state
        val loadingData = BPMData.createLoading()
        _bpmDataFlow.value = loadingData

        // Initialize network monitoring
        setupNetworkMonitoring()

        // Start auto-discovery when ViewModel is created (only if permissions are granted)
        // Delay slightly to ensure permissions are checked first
        viewModelScope.launch {
            kotlinx.coroutines.delay(500) // Small delay for initialization
            if (wifiManager.hasLocationPermissions() && wifiManager.isWifiEnabled()) {
                autoDiscoverDevice()
            } else {
                Timber.d("Auto-discovery skipped - missing permissions or WiFi disabled")
            }
        }
    }

    /**
     * Setup network connectivity monitoring
     */
    private fun setupNetworkMonitoring() {
        networkCallback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                super.onAvailable(network)
                Timber.d("Network available")
                // Check if WiFi is restored and we were previously connected
                if (_connectionStatus.value == ConnectionStatus.DISCONNECTED ||
                    _connectionStatus.value == ConnectionStatus.ERROR) {
                    viewModelScope.launch {
                        kotlinx.coroutines.delay(1000) // Brief delay to let network stabilize
                        if (wifiManager.isConnectedToEsp32()) {
                            Timber.d("WiFi connection restored, testing connectivity...")
                            testHttpConnectivityWithRetry()
                        } else if (_detectionMode.value == DetectionMode.ESP32) {
                            Timber.d("Network restored, attempting auto-discovery...")
                            autoDiscoverDevice()
                        }
                    }
                }
            }

            override fun onLost(network: Network) {
                super.onLost(network)
                Timber.d("Network lost")
                // Only update status if we were previously connected
                if (_connectionStatus.value == ConnectionStatus.CONNECTED) {
                    _connectionStatus.value = ConnectionStatus.DISCONNECTED
                    Timber.w("ESP32 connection lost due to network change")
                }
            }

            override fun onCapabilitiesChanged(network: Network, networkCapabilities: NetworkCapabilities) {
                super.onCapabilitiesChanged(network, networkCapabilities)
                val hasInternet = networkCapabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                val hasWifi = networkCapabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)

                Timber.d("Network capabilities changed - Internet: $hasInternet, WiFi: $hasWifi")

                // If we lose WiFi connectivity while connected to ESP32, update status
                if (!hasWifi && _connectionStatus.value == ConnectionStatus.CONNECTED) {
                    _connectionStatus.value = ConnectionStatus.DISCONNECTED
                    Timber.w("WiFi connectivity lost while connected to ESP32")
                }
            }
        }

        // Register network callback
        val networkRequest = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
            .build()

        connectivityManager.registerNetworkCallback(networkRequest, networkCallback)
    }

    /**
     * Set BPM service reference (called when service is bound)
     */
    fun setBPMService(service: BPMService) {
        Timber.d("BPM service bound to ViewModel")

        // Safely unbind previous service with proper error handling
        clearServiceObservers()

        bpmService = service

        try {
            // Observe service LiveData with proper lifecycle management
            service.bpmData.observeForever(bpmDataObserver)
            service.connectionStatus.observeForever(connectionStatusObserver)

            // Update service state
            _isServiceRunning.value = service.isPolling()

            // Sync settings with service
            _serverIp.value = service.getServerIp()
        } catch (e: Exception) {
            Timber.e(e, "Error setting up service observers")
            // Clean up on error
            clearServiceObservers()
            throw e
        }
    }

    /**
     * Clear BPM service reference (called when service is unbound)
     */
    fun clearBPMService() {
        Timber.d("BPM service unbound from ViewModel")
        clearServiceObservers()
        bpmService = null
        _isServiceRunning.value = false
    }

    /**
     * Safely clear service observers with error handling
     */
    private fun clearServiceObservers() {
        bpmService?.let { service ->
            try {
                service.bpmData.removeObserver(bpmDataObserver)
                service.connectionStatus.removeObserver(connectionStatusObserver)
                Timber.d("Service observers removed successfully")
            } catch (e: Exception) {
                Timber.w(e, "Error removing service observers (may have been already removed)")
            }
        }
    }

    /**
     * Start BPM monitoring (ESP32 or local based on current mode)
     */
    fun startMonitoring() {
        when (_detectionMode.value) {
            DetectionMode.ESP32 -> startESP32Monitoring()
            DetectionMode.LOCAL -> startLocalMonitoring()
        }
    }

    /**
     * Stop BPM monitoring
     */
    fun stopMonitoring() {
        when (_detectionMode.value) {
            DetectionMode.ESP32 -> stopESP32Monitoring()
            DetectionMode.LOCAL -> stopLocalMonitoring()
        }
    }

    /**
     * Switch detection mode
     */
    fun setDetectionMode(mode: DetectionMode) {
        if (_detectionMode.value == mode) {
            return
        }

        // Stop current mode
        when (_detectionMode.value) {
            DetectionMode.ESP32 -> stopESP32Monitoring()
            DetectionMode.LOCAL -> stopLocalMonitoring()
        }

        _detectionMode.value = mode
        saveSettings()

        // Start new mode if service was running
        if (_isServiceRunning.value) {
            startMonitoring()
        }
    }

    /**
     * Start ESP32 monitoring
     */
    private fun startESP32Monitoring() {
        viewModelScope.launch {
            try {
                bpmService?.startPolling()
                _isServiceRunning.value = true
                Timber.d("ESP32 BPM monitoring started")
            } catch (e: Exception) {
                Timber.e(e, "Failed to start ESP32 BPM monitoring")
            }
        }
    }

    /**
     * Stop ESP32 monitoring
     */
    private fun stopESP32Monitoring() {
        viewModelScope.launch {
            try {
                bpmService?.stopPolling()
                _isServiceRunning.value = false
                Timber.d("ESP32 BPM monitoring stopped")
            } catch (e: Exception) {
                Timber.e(e, "Failed to stop ESP32 BPM monitoring")
            }
        }
    }

    /**
     * Start local (microphone) monitoring
     */
    private fun startLocalMonitoring() {
        viewModelScope.launch {
            try {
                if (localBPMDetector == null) {
                    localBPMDetector = LocalBPMDetector(
                        sampleRate = _localSampleRate.value,
                        fftSize = _localFftSize.value,
                        minBpm = _localMinBpm.value,
                        maxBpm = _localMaxBpm.value
                    )
                }

                val started = localBPMDetector?.startDetection() ?: false
                if (started) {
                    _isServiceRunning.value = true
                    _connectionStatus.value = ConnectionStatus.CONNECTED

                    // Observe local detector's BPM data
                    localDetectionJob = launch {
                        localBPMDetector?.bpmData?.collect { bpmData ->
                            bpmData?.let {
                                _bpmDataFlow.value = it
                            }
                        }
                    }

                    // Observe frequency spectrum
                    launch {
                        localBPMDetector?.frequencySpectrum?.collect { spectrum ->
                            _frequencySpectrum.value = spectrum
                        }
                    }

                    Timber.d("Local BPM monitoring started")
                } else {
                    _connectionStatus.value = ConnectionStatus.ERROR
                    Timber.e("Failed to start local BPM detection")
                }
            } catch (e: Exception) {
                Timber.e(e, "Failed to start local BPM monitoring")
                _connectionStatus.value = ConnectionStatus.ERROR
            }
        }
    }

    /**
     * Stop local (microphone) monitoring
     */
    private fun stopLocalMonitoring() {
        viewModelScope.launch {
            try {
                localDetectionJob?.cancel()
                localDetectionJob = null
                localBPMDetector?.stopDetection()
                _isServiceRunning.value = false
                _connectionStatus.value = ConnectionStatus.DISCONNECTED
                Timber.d("Local BPM monitoring stopped")
            } catch (e: Exception) {
                Timber.e(e, "Failed to stop local BPM monitoring")
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
            saveSettings()
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
            saveSettings()
            Timber.d("Polling interval updated to: ${clampedInterval}ms")
        }
    }

    /**
     * Get current BPM value as formatted string
     */
    fun getFormattedBpm(): String {
        return _bpmDataFlow.value?.getFormattedBpm() ?: "--"
    }

    /**
     * Get current confidence as percentage
     */
    fun getConfidencePercentage(): Int {
        return _bpmDataFlow.value?.getConfidencePercentage() ?: 0
    }

    /**
     * Get current signal level as percentage
     */
    fun getSignalLevelPercentage(): Int {
        return _bpmDataFlow.value?.getSignalLevelPercentage() ?: 0
    }

    /**
     * Get status description
     */
    fun getStatusDescription(): String {
        return _bpmDataFlow.value?.getStatusDescription() ?: "Disconnected"
    }

    /**
     * Check if currently detecting BPM
     */
    fun isDetecting(): Boolean {
        return _bpmDataFlow.value?.isDetecting() ?: false
    }

    /**
     * Check if there's low signal
     */
    fun hasLowSignal(): Boolean {
        return _bpmDataFlow.value?.hasLowSignal() ?: false
    }

    /**
     * Check if there's an error
     */
    fun hasError(): Boolean {
        return _bpmDataFlow.value?.hasError() ?: false
    }

    /**
     * Get connection status description
     */
    fun getConnectionStatusDescription(): String {
        return when (connectionStatus.value) {
            ConnectionStatus.CONNECTED -> "Connected"
            ConnectionStatus.CONNECTING -> "Connecting..."
            ConnectionStatus.SEARCHING -> "Searching for device..."
            ConnectionStatus.DISCONNECTED -> "Disconnected"
            ConnectionStatus.ERROR -> "Connection Error"
        }
    }

    // Observers for service LiveData
    private val bpmDataObserver = androidx.lifecycle.Observer<BPMData> { data ->
        _bpmDataFlow.value = data
    }

    private val connectionStatusObserver = androidx.lifecycle.Observer<ConnectionStatus> { status ->
        _connectionStatus.value = status
    }

    /**
     * Update local detector settings
     */
    fun updateLocalDetectorSettings(
        sampleRate: Int? = null,
        fftSize: Int? = null,
        minBpm: Int? = null,
        maxBpm: Int? = null
    ) {
        sampleRate?.let { _localSampleRate.value = it }
        fftSize?.let { _localFftSize.value = it }
        minBpm?.let { _localMinBpm.value = it }
        maxBpm?.let { _localMaxBpm.value = it }

        viewModelScope.launch {
            localBPMDetector?.updateConfiguration(
                sampleRate = sampleRate,
                fftSize = fftSize,
                minBpm = minBpm,
                maxBpm = maxBpm
            )
        }
    }

    /**
     * Start recording audio to file
     */
    fun startRecording(outputFile: java.io.File) {
        viewModelScope.launch {
            val result = localBPMDetector?.startRecordingToFile(outputFile) ?: false
            _isRecording.value = result
        }
    }

    /**
     * Stop recording audio
     */
    fun stopRecording(): java.io.File? {
        val file = localBPMDetector?.stopRecordingToFile()
        _isRecording.value = false
        return file
    }

    /**
     * Analyze recorded audio file
     */
    fun analyzeAudioFile(file: java.io.File) {
        viewModelScope.launch {
            val result = localBPMDetector?.analyzeAudioFile(file)
            result?.let {
                _bpmDataFlow.value = it
            }
        }
    }

    /**
     * Load saved settings from SharedPreferences
     */
    private fun loadSavedSettings() {
        val savedIp = prefs.getString("server_ip", "192.168.4.1") ?: "192.168.4.1"
        val savedInterval = prefs.getLong("polling_interval", 500L)
        val savedMode = DetectionMode.valueOf(
            prefs.getString("detection_mode", DetectionMode.ESP32.name) ?: DetectionMode.ESP32.name
        )

        _serverIp.value = savedIp
        _pollingInterval.value = savedInterval
        _detectionMode.value = savedMode

        Timber.d("Loaded saved settings: IP=$savedIp, interval=$savedInterval, mode=$savedMode")
    }

    /**
     * Save current settings to SharedPreferences
     */
    private fun saveSettings() {
        prefs.edit().apply {
            putString("server_ip", _serverIp.value)
            putLong("polling_interval", _pollingInterval.value)
            putString("detection_mode", _detectionMode.value.name)
            apply()
        }
        Timber.d("Saved settings: IP=${_serverIp.value}, interval=${_pollingInterval.value}, mode=${_detectionMode.value}")
    }

    /**
     * Automatically discover and connect to ESP32 device (WiFi + Network)
     */
    fun autoDiscoverDevice() {
        if (_detectionMode.value != DetectionMode.ESP32) {
            return
        }

        viewModelScope.launch {
            try {
                _connectionStatus.value = ConnectionStatus.SEARCHING
                Timber.d("Starting enhanced auto-discovery for ESP32 device")

                // Retry WiFi scan up to 3 times with exponential backoff
                var scanSuccessful = false
                for (attempt in 1..3) {
                    Timber.d("WiFi scan attempt $attempt/3")

                    // Scan for ESP32 WiFi network
                    scanForEsp32Wifi()

                    // Wait for scan to complete with timeout
                    val scanTimeoutMs = 3000L * attempt // Increasing timeout
                    var elapsed = 0L
                    while (elapsed < scanTimeoutMs && _isScanningWifi.value) {
                        kotlinx.coroutines.delay(500)
                        elapsed += 500
                    }

                    if (_esp32NetworkFound.value) {
                        scanSuccessful = true
                        Timber.d("ESP32 network found on attempt $attempt")
                        break
                    } else if (attempt < 3) {
                        val backoffDelay = 1000L * attempt // 1s, 2s, 3s
                        Timber.d("ESP32 network not found, retrying in ${backoffDelay}ms")
                        kotlinx.coroutines.delay(backoffDelay)
                    }
                }

                if (!scanSuccessful) {
                    Timber.w("ESP32 network not found after 3 attempts")
                    _connectionStatus.value = ConnectionStatus.DISCONNECTED
                    return@launch
                }

                // If ESP32 network found and not already connected, attempt connection
                if (!wifiManager.isConnectedToEsp32()) {
                    Timber.d("ESP32 WiFi network found, attempting connection")
                    _isConnectingToWifi.value = true

                    val connected = wifiManager.connectToEsp32Network()

                    if (connected) {
                        Timber.d("WiFi connection initiated, monitoring connection state...")

                        // Monitor connection state for up to 10 seconds
                        var connectionEstablished = false
                        for (i in 1..20) { // 20 * 500ms = 10 seconds
                            kotlinx.coroutines.delay(500)
                            if (wifiManager.isConnectedToEsp32()) {
                                connectionEstablished = true
                                Timber.d("Successfully connected to ESP32 WiFi network")
                                break
                            }
                        }

                        if (!connectionEstablished) {
                            Timber.w("WiFi connection initiated but not established within timeout")
                            _connectionStatus.value = ConnectionStatus.ERROR
                            _isConnectingToWifi.value = false
                            return@launch
                        }
                    } else {
                        Timber.w("Failed to initiate ESP32 WiFi network connection")
                        _connectionStatus.value = ConnectionStatus.ERROR
                        _isConnectingToWifi.value = false
                        return@launch
                    }

                    _isConnectingToWifi.value = false
                }

                // Now verify HTTP connectivity with retries
                Timber.d("WiFi connected, testing HTTP connectivity...")
                testHttpConnectivityWithRetry()

            } catch (e: Exception) {
                Timber.e(e, "Auto-discovery failed with exception")
                _connectionStatus.value = ConnectionStatus.ERROR
            }
        }
    }

    // Add HTTP connectivity test with retry
    private suspend fun testHttpConnectivityWithRetry() {
        val apiClient = com.sparesparrow.bpmdetector.network.BPMApiClient.createWithIp(_serverIp.value)

        // Retry HTTP connection up to 3 times
        for (attempt in 1..3) {
            try {
                Timber.d("HTTP connectivity test attempt $attempt/3")
                val isReachable = apiClient.isServerReachable()

                if (isReachable) {
                    Timber.d("Auto-discovery successful - device found at ${_serverIp.value}")
                    _connectionStatus.value = ConnectionStatus.CONNECTED

                    // Start monitoring automatically if device is found
                    if (bpmService != null && !_isServiceRunning.value) {
                        startMonitoring()
                    }
                    return
                } else {
                    if (attempt < 3) {
                        val backoffDelay = 1000L * attempt
                        Timber.d("HTTP test failed, retrying in ${backoffDelay}ms")
                        kotlinx.coroutines.delay(backoffDelay)
                    }
                }
            } catch (e: Exception) {
                Timber.w(e, "HTTP connectivity test failed on attempt $attempt")
                if (attempt < 3) {
                    kotlinx.coroutines.delay(1000L * attempt)
                }
            }
        }

        Timber.d("HTTP connectivity test failed after 3 attempts")
        _connectionStatus.value = ConnectionStatus.DISCONNECTED
    }

    /**
     * Scan for ESP32 WiFi network
     */
    fun scanForEsp32Wifi() {
        viewModelScope.launch {
            try {
                _isScanningWifi.value = true
                Timber.d("Starting WiFi scan for ESP32 network")

                wifiManager.scanWifiNetworks().collect { results ->
                    _wifiScanResults.value = results
                    val esp32Found = wifiManager.isEsp32NetworkAvailable(results)
                    _esp32NetworkFound.value = esp32Found

                    Timber.d("WiFi scan completed. ESP32 network found: $esp32Found")
                    _isScanningWifi.value = false
                }
            } catch (e: Exception) {
                Timber.e(e, "WiFi scan failed")
                _isScanningWifi.value = false
                _esp32NetworkFound.value = false
            }
        }
    }

    /**
     * Connect to ESP32 WiFi network manually
     */
    fun connectToEsp32Wifi() {
        viewModelScope.launch {
            try {
                _isConnectingToWifi.value = true
                Timber.d("Manually connecting to ESP32 WiFi network")

                val connected = wifiManager.connectToEsp32Network()

                if (connected) {
                    Timber.d("Successfully connected to ESP32 WiFi network")
                    // Trigger auto-discovery again to check network connectivity
                    kotlinx.coroutines.delay(2000)
                    autoDiscoverDevice()
                } else {
                    Timber.w("Failed to connect to ESP32 WiFi network")
                }
            } catch (e: Exception) {
                Timber.e(e, "WiFi connection failed")
            } finally {
                _isConnectingToWifi.value = false
            }
        }
    }

    /**
     * Get WiFi connection info
     */
    fun getWifiConnectionInfo(): String = wifiManager.getCurrentConnectionInfo()

    /**
     * Check if connected to ESP32 WiFi
     */
    fun isConnectedToEsp32Wifi(): Boolean = wifiManager.isConnectedToEsp32()

    /**
     * Get WiFi state description
     */
    fun getWifiStateDescription(): String = wifiManager.getWifiStateDescription()

    /**
     * Get WiFi debug information
     */
    fun getWifiDebugInfo(): String = wifiManager.getWifiDebugInfo()

    /**
     * Check if WiFi scanning is supported
     */
    fun isWifiScanningSupported(): Boolean = wifiManager.isWifiScanningSupported()

    /**
     * Get all available WiFi networks (for debugging)
     */
    fun getAllWifiNetworks(): List<String> {
        return _wifiScanResults.value.map { it.SSID }.filter { it.isNotEmpty() }
    }

    override fun onCleared() {
        super.onCleared()
        clearBPMService()
        localDetectionJob?.cancel()
        localBPMDetector?.release()
        localBPMDetector = null

        // Unregister network callback
        try {
            connectivityManager.unregisterNetworkCallback(networkCallback)
        } catch (e: Exception) {
            Timber.w(e, "Error unregistering network callback")
        }
    }
}

