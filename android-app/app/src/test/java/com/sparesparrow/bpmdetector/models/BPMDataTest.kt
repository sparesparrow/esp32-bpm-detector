package com.sparesparrow.bpmdetector.models

import org.junit.*
import org.junit.runner.RunWith
import org.mockito.junit.MockitoJUnitRunner

@RunWith(MockitoJUnitRunner::class)
class BPMDataTest {

    @Test
    fun `isDetecting should return true for detecting status`() {
        // Given
        val bpmData = BPMData(status = "detecting")

        // When & Then
        Assert.assertTrue(bpmData.isDetecting())
    }

    @Test
    fun `isDetecting should return false for non-detecting status`() {
        // Given
        val statuses = listOf("low_signal", "error", "initializing", "buffering", "unknown")

        statuses.forEach { status ->
            val bpmData = BPMData(status = status)

            // When & Then
            Assert.assertFalse("Status '$status' should not be detecting", bpmData.isDetecting())
        }
    }

    @Test
    fun `hasLowSignal should return true for low_signal status`() {
        // Given
        val bpmData = BPMData(status = "low_signal")

        // When & Then
        Assert.assertTrue(bpmData.hasLowSignal())
    }

    @Test
    fun `hasLowSignal should return false for non-low-signal status`() {
        // Given
        val statuses = listOf("detecting", "error", "initializing", "buffering", "unknown")

        statuses.forEach { status ->
            val bpmData = BPMData(status = status)

            // When & Then
            Assert.assertFalse("Status '$status' should not be low signal", bpmData.hasLowSignal())
        }
    }

    @Test
    fun `hasError should return true for error status`() {
        // Given
        val bpmData = BPMData(status = "error")

        // When & Then
        Assert.assertTrue(bpmData.hasError())
    }

    @Test
    fun `hasError should return false for non-error status`() {
        // Given
        val statuses = listOf("detecting", "low_signal", "initializing", "buffering", "unknown")

        statuses.forEach { status ->
            val bpmData = BPMData(status = status)

            // When & Then
            Assert.assertFalse("Status '$status' should not be error", bpmData.hasError())
        }
    }

    @Test
    fun `getConfidencePercentage should convert confidence to percentage correctly`() {
        // Given
        val testCases = listOf(
            0.0f to 0,
            0.5f to 50,
            1.0f to 100,
            0.123f to 12,
            0.987f to 98
        )

        testCases.forEach { (confidence, expected) ->
            val bpmData = BPMData(confidence = confidence)

            // When
            val percentage = bpmData.getConfidencePercentage()

            // Then
            Assert.assertEquals("Confidence $confidence should be $expected%", expected, percentage)
        }
    }

    @Test
    fun `getSignalLevelPercentage should convert signal level to percentage correctly`() {
        // Given
        val testCases = listOf(
            0.0f to 0,
            0.5f to 50,
            1.0f to 100,
            0.234f to 23,
            0.789f to 78
        )

        testCases.forEach { (signalLevel, expected) ->
            val bpmData = BPMData(signalLevel = signalLevel)

            // When
            val percentage = bpmData.getSignalLevelPercentage()

            // Then
            Assert.assertEquals("Signal level $signalLevel should be $expected%", expected, percentage)
        }
    }

    @Test
    fun `getFormattedBpm should return formatted string for positive BPM`() {
        // Given
        val testCases = listOf(
            120.0f to "120.0",
            128.5f to "128.5",
            99.9f to "99.9",
            200.0f to "200.0"
        )

        testCases.forEach { (bpm, expected) ->
            val bpmData = BPMData(bpm = bpm)

            // When
            val formatted = bpmData.getFormattedBpm()

            // Then
            Assert.assertEquals("BPM $bpm should format to $expected", expected, formatted)
        }
    }

    @Test
    fun `getFormattedBpm should return dash for zero or negative BPM`() {
        // Given
        val testCases = listOf(0.0f, -1.0f, -50.0f)

        testCases.forEach { bpm ->
            val bpmData = BPMData(bpm = bpm)

            // When
            val formatted = bpmData.getFormattedBpm()

            // Then
            Assert.assertEquals("BPM $bpm should format to '--'", "--", formatted)
        }
    }

    @Test
    fun `getStatusDescription should return correct descriptions for all statuses`() {
        // Given
        val testCases = mapOf(
            "detecting" to "Detecting BPM",
            "low_signal" to "Low Audio Signal",
            "low_confidence" to "Analyzing...",
            "error" to "Connection Error",
            "initializing" to "Initializing...",
            "buffering" to "Buffering...",
            "unknown" to "Unknown Status",
            "random_status" to "Unknown Status"
        )

        testCases.forEach { (status, expected) ->
            val bpmData = BPMData(status = status)

            // When
            val description = bpmData.getStatusDescription()

            // Then
            Assert.assertEquals("Status '$status' should describe as '$expected'", expected, description)
        }
    }

    @Test
    fun `createError should create BPM data with error status`() {
        // When
        val errorData = BPMData.createError()

        // Then
        Assert.assertEquals(0.0f, errorData.bpm)
        Assert.assertEquals(0.0f, errorData.confidence)
        Assert.assertEquals(0.0f, errorData.signalLevel)
        Assert.assertEquals("error", errorData.status)
        Assert.assertTrue(errorData.timestamp > 0L)
    }

    @Test
    fun `createLoading should create BPM data with connecting status`() {
        // When
        val loadingData = BPMData.createLoading()

        // Then
        Assert.assertEquals(0.0f, loadingData.bpm)
        Assert.assertEquals(0.0f, loadingData.confidence)
        Assert.assertEquals(0.0f, loadingData.signalLevel)
        Assert.assertEquals("connecting", loadingData.status)
        Assert.assertTrue(loadingData.timestamp > 0L)
    }
}
