package com.sparesparrow.bpmdetector.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
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
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import kotlinx.coroutines.delay

/**
 * BPM Display Screen - Main screen showing live BPM data
 */
@Composable
fun BPMDisplayScreen(viewModel: BPMViewModel) {
    val bpmData by viewModel.bpmData.observeAsState()
    val connectionStatus by viewModel.connectionStatus.collectAsState()
    val isServiceRunning by viewModel.isServiceRunning.collectAsState()

    // Auto-start monitoring when screen is displayed
    LaunchedEffect(Unit) {
        if (!isServiceRunning) {
            delay(500) // Small delay to ensure service is bound
            viewModel.startMonitoring()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        // Connection Status
        ConnectionStatusIndicator(
            connectionStatus = connectionStatus,
            modifier = Modifier.fillMaxWidth()
        )

        // BPM Display
        BPMDisplay(
            bpm = viewModel.getFormattedBpm(),
            confidence = viewModel.getConfidencePercentage(),
            signalLevel = viewModel.getSignalLevelPercentage(),
            status = viewModel.getStatusDescription(),
            isDetecting = viewModel.isDetecting(),
            hasLowSignal = viewModel.hasLowSignal(),
            hasError = viewModel.hasError(),
            modifier = Modifier.weight(1f)
        )

        // Control Buttons
        BPMControlButtons(
            isServiceRunning = isServiceRunning,
            onStartStopClick = {
                if (isServiceRunning) {
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
            connectionStatus.errorMessage ?: "Connection Error"
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

