package com.sparesparrow.bpmdetector.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.media.MediaPlayer
import com.sparesparrow.bpmdetector.models.BPMData
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import timber.log.Timber
import kotlin.coroutines.coroutineContext
import kotlin.math.*
import java.io.File
import java.io.FileOutputStream
import java.io.IOException

/**
 * Local BPM detector using phone's microphone
 * Implements FFT-based beat detection similar to ESP32 implementation
 */
class LocalBPMDetector(
    sampleRate: Int = 16000, // Android typical sample rate
    fftSize: Int = 1024,
    minBpm: Int = 60,
    maxBpm: Int = 200
) {
    // Configurable parameters
    private var _sampleRate = MutableStateFlow(sampleRate)
    var sampleRate: StateFlow<Int> = _sampleRate.asStateFlow()
    
    private var _fftSize = MutableStateFlow(fftSize)
    var fftSize: StateFlow<Int> = _fftSize.asStateFlow()
    
    private var _minBpm = MutableStateFlow(minBpm)
    var minBpm: StateFlow<Int> = _minBpm.asStateFlow()
    
    private var _maxBpm = MutableStateFlow(maxBpm)
    var maxBpm: StateFlow<Int> = _maxBpm.asStateFlow()

    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var detectionJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())

    // BPM detection state
    private val _bpmData = MutableStateFlow<BPMData?>(null)
    val bpmData: StateFlow<BPMData?> = _bpmData.asStateFlow()

    private val _isDetecting = MutableStateFlow(false)
    val isDetecting: StateFlow<Boolean> = _isDetecting.asStateFlow()

    // Frequency spectrum data (for visualization)
    private val _frequencySpectrum = MutableStateFlow<FloatArray?>(null)
    val frequencySpectrum: StateFlow<FloatArray?> = _frequencySpectrum.asStateFlow()

    // Audio buffer (dynamically sized)
    private var audioBuffer = ShortArray(fftSize)
    private var fftBuffer = FloatArray(fftSize * 2) // Complex FFT buffer
    private var magnitudeBuffer = FloatArray(fftSize / 2)
    
    // Audio recording state
    private var isRecordingToFile = false
    private var recordingFile: File? = null
    private var recordingJob: Job? = null

    // BPM detection state
    private val bpmHistory = mutableListOf<Float>()
    private var lastDetectionTime = 0L

    companion object {
        private const val TAG = "LocalBPMDetector"
        private const val CONFIDENCE_THRESHOLD = 0.5f
        private const val MIN_SIGNAL_LEVEL = 0.1f
    }

    /**
     * Update configuration parameters
     */
    fun updateConfiguration(
        sampleRate: Int? = null,
        fftSize: Int? = null,
        minBpm: Int? = null,
        maxBpm: Int? = null
    ) {
        val wasRecording = isRecording
        if (wasRecording) {
            stopDetection()
        }

        sampleRate?.let {
            _sampleRate.value = it.coerceIn(8000, 48000)
        }
        fftSize?.let {
            val newSize = it.coerceIn(256, 4096)
            // Ensure fftSize is power of 2
            val powerOf2 = 1 shl (31 - Integer.numberOfLeadingZeros(newSize))
            _fftSize.value = powerOf2
        }
        minBpm?.let {
            _minBpm.value = it.coerceIn(30, 200)
        }
        maxBpm?.let {
            _maxBpm.value = it.coerceIn(60, 300)
        }

        // Reallocate buffers if fftSize changed
        if (fftSize != null) {
            val newFftSize = _fftSize.value
            audioBuffer = ShortArray(newFftSize)
            fftBuffer = FloatArray(newFftSize * 2)
            magnitudeBuffer = FloatArray(newFftSize / 2)
        }

        if (wasRecording) {
            startDetection()
        }
    }

    /**
     * Start BPM detection using microphone
     */
    fun startDetection(): Boolean {
        if (isRecording) {
            Timber.w("BPM detection already running")
            return false
        }

        return try {
            val currentSampleRate = _sampleRate.value
            val currentFftSize = _fftSize.value
            
            val bufferSize = AudioRecord.getMinBufferSize(
                currentSampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT
            )

            if (bufferSize == AudioRecord.ERROR_BAD_VALUE || bufferSize == AudioRecord.ERROR) {
                Timber.e("Invalid audio parameters")
                return false
            }

            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                currentSampleRate,
                AudioFormat.CHANNEL_IN_MONO,
                AudioFormat.ENCODING_PCM_16BIT,
                bufferSize * 2
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Timber.e("AudioRecord initialization failed")
                audioRecord?.release()
                audioRecord = null
                return false
            }

            isRecording = true
            _isDetecting.value = true
            audioRecord?.startRecording()

            detectionJob = scope.launch {
                processAudio()
            }

            Timber.d("Local BPM detection started")
            true
        } catch (e: Exception) {
            Timber.e(e, "Failed to start BPM detection")
            isRecording = false
            _isDetecting.value = false
            false
        }
    }

    /**
     * Stop BPM detection
     */
    fun stopDetection() {
        if (!isRecording) {
            return
        }

        isRecording = false
        _isDetecting.value = false

        detectionJob?.cancel()
        detectionJob = null

        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null

        Timber.d("Local BPM detection stopped")
    }

    /**
     * Process audio samples and detect BPM
     */
    private suspend fun processAudio() {
        while (isRecording && coroutineContext.isActive) {
            try {
                val currentFftSize = _fftSize.value
                val samplesRead = audioRecord?.read(audioBuffer, 0, currentFftSize) ?: 0

                if (samplesRead < 0) {
                    Timber.e("AudioRecord read error: $samplesRead")
                    delay(100)
                    continue
                }

                if (samplesRead < currentFftSize) {
                    delay(10)
                    continue
                }

                // Convert to float and apply window function
                for (i in 0 until currentFftSize) {
                    val sample = audioBuffer[i].toFloat() / Short.MAX_VALUE
                    fftBuffer[i * 2] = sample * windowFunction(i, currentFftSize) // Real part
                    fftBuffer[i * 2 + 1] = 0f // Imaginary part
                }

                // Perform FFT
                performFFT(fftBuffer, currentFftSize)

                // Calculate magnitude spectrum
                for (i in 0 until currentFftSize / 2) {
                    val real = fftBuffer[i * 2]
                    val imag = fftBuffer[i * 2 + 1]
                    magnitudeBuffer[i] = sqrt(real * real + imag * imag)
                }

                // Update frequency spectrum for visualization
                _frequencySpectrum.value = magnitudeBuffer.copyOf()

                // Detect BPM from frequency spectrum
                val bpmResult = detectBPMFromSpectrum()

                if (bpmResult != null) {
                    val currentTime = System.currentTimeMillis()
                    
                    // Update BPM data
                    _bpmData.value = BPMData(
                        bpm = bpmResult.bpm,
                        confidence = bpmResult.confidence,
                        signalLevel = bpmResult.signalLevel,
                        status = if (bpmResult.confidence >= CONFIDENCE_THRESHOLD) "detecting" else "low_confidence",
                        timestamp = currentTime
                    )

                    lastDetectionTime = currentTime
                } else {
                    // Low signal or no detection
                    _bpmData.value = BPMData(
                        bpm = 0f,
                        confidence = 0f,
                        signalLevel = calculateSignalLevel(),
                        status = "low_signal",
                        timestamp = System.currentTimeMillis()
                    )
                }

                // Process at ~10Hz (100ms intervals)
                delay(100)
            } catch (e: Exception) {
                Timber.e(e, "Error processing audio")
                delay(100)
            }
        }
    }

    /**
     * Simple window function (Hanning window)
     */
    private fun windowFunction(n: Int, size: Int): Float {
        return 0.5f * (1f - cos(2f * PI.toFloat() * n / (size - 1)))
    }

    /**
     * Perform FFT using Cooley-Tukey algorithm
     */
    private fun performFFT(buffer: FloatArray, size: Int) {
        // Bit-reverse permutation
        var j = 0
        for (i in 1 until size) {
            var bit = size shr 1
            while (j and bit != 0) {
                j = j xor bit
                bit = bit shr 1
            }
            j = j xor bit

            if (i < j) {
                val tempReal = buffer[i * 2]
                val tempImag = buffer[i * 2 + 1]
                buffer[i * 2] = buffer[j * 2]
                buffer[i * 2 + 1] = buffer[j * 2 + 1]
                buffer[j * 2] = tempReal
                buffer[j * 2 + 1] = tempImag
            }
        }

        // FFT computation
        var step = 1
        while (step < size) {
            val step2 = step * 2
            val angle = -PI.toFloat() / step
            val wReal = cos(angle)
            val wImag = sin(angle)

            for (i in 0 until size step step2) {
                var wRealCurrent = 1f
                var wImagCurrent = 0f

                for (j in 0 until step) {
                    val u = i + j
                    val v = u + step

                    val tReal = wRealCurrent * buffer[v * 2] - wImagCurrent * buffer[v * 2 + 1]
                    val tImag = wRealCurrent * buffer[v * 2 + 1] + wImagCurrent * buffer[v * 2]

                    buffer[v * 2] = buffer[u * 2] - tReal
                    buffer[v * 2 + 1] = buffer[u * 2 + 1] - tImag
                    buffer[u * 2] += tReal
                    buffer[u * 2 + 1] += tImag

                    val nextWReal = wRealCurrent * wReal - wImagCurrent * wImag
                    val nextWImag = wRealCurrent * wImag + wImagCurrent * wReal
                    wRealCurrent = nextWReal
                    wImagCurrent = nextWImag
                }
            }
            step = step2
        }
    }

    /**
     * Detect BPM from frequency spectrum
     */
    private fun detectBPMFromSpectrum(): BPMResult? {
        // Find peak in frequency range corresponding to BPM
        val currentMinBpm = _minBpm.value
        val currentMaxBpm = _maxBpm.value
        val currentSampleRate = _sampleRate.value
        val currentFftSize = _fftSize.value
        
        val minFreq = currentMinBpm / 60f
        val maxFreq = currentMaxBpm / 60f
        val freqResolution = currentSampleRate.toFloat() / currentFftSize

        var maxMagnitude = 0f
        var peakFreq = 0f
        var totalEnergy = 0f

        // Calculate energy in BPM range
        val minBin = (minFreq / freqResolution).toInt().coerceAtLeast(1)
        val maxBin = (maxFreq / freqResolution).toInt().coerceAtMost(currentFftSize / 2 - 1)

        for (i in minBin..maxBin) {
            val magnitude = magnitudeBuffer[i]
            totalEnergy += magnitude

            if (magnitude > maxMagnitude) {
                maxMagnitude = magnitude
                peakFreq = i * freqResolution
            }
        }

        // Calculate signal level
        val signalLevel = (totalEnergy / (maxBin - minBin + 1)).coerceIn(0f, 1f)

        if (signalLevel < MIN_SIGNAL_LEVEL) {
            return null // Too low signal
        }

        // Convert frequency to BPM
        val detectedBpm = peakFreq * 60f

        if (detectedBpm < currentMinBpm || detectedBpm > currentMaxBpm) {
            return null
        }

        // Calculate confidence based on peak prominence
        val avgMagnitude = totalEnergy / (maxBin - minBin + 1)
        val confidence = (maxMagnitude / (avgMagnitude + 0.001f)).coerceIn(0f, 1f)

        // Add to history for smoothing
        bpmHistory.add(detectedBpm)
        if (bpmHistory.size > 10) {
            bpmHistory.removeAt(0)
        }

        // Calculate smoothed BPM
        val smoothedBpm = if (bpmHistory.isNotEmpty()) {
            bpmHistory.average().toFloat()
        } else {
            detectedBpm
        }

        return BPMResult(
            bpm = smoothedBpm,
            confidence = confidence,
            signalLevel = signalLevel
        )
    }

    /**
     * Calculate overall signal level
     */
    private fun calculateSignalLevel(): Float {
        val currentFftSize = _fftSize.value
        var totalEnergy = 0f
        for (i in 0 until currentFftSize / 2) {
            totalEnergy += magnitudeBuffer[i]
        }
        return (totalEnergy / (currentFftSize / 2)).coerceIn(0f, 1f)
    }

    /**
     * Start recording audio to file
     */
    fun startRecordingToFile(outputFile: File): Boolean {
        if (isRecordingToFile) {
            Timber.w("Already recording to file")
            return false
        }

        if (!isRecording) {
            Timber.w("BPM detection must be running to record")
            return false
        }

        return try {
            recordingFile = outputFile
            isRecordingToFile = true

            recordingJob = scope.launch {
                recordAudioToFile(outputFile)
            }

            Timber.d("Started recording to file: ${outputFile.absolutePath}")
            true
        } catch (e: Exception) {
            Timber.e(e, "Failed to start recording")
            isRecordingToFile = false
            recordingFile = null
            false
        }
    }

    /**
     * Stop recording audio to file
     */
    fun stopRecordingToFile(): File? {
        if (!isRecordingToFile) {
            return null
        }

        isRecordingToFile = false
        recordingJob?.cancel()
        recordingJob = null

        val file = recordingFile
        recordingFile = null

        Timber.d("Stopped recording to file")
        return file
    }

    /**
     * Record audio to file (PCM format)
     */
    private suspend fun recordAudioToFile(file: File) {
        val currentFftSize = _fftSize.value
        val buffer = ShortArray(currentFftSize)
        
        try {
            FileOutputStream(file).use { outputStream ->
                while (isRecordingToFile && isRecording && coroutineContext.isActive) {
                    val samplesRead = audioRecord?.read(buffer, 0, currentFftSize) ?: 0
                    
                    if (samplesRead > 0) {
                        // Write PCM data to file
                        val byteArray = ByteArray(samplesRead * 2)
                        for (i in 0 until samplesRead) {
                            val sample = buffer[i].toInt()
                            byteArray[i * 2] = (sample and 0xFF).toByte()
                            byteArray[i * 2 + 1] = ((sample shr 8) and 0xFF).toByte()
                        }
                        outputStream.write(byteArray)
                    }
                    
                    delay(10)
                }
            }
            Timber.d("Recording completed: ${file.absolutePath}")
        } catch (e: Exception) {
            Timber.e(e, "Error recording audio to file")
        }
    }

    /**
     * Analyze recorded audio file
     */
    suspend fun analyzeAudioFile(file: File): BPMData? {
        if (!file.exists() || !file.canRead()) {
            Timber.e("Cannot read audio file: ${file.absolutePath}")
            return null
        }

        return withContext(Dispatchers.IO) {
            try {
                val currentFftSize = _fftSize.value
                val currentSampleRate = _sampleRate.value
                val buffer = ShortArray(currentFftSize)
                val fileData = file.readBytes()
                
                // Process audio file in chunks
                var maxBpm = 0f
                var maxConfidence = 0f
                var totalSignalLevel = 0f
                var validSamples = 0

                var offset = 0
                while (offset < fileData.size - currentFftSize * 2) {
                    // Read samples
                    for (i in 0 until currentFftSize) {
                        if (offset + i * 2 + 1 < fileData.size) {
                            val low = fileData[offset + i * 2].toInt() and 0xFF
                            val high = fileData[offset + i * 2 + 1].toInt() and 0xFF
                            buffer[i] = ((high shl 8) or low).toShort()
                        }
                    }

                    // Process chunk
                    for (i in 0 until currentFftSize) {
                        val sample = buffer[i].toFloat() / Short.MAX_VALUE
                        fftBuffer[i * 2] = sample * windowFunction(i, currentFftSize)
                        fftBuffer[i * 2 + 1] = 0f
                    }

                    performFFT(fftBuffer, currentFftSize)

                    for (i in 0 until currentFftSize / 2) {
                        val real = fftBuffer[i * 2]
                        val imag = fftBuffer[i * 2 + 1]
                        magnitudeBuffer[i] = sqrt(real * real + imag * imag)
                    }

                    val result = detectBPMFromSpectrum()
                    if (result != null) {
                        if (result.confidence > maxConfidence) {
                            maxBpm = result.bpm
                            maxConfidence = result.confidence
                        }
                        totalSignalLevel += result.signalLevel
                        validSamples++
                    }

                    offset += currentFftSize * 2
                }

                if (validSamples > 0) {
                    BPMData(
                        bpm = maxBpm,
                        confidence = maxConfidence,
                        signalLevel = totalSignalLevel / validSamples,
                        status = if (maxConfidence >= CONFIDENCE_THRESHOLD) "detecting" else "low_confidence",
                        timestamp = System.currentTimeMillis()
                    )
                } else {
                    null
                }
            } catch (e: Exception) {
                Timber.e(e, "Error analyzing audio file")
                null
            }
        }
    }

    /**
     * Cleanup resources
     */
    fun release() {
        stopDetection()
        scope.cancel()
    }

    /**
     * Internal data class for BPM detection result
     */
    private data class BPMResult(
        val bpm: Float,
        val confidence: Float,
        val signalLevel: Float
    )
}