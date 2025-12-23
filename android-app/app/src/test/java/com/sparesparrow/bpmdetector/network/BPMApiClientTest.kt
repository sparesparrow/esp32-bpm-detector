package com.sparesparrow.bpmdetector.network

import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.models.BPMHealth
import com.sparesparrow.bpmdetector.models.BPMSettings
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.runTest
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.*
import org.junit.runner.RunWith
import org.mockito.junit.MockitoJUnitRunner
import java.net.SocketTimeoutException
import java.net.UnknownHostException

@ExperimentalCoroutinesApi
@RunWith(MockitoJUnitRunner::class)
class BPMApiClientTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiClient: BPMApiClient

    @Before
    fun setUp() {
        mockWebServer = MockWebServer()
        mockWebServer.start()
        val baseUrl = mockWebServer.url("/").toString()
        apiClient = BPMApiClient(baseUrl)
    }

    @After
    fun tearDown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `getBPMDataWithRetry should return success with valid response`() = runTest {
        // Given
        val bpmData = BPMData(
            bpm = 128.5f,
            confidence = 0.87f,
            signalLevel = 0.72f,
            status = "detecting",
            timestamp = 1671545123456L
        )
        val responseJson = """
            {
                "bpm": 128.5,
                "confidence": 0.87,
                "signal_level": 0.72,
                "status": "detecting",
                "timestamp": 1671545123456
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setBody(responseJson).setResponseCode(200))

        // When
        val result = apiClient.getBPMDataWithRetry()

        // Then
        Assert.assertTrue(result.isSuccess)
        val data = result.getOrNull()
        Assert.assertNotNull(data)
        Assert.assertEquals(128.5f, data?.bpm)
        Assert.assertEquals(0.87f, data?.confidence)
        Assert.assertEquals(0.72f, data?.signalLevel)
        Assert.assertEquals("detecting", data?.status)
    }

    @Test
    fun `getBPMDataWithRetry should handle HTTP error responses`() = runTest {
        // Given
        mockWebServer.enqueue(MockResponse().setResponseCode(500).setBody("Internal Server Error"))

        // When
        val result = apiClient.getBPMDataWithRetry()

        // Then
        Assert.assertTrue(result.isFailure)
        val exception = result.exceptionOrNull()
        Assert.assertTrue(exception is HttpException)
        Assert.assertTrue(exception?.message?.contains("HTTP 500") == true)
    }

    @Test
    fun `getBPMDataWithRetry should handle empty response body`() = runTest {
        // Given
        mockWebServer.enqueue(MockResponse().setResponseCode(200).setBody(""))

        // When
        val result = apiClient.getBPMDataWithRetry()

        // Then
        Assert.assertTrue(result.isFailure)
        val exception = result.exceptionOrNull()
        Assert.assertTrue(exception is java.io.IOException)
        Assert.assertEquals("Empty response body", exception?.message)
    }

    @Test
    fun `getBPMDataWithRetry should retry on network failures`() = runTest {
        // Given - First two calls fail, third succeeds
        mockWebServer.enqueue(MockResponse().setResponseCode(500))
        mockWebServer.enqueue(MockResponse().setSocketPolicy(okhttp3.mockwebserver.SocketPolicy.DISCONNECT_AT_START))
        mockWebServer.enqueue(MockResponse().setBody("""{"bpm": 120.0, "confidence": 0.8, "signal_level": 0.6, "status": "detecting", "timestamp": 1234567890}""").setResponseCode(200))

        // When
        val result = apiClient.getBPMDataWithRetry(retryAttempts = 3)

        // Then
        Assert.assertTrue(result.isSuccess)
        val data = result.getOrNull()
        Assert.assertEquals(120.0f, data?.bpm)
    }

    @Test
    fun `getSettings should return success with valid response`() = runTest {
        // Given
        val settingsJson = """
            {
                "min_bpm": 60,
                "max_bpm": 200,
                "sample_rate": 25000,
                "fft_size": 1024,
                "version": "1.0.0"
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setBody(settingsJson).setResponseCode(200))

        // When
        val result = apiClient.getSettings()

        // Then
        Assert.assertTrue(result.isSuccess)
        val settings = result.getOrNull()
        Assert.assertNotNull(settings)
        Assert.assertEquals(60, settings?.minBpm)
        Assert.assertEquals(200, settings?.maxBpm)
        Assert.assertEquals(25000, settings?.sampleRate)
        Assert.assertEquals(1024, settings?.fftSize)
        Assert.assertEquals("1.0.0", settings?.version)
    }

    @Test
    fun `getHealth should return success with valid response`() = runTest {
        // Given
        val healthJson = """
            {
                "status": "ok",
                "uptime": 3600,
                "heap_free": 245760
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setBody(healthJson).setResponseCode(200))

        // When
        val result = apiClient.getHealth()

        // Then
        Assert.assertTrue(result.isSuccess)
        val health = result.getOrNull()
        Assert.assertNotNull(health)
        Assert.assertEquals("ok", health?.status)
        Assert.assertEquals(3600L, health?.uptime)
        Assert.assertEquals(245760, health?.heapFree)
    }

    @Test
    fun `isServerReachable should return true for healthy server`() = runTest {
        // Given
        val healthJson = """
            {
                "status": "ok",
                "uptime": 3600,
                "heap_free": 245760
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setBody(healthJson).setResponseCode(200))

        // When
        val isReachable = apiClient.isServerReachable()

        // Then
        Assert.assertTrue(isReachable)
    }

    @Test
    fun `isServerReachable should return false for unhealthy server`() = runTest {
        // Given
        val healthJson = """
            {
                "status": "error",
                "uptime": 0,
                "heap_free": 0
            }
        """.trimIndent()

        mockWebServer.enqueue(MockResponse().setBody(healthJson).setResponseCode(200))

        // When
        val isReachable = apiClient.isServerReachable()

        // Then
        Assert.assertFalse(isReachable)
    }

    @Test
    fun `isServerReachable should return false on network errors`() = runTest {
        // Given - Server is down
        mockWebServer.shutdown()

        // When
        val isReachable = apiClient.isServerReachable()

        // Then
        Assert.assertFalse(isReachable)
    }

    @Test
    fun `getConnectionInfo should return formatted connection string`() {
        // Given
        val expectedBaseUrl = mockWebServer.url("/").toString()

        // When
        val connectionInfo = apiClient.getConnectionInfo()

        // Then
        Assert.assertEquals("Connected to: $expectedBaseUrl", connectionInfo)
    }

    @Test
    fun `companion object createDefault should create client with default IP`() {
        // When
        val client = BPMApiClient.createDefault()

        // Then
        val connectionInfo = client.getConnectionInfo()
        Assert.assertEquals("Connected to: http://192.168.1.100", connectionInfo)
    }

    @Test
    fun `companion object createWithIp should create client with custom IP`() {
        // When
        val client = BPMApiClient.createWithIp("192.168.0.100")

        // Then
        val connectionInfo = client.getConnectionInfo()
        Assert.assertEquals("Connected to: http://192.168.0.100", connectionInfo)
    }

    @Test
    fun `companion object isValidIpAddress should validate IP formats correctly`() {
        // Given - Valid IPs
        val validIps = listOf(
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "255.255.255.255",
            "0.0.0.0"
        )

        // Given - Invalid IPs
        val invalidIps = listOf(
            "256.1.1.1",
            "192.168.1.256",
            "192.168.1",
            "192.168.1.1.1",
            "abc.def.ghi.jkl",
            "",
            "192.168.1.1/"
        )

        // When & Then - Valid IPs
        validIps.forEach { ip ->
            Assert.assertTrue("IP $ip should be valid", BPMApiClient.isValidIpAddress(ip))
        }

        // When & Then - Invalid IPs
        invalidIps.forEach { ip ->
            Assert.assertFalse("IP $ip should be invalid", BPMApiClient.isValidIpAddress(ip))
        }
    }

    @Test
    fun `getBPMDataWithRetry should handle malformed JSON gracefully`() = runTest {
        // Given
        val malformedJson = "{invalid json"
        mockWebServer.enqueue(MockResponse().setBody(malformedJson).setResponseCode(200))

        // When
        val result = apiClient.getBPMDataWithRetry()

        // Then
        Assert.assertTrue(result.isFailure)
    }
}
