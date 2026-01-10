package com.sparesparrow.bpmdetector.ui.screens

import android.Manifest
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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
import com.sparesparrow.bpmdetector.network.WiFiManager
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

    // WiFi state
    val isScanningWifi by viewModel.isScanningWifi.collectAsState()
    val wifiScanResults by viewModel.wifiScanResults.collectAsState()
    val isConnectingToWifi by viewModel.isConnectingToWifi.collectAsState()
    val esp32NetworkFound by viewModel.esp32NetworkFound.collectAsState()

    val coroutineScope = rememberCoroutineScope()

    // Audio permission state
    val audioPermissionState = rememberMultiplePermissionsState(
        permissions = listOf(Manifest.permission.RECORD_AUDIO)
    )

    // WiFi permission state
    val wifiPermissionState = rememberMultiplePermissionsState(
        permissions = listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )

    var ipInput by remember { mutableStateOf(serverIp) }
    var intervalInput by remember { mutableStateOf(pollingInterval.toString()) }
    var isTestingConnection by remember { mutableStateOf(false) }
    var connectionTestResult by remember { mutableStateOf<String?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
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
            placeholder = { Text("192.168.4.1") },
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

        // WiFi Network Management (ESP32 mode only)
        if (detectionMode == DetectionMode.ESP32) {
            Text(
                text = "ESP32 WiFi Network",
                style = MaterialTheme.typography.titleLarge
            )

            // WiFi Permissions
            if (!wifiPermissionState.allPermissionsGranted) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = Color(0xFFFFF3E0) // Light orange background
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = "Location Permissions Required",
                            style = MaterialTheme.typography.titleMedium,
                            color = Color(0xFFE65100)
                        )
                        Text(
                            text = "WiFi scanning requires location permissions to find and connect to the ESP32-BPM-DETECTOR network.",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Button(
                            onClick = { wifiPermissionState.launchMultiplePermissionRequest() },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Grant Location Permissions")
                        }
                    }
                }
            }

            // WiFi Status and Controls
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "WiFi Network Status",
                        style = MaterialTheme.typography.titleMedium
                    )

                    // Current WiFi connection
                    Text(
                        text = viewModel.getWifiConnectionInfo(),
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (viewModel.isConnectedToEsp32Wifi()) {
                            Color(0xFF4CAF50) // Green for ESP32 connection
                        } else {
                            MaterialTheme.colorScheme.onSurface
                        }
                    )

                    // WiFi state
                    Text(
                        text = viewModel.getWifiStateDescription(),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )

                    // ESP32 network status
                    if (esp32NetworkFound) {
                        Text(
                            text = "✓ ESP32-BPM-DETECTOR network found",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFF4CAF50)
                        )
                    } else if (!isScanningWifi) {
                        Text(
                            text = "ESP32 network not found",
                            style = MaterialTheme.typography.bodyMedium,
                            color = Color(0xFFF44336)
                        )
                    }

                    // WiFi control buttons
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Button(
                            onClick = {
                                if (wifiPermissionState.allPermissionsGranted) {
                                    coroutineScope.launch {
                                        viewModel.scanForEsp32Wifi()
                                    }
                                } else {
                                    wifiPermissionState.launchMultiplePermissionRequest()
                                }
                            },
                            enabled = !isScanningWifi && !isConnectingToWifi,
                            modifier = Modifier.weight(1f)
                        ) {
                            if (isScanningWifi) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(20.dp),
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Scanning...")
                            } else {
                                Text("Scan WiFi")
                            }
                        }

                        Button(
                            onClick = {
                                coroutineScope.launch {
                                    viewModel.connectToEsp32Wifi()
                                }
                            },
                            enabled = esp32NetworkFound && !isConnectingToWifi && !isScanningWifi,
                            modifier = Modifier.weight(1f)
                        ) {
                            if (isConnectingToWifi) {
                                CircularProgressIndicator(
                                    modifier = Modifier.size(20.dp),
                                    strokeWidth = 2.dp
                                )
                                Spacer(modifier = Modifier.width(8.dp))
                                Text("Connecting...")
                            } else {
                                Text("Connect")
                            }
                        }
                    }

                    // Debug Information
                    if (!viewModel.isWifiScanningSupported()) {
                        Text(
                            text = "⚠️ WiFi scanning not supported on this device",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color(0xFFF44336)
                        )
                    }

                    // Show debug info in a collapsible section
                    var showDebugInfo by remember { mutableStateOf(false) }
                    Button(
                        onClick = { showDebugInfo = !showDebugInfo },
                        modifier = Modifier.fillMaxWidth(),
                        colors = ButtonDefaults.buttonColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant
                        )
                    ) {
                        Text(
                            text = if (showDebugInfo) "Hide Debug Info" else "Show Debug Info",
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }

                    if (showDebugInfo) {
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(
                                containerColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        ) {
                            Text(
                                text = viewModel.getWifiDebugInfo(),
                                style = MaterialTheme.typography.bodySmall,
                                modifier = Modifier.padding(12.dp),
                                fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace
                            )
                        }
                    }
                }
            }

            // Auto-Discovery Button
            Button(
                onClick = {
                    coroutineScope.launch {
                        viewModel.autoDiscoverDevice()
                    }
                },
                enabled = wifiPermissionState.allPermissionsGranted && !isScanningWifi && !isConnectingToWifi,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("🔍 Auto-Discover ESP32 Device")
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
                        connectionStatus.isSearching() -> Color(0xFF2196F3) // Blue for searching
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

