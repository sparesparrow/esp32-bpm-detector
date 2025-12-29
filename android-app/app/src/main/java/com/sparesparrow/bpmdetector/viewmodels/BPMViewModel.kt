package com.sparesparrow.bpmdetector.viewmodels

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.sparesparrow.bpmdetector.audio.LocalBPMDetector
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.services.ConnectionStatus
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

    // BPM Data
    private val _bpmData = MutableLiveData<BPMData>()
    val bpmData: LiveData<BPMData> = _bpmData
    
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
    private val _serverIp = MutableStateFlow("192.168.200.23")
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

    init {
        // Initialize with loading state
        val loadingData = BPMData.createLoading()
        _bpmData.value = loadingData
        _bpmDataFlow.value = loadingData
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
                                _bpmData.postValue(it)
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
        return when (connectionStatus.value) {
            ConnectionStatus.CONNECTED -> "Connected"
            ConnectionStatus.CONNECTING -> "Connecting..."
            ConnectionStatus.DISCONNECTED -> "Disconnected"
            ConnectionStatus.ERROR -> "Connection Error"
        }
    }

    // Observers for service LiveData
    private val bpmDataObserver = androidx.lifecycle.Observer<BPMData> { data ->
        _bpmData.postValue(data)
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
                _bpmData.postValue(it)
                _bpmDataFlow.value = it
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        clearBPMService()
        localDetectionJob?.cancel()
        localBPMDetector?.release()
        localBPMDetector = null
    }
}

