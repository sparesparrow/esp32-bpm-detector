package com.sparesparrow.bpmdetector.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

enum class VisualizationStyle {
    BARS,
    LINE,
    FILLED
}

@Composable
fun FrequencySpectrumVisualization(
    spectrum: FloatArray?,
    sampleRate: Int,
    fftSize: Int,
    style: VisualizationStyle = VisualizationStyle.BARS,
    modifier: Modifier = Modifier
        .fillMaxWidth()
        .height(120.dp)
) {
    val data = spectrum ?: return
    val barColor = Color(0xFF4CAF50)

    Canvas(modifier = modifier) {
        if (data.isEmpty()) return@Canvas

        val maxVal = data.max().coerceAtLeast(0.001f)
        val binCount = data.size
        val canvasWidth = size.width
        val canvasHeight = size.height

        when (style) {
            VisualizationStyle.BARS -> {
                val barWidth = canvasWidth / binCount
                data.forEachIndexed { i, value ->
                    val normalised = (value / maxVal).coerceIn(0f, 1f)
                    val barHeight = normalised * canvasHeight
                    drawRect(
                        color = barColor,
                        topLeft = Offset(i * barWidth, canvasHeight - barHeight),
                        size = Size(barWidth * 0.8f, barHeight)
                    )
                }
            }
            VisualizationStyle.LINE, VisualizationStyle.FILLED -> {
                val points = data.mapIndexed { i, value ->
                    val normalised = (value / maxVal).coerceIn(0f, 1f)
                    Offset(
                        x = i * canvasWidth / binCount,
                        y = canvasHeight - normalised * canvasHeight
                    )
                }
                for (i in 0 until points.size - 1) {
                    drawLine(
                        color = barColor,
                        start = points[i],
                        end = points[i + 1],
                        strokeWidth = 2f
                    )
                }
            }
        }
    }
}
