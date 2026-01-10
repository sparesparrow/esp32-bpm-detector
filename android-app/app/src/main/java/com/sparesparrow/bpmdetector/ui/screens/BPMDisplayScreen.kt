package com.sparesparrow.bpmdetector.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.sparesparrow.bpmdetector.services.ConnectionStatus
import com.sparesparrow.bpmdetector.ui.components.FrequencySpectrumVisualization
import com.sparesparrow.bpmdetector.ui.components.VisualizationStyle
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import com.sparesparrow.bpmdetector.viewmodels.DetectionMode
import com.sparesparrow.bpmdetector.models.BPMData
import kotlinx.coroutines.delay

/**
 * UI State for BPM Display Screen
 */
private data class BPMDisplayUiState(
    val bpmData: BPMData?,
    val connectionStatus: ConnectionStatus,
    val isServiceRunning: Boolean,
    val detectionMode: DetectionMode,
    val frequencySpectrum: FloatArray?,
    val localSampleRate: Int,
    val localFftSize: Int
)

/**
 * Pre-computed display values to avoid recomputation
 */
private data class DisplayValues(
    val bpm: String,
    val confidence: Int,
    val signalLevel: Int,
    val status: String,
    val isDetecting: Boolean,
    val hasLowSignal: Boolean,
    val hasError: Boolean
)

/**
 * BPM Display Screen - Main screen showing live BPM data
 */
@Composable
fun BPMDisplayScreen(viewModel: BPMViewModel) {
    // Collect all state flows efficiently
    val uiState by remember {
        derivedStateOf {
            BPMDisplayUiState(
                bpmData = viewModel.bpmDataFlow.value,
                connectionStatus = viewModel.connectionStatus.value,
                isServiceRunning = viewModel.isServiceRunning.value,
                detectionMode = viewModel.detectionMode.value,
                frequencySpectrum = viewModel.frequencySpectrum.value,
                localSampleRate = viewModel.localSampleRate.value,
                localFftSize = viewModel.localFftSize.value
            )
        }
    }

    // Auto-start monitoring when screen is displayed
    LaunchedEffect(uiState.isServiceRunning) {
        if (!uiState.isServiceRunning) {
            viewModel.startMonitoring()
        }
    }

    // Pre-compute display values to avoid recomputation
    val displayValues by remember(uiState.bpmData) {
        derivedStateOf {
            uiState.bpmData?.let { data ->
                DisplayValues(
                    bpm = viewModel.getFormattedBpm(),
                    confidence = viewModel.getConfidencePercentage(),
                    signalLevel = viewModel.getSignalLevelPercentage(),
                    status = viewModel.getStatusDescription(),
                    isDetecting = viewModel.isDetecting(),
                    hasLowSignal = viewModel.hasLowSignal(),
                    hasError = viewModel.hasError()
                )
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        // Connection Status
        ConnectionStatusIndicator(
            connectionStatus = uiState.connectionStatus,
            modifier = Modifier.fillMaxWidth()
        )

        // Detection Mode Indicator
        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.small,
            color = when (uiState.detectionMode) {
                DetectionMode.ESP32 -> MaterialTheme.colorScheme.primaryContainer
                DetectionMode.LOCAL -> MaterialTheme.colorScheme.secondaryContainer
            }
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = when (uiState.detectionMode) {
                        DetectionMode.ESP32 -> "📡 ESP32 Device"
                        DetectionMode.LOCAL -> "🎤 Phone Microphone"
                    },
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        // BPM Display
        displayValues?.let { values ->
            BPMDisplay(
                bpm = values.bpm,
                confidence = values.confidence,
                signalLevel = values.signalLevel,
                status = values.status,
                isDetecting = values.isDetecting,
                hasLowSignal = values.hasLowSignal,
                hasError = values.hasError,
                modifier = Modifier.weight(1f)
            )
        } ?: run {
            // Loading state
            CircularProgressIndicator(
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }

        // Frequency Spectrum Visualization (only for local mode)
        if (uiState.detectionMode == DetectionMode.LOCAL && uiState.frequencySpectrum != null) {
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Frequency Spectrum",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(horizontal = 8.dp)
                    )
                    FrequencySpectrumVisualization(
                        spectrum = uiState.frequencySpectrum,
                        sampleRate = uiState.localSampleRate,
                        fftSize = uiState.localFftSize,
                        style = VisualizationStyle.BARS
                    )
                }
            }
        }

        // Control Buttons
        BPMControlButtons(
            isServiceRunning = uiState.isServiceRunning,
            onStartStopClick = {
                if (uiState.isServiceRunning) {
                    viewModel.stopMonitoring()
                } else {
                    viewModel.startMonitoring()
                }
            },
            modifier = Modifier.fillMaxWidth()
        )
    }
}

/**
 * Connection status indicator
 */
@Composable
fun ConnectionStatusIndicator(
    connectionStatus: ConnectionStatus,
    modifier: Modifier = Modifier
) {
    val (backgroundColor, textColor, statusText) = when {
        connectionStatus.isConnected() -> Triple(
            Color(0xFF4CAF50), // Green
            Color.White,
            "Connected"
        )
        connectionStatus.isConnecting() -> Triple(
            Color(0xFFFF9800), // Orange
            Color.White,
            "Connecting..."
        )
        connectionStatus.hasError() -> Triple(
            Color(0xFFF44336), // Red
            Color.White,
            "Connection Error"
        )
        else -> Triple(
            Color(0xFF9E9E9E), // Gray
            Color.White,
            "Disconnected"
        )
    }

    Surface(
        color = backgroundColor,
        shape = MaterialTheme.shapes.medium,
        modifier = modifier
    ) {
        Text(
            text = statusText,
            color = textColor,
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(12.dp)
        )
    }
}

/**
 * Main BPM display component
 */
@Composable
fun BPMDisplay(
    bpm: String,
    confidence: Int,
    signalLevel: Int,
    status: String,
    isDetecting: Boolean,
    hasLowSignal: Boolean,
    hasError: Boolean,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier,
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // BPM Value
        Text(
            text = bpm,
            style = MaterialTheme.typography.displayLarge.copy(
                fontWeight = FontWeight.Bold,
                fontSize = 72.sp
            ),
            color = when {
                hasError -> Color(0xFFF44336) // Red
                hasLowSignal -> Color(0xFFFF9800) // Orange
                isDetecting -> Color(0xFF4CAF50) // Green
                else -> MaterialTheme.colorScheme.onSurface
            },
            textAlign = TextAlign.Center
        )

        // Status Text
        Text(
            text = status,
            style = MaterialTheme.typography.headlineSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            textAlign = TextAlign.Center
        )

        // Progress Indicators
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterHorizontally)
        ) {
            // Confidence Indicator
            CircularProgressIndicator(
                progress = confidence / 100f,
                label = "Confidence",
                value = confidence,
                color = when {
                    confidence > 80 -> Color(0xFF4CAF50)
                    confidence > 60 -> Color(0xFFFF9800)
                    else -> Color(0xFFF44336)
                }
            )

            // Signal Level Indicator
            CircularProgressIndicator(
                progress = signalLevel / 100f,
                label = "Signal",
                value = signalLevel,
                color = when {
                    signalLevel > 70 -> Color(0xFF4CAF50)
                    signalLevel > 40 -> Color(0xFFFF9800)
                    else -> Color(0xFFF44336)
                }
            )
        }
    }
}

/**
 * Circular progress indicator with label and value
 */
@Composable
fun CircularProgressIndicator(
    progress: Float,
    label: String,
    value: Int,
    color: Color,
    modifier: Modifier = Modifier
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(4.dp),
        modifier = modifier
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier.size(80.dp)
        ) {
            // Background circle
            androidx.compose.foundation.Canvas(
                modifier = Modifier.size(80.dp)
            ) {
                drawCircle(
                    color = color.copy(alpha = 0.2f),
                    style = androidx.compose.ui.graphics.drawscope.Stroke(width = 8f)
                )
            }

            // Progress arc
            androidx.compose.foundation.Canvas(
                modifier = Modifier.size(80.dp)
            ) {
                drawArc(
                    color = color,
                    startAngle = -90f,
                    sweepAngle = progress * 360f,
                    useCenter = false,
                    style = androidx.compose.ui.graphics.drawscope.Stroke(width = 8f)
                )
            }

            // Value text
            Text(
                text = "$value%",
                style = MaterialTheme.typography.bodyMedium.copy(
                    fontWeight = FontWeight.Bold
                ),
                color = color
            )
        }

        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Control buttons for starting/stopping monitoring
 */
@Composable
fun BPMControlButtons(
    isServiceRunning: Boolean,
    onStartStopClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onStartStopClick,
        colors = ButtonDefaults.buttonColors(
            containerColor = if (isServiceRunning) Color(0xFFF44336) else Color(0xFF4CAF50)
        ),
        modifier = modifier
    ) {
        Text(
            text = if (isServiceRunning) "Stop Monitoring" else "Start Monitoring",
            style = MaterialTheme.typography.titleMedium
        )
    }
}

