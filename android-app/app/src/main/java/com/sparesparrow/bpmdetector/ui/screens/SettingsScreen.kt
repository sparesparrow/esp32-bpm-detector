package com.sparesparrow.bpmdetector.ui.screens

import android.Manifest
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.sparesparrow.bpmdetector.network.BPMApiClient
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import com.sparesparrow.bpmdetector.viewmodels.DetectionMode
import kotlinx.coroutines.launch
import kotlin.math.log2

/**
 * Settings Screen - Configure ESP32 connection and monitoring parameters
 */
@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun SettingsScreen(viewModel: BPMViewModel) {
    val serverIp by viewModel.serverIp.collectAsState()
    val pollingInterval by viewModel.pollingInterval.collectAsState()
    val connectionStatus by viewModel.connectionStatus.collectAsState()
    val detectionMode by viewModel.detectionMode.collectAsState()

    val coroutineScope = rememberCoroutineScope()

    // Audio permission state
    val audioPermissionState = rememberMultiplePermissionsState(
        permissions = listOf(Manifest.permission.RECORD_AUDIO)
    )

    var ipInput by remember { mutableStateOf(serverIp) }
    var intervalInput by remember { mutableStateOf(pollingInterval.toString()) }
    var isTestingConnection by remember { mutableStateOf(false) }
    var connectionTestResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "BPM Detection Settings",
            style = MaterialTheme.typography.headlineMedium
        )

        // Detection Mode Selection
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Detection Mode",
                    style = MaterialTheme.typography.titleMedium
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    FilterChip(
                        selected = detectionMode == DetectionMode.ESP32,
                        onClick = {
                            coroutineScope.launch {
                                viewModel.setDetectionMode(DetectionMode.ESP32)
                            }
                        },
                        label = { Text("ESP32 Device") }
                    )
                    
                    FilterChip(
                        selected = detectionMode == DetectionMode.LOCAL,
                        onClick = {
                            if (audioPermissionState.allPermissionsGranted) {
                                coroutineScope.launch {
                                    viewModel.setDetectionMode(DetectionMode.LOCAL)
                                }
                            } else {
                                audioPermissionState.launchMultiplePermissionRequest()
                            }
                        },
                        label = { Text("Phone Microphone") }
                    )
                }
                
                Text(
                    text = when (detectionMode) {
                        DetectionMode.ESP32 -> "Connect to ESP32 device over network"
                        DetectionMode.LOCAL -> "Use phone's built-in microphone for BPM detection"
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        // ESP32 Settings (only show when ESP32 mode is selected)
        if (detectionMode == DetectionMode.ESP32) {
            Text(
                text = "ESP32 Connection Settings",
                style = MaterialTheme.typography.titleLarge
            )

        // Server IP Configuration
        OutlinedTextField(
            value = ipInput,
            onValueChange = { ipInput = it },
            label = { Text("ESP32 Server IP Address") },
            placeholder = { Text("192.168.1.100") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            supportingText = {
                Text("IP address of your ESP32 device")
            },
            isError = ipInput.isNotEmpty() && !BPMApiClient.isValidIpAddress(ipInput),
            modifier = Modifier.fillMaxWidth()
        )

        // Polling Interval Configuration
        OutlinedTextField(
            value = intervalInput,
            onValueChange = {
                // Only allow numeric input
                if (it.all { char -> char.isDigit() }) {
                    intervalInput = it
                }
            },
            label = { Text("Polling Interval (ms)") },
            placeholder = { Text("500") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            supportingText = {
                Text("How often to check for BPM updates (100-2000ms)")
            },
            modifier = Modifier.fillMaxWidth()
        )

        // Connection Test Button
        Button(
            onClick = {
                coroutineScope.launch {
                    connectionTestResult = null
                    isTestingConnection = true

                    try {
                        val apiClient = BPMApiClient.createWithIp(ipInput)
                        val isReachable = apiClient.isServerReachable()

                        connectionTestResult = if (isReachable) {
                            "✓ Connection successful!"
                        } else {
                            "✗ Cannot reach ESP32 server"
                        }
                    } catch (e: Exception) {
                        connectionTestResult = "✗ Connection failed: ${e.message}"
                    } finally {
                        isTestingConnection = false
                    }
                }
            },
            enabled = !isTestingConnection && BPMApiClient.isValidIpAddress(ipInput),
            modifier = Modifier.fillMaxWidth()
        ) {
            if (isTestingConnection) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text("Testing Connection...")
            } else {
                Text("Test Connection")
            }
        }

        // Connection Test Result
        connectionTestResult?.let { result ->
            val isSuccess = result.startsWith("✓")
            Surface(
                color = if (isSuccess) Color(0xFF4CAF50) else Color(0xFFF44336),
                shape = MaterialTheme.shapes.medium,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = result,
                    color = Color.White,
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(12.dp)
                )
            }
        }

        // Current Connection Status
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Text(
                    text = "Current Connection Status",
                    style = MaterialTheme.typography.titleMedium
                )

                Text(
                    text = viewModel.getConnectionStatusDescription(),
                    style = MaterialTheme.typography.bodyMedium,
                    color = when {
                        connectionStatus.isConnected() -> Color(0xFF4CAF50)
                        connectionStatus.isConnecting() -> Color(0xFFFF9800)
                        connectionStatus.hasError() -> Color(0xFFF44336)
                        else -> MaterialTheme.colorScheme.onSurface
                    }
                )

                if (connectionStatus.isConnected()) {
                    Text(
                        text = "BPM: ${viewModel.getFormattedBpm()} | Confidence: ${viewModel.getConfidencePercentage()}%",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            }

            // Save Settings Button (ESP32 mode only)
            Spacer(modifier = Modifier.weight(1f))

            Button(
                onClick = {
                    // Update ViewModel with new settings
                    viewModel.updateServerIp(ipInput)
                    intervalInput.toLongOrNull()?.let { interval ->
                        viewModel.updatePollingInterval(interval)
                    }
                },
                enabled = BPMApiClient.isValidIpAddress(ipInput) &&
                         intervalInput.toLongOrNull()?.let { it in 100L..2000L } == true,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Save Settings",
                    style = MaterialTheme.typography.titleMedium
                )
            }
        }

        // Local Mode Settings (when LOCAL mode is selected)
        if (detectionMode == DetectionMode.LOCAL) {
            Text(
                text = "Local Detection Settings",
                style = MaterialTheme.typography.titleLarge
            )

            val localSampleRate by viewModel.localSampleRate.collectAsState()
            val localFftSize by viewModel.localFftSize.collectAsState()
            val localMinBpm by viewModel.localMinBpm.collectAsState()
            val localMaxBpm by viewModel.localMaxBpm.collectAsState()
            val isRecording by viewModel.isRecording.collectAsState()

            var sampleRateInput by remember { mutableStateOf(localSampleRate.toString()) }
            var fftSizeInput by remember { mutableStateOf(localFftSize.toString()) }
            var minBpmInput by remember { mutableStateOf(localMinBpm.toString()) }
            var maxBpmInput by remember { mutableStateOf(localMaxBpm.toString()) }

            // Sample Rate
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Sample Rate: ${localSampleRate} Hz",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Slider(
                        value = localSampleRate.toFloat(),
                        onValueChange = { value ->
                            val newValue = value.toInt().coerceIn(8000, 48000)
                            sampleRateInput = newValue.toString()
                            viewModel.updateLocalDetectorSettings(sampleRate = newValue)
                        },
                        valueRange = 8000f..48000f,
                        steps = 7, // 8kHz, 16kHz, 24kHz, 32kHz, 40kHz, 48kHz
                        modifier = Modifier.fillMaxWidth()
                    )
                    Text(
                        text = "Higher sample rates provide better frequency resolution but use more CPU",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // FFT Size
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "FFT Size: ${localFftSize}",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Slider(
                        value = log2(localFftSize.toFloat()),
                        onValueChange = { value ->
                            val powerOf2 = (1 shl value.toInt()).coerceIn(256, 4096)
                            fftSizeInput = powerOf2.toString()
                            viewModel.updateLocalDetectorSettings(fftSize = powerOf2)
                        },
                        valueRange = 8f..12f, // 2^8=256 to 2^12=4096
                        steps = 4,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Text(
                        text = "Larger FFT sizes provide better frequency resolution but require more memory",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            // BPM Range
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "BPM Range: ${localMinBpm} - ${localMaxBpm} BPM",
                        style = MaterialTheme.typography.titleMedium
                    )
                    
                    Text(
                        text = "Min BPM: $localMinBpm",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Slider(
                        value = localMinBpm.toFloat(),
                        onValueChange = { value ->
                            val newValue = value.toInt().coerceIn(30, localMaxBpm - 10)
                            minBpmInput = newValue.toString()
                            viewModel.updateLocalDetectorSettings(minBpm = newValue)
                        },
                        valueRange = 30f..200f,
                        modifier = Modifier.fillMaxWidth()
                    )

                    Text(
                        text = "Max BPM: $localMaxBpm",
                        style = MaterialTheme.typography.bodyMedium,
                        modifier = Modifier.padding(top = 8.dp)
                    )
                    Slider(
                        value = localMaxBpm.toFloat(),
                        onValueChange = { value ->
                            val newValue = value.toInt().coerceIn(localMinBpm + 10, 300)
                            maxBpmInput = newValue.toString()
                            viewModel.updateLocalDetectorSettings(maxBpm = newValue)
                        },
                        valueRange = 60f..300f,
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            }

            // Recording Controls
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "Audio Recording",
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text(
                        text = "Record audio to file for later analysis",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    val context = LocalContext.current
                    
                    if (!isRecording) {
                        Button(
                            onClick = {
                                coroutineScope.launch {
                                    val file = java.io.File(
                                        context.getExternalFilesDir(null),
                                        "bpm_recording_${System.currentTimeMillis()}.pcm"
                                    )
                                    viewModel.startRecording(file)
                                }
                            },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Start Recording")
                        }
                    } else {
                        Button(
                            onClick = {
                                coroutineScope.launch {
                                    val file = viewModel.stopRecording()
                                    // Optionally analyze the file
                                    file?.let {
                                        viewModel.analyzeAudioFile(it)
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = MaterialTheme.colorScheme.error
                            ),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Stop Recording")
                        }
                    }
                }
            }
        }

        // App Info
        Card(
            modifier = Modifier.fillMaxWidth()
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Text(
                    text = "ESP32 BPM Detector",
                    style = MaterialTheme.typography.titleSmall
                )
                Text(
                    text = "Version 1.0.0",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Text(
                    text = "Real-time BPM detection from audio signals",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

