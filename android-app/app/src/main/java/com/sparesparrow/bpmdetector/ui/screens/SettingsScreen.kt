package com.sparesparrow.bpmdetector.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.sparesparrow.bpmdetector.network.BPMApiClient
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import kotlinx.coroutines.launch

/**
 * Settings Screen - Configure ESP32 connection and monitoring parameters
 */
@Composable
fun SettingsScreen(viewModel: BPMViewModel) {
    val serverIp by viewModel.serverIp.collectAsState()
    val pollingInterval by viewModel.pollingInterval.collectAsState()
    val connectionStatus by viewModel.connectionStatus.collectAsState()

    val coroutineScope = rememberCoroutineScope()

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
            text = "ESP32 Connection Settings",
            style = MaterialTheme.typography.headlineMedium
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

        // Save Settings Button
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
