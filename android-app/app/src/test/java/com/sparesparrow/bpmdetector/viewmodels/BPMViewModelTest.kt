package com.sparesparrow.bpmdetector.viewmodels

import android.app.Application
import android.content.Context
import android.content.SharedPreferences
import android.net.ConnectivityManager
import android.net.wifi.WifiManager
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import com.sparesparrow.bpmdetector.models.BPMData
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.services.ConnectionStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.*
import org.junit.rules.TestWatcher
import org.junit.runner.Description
import org.junit.runner.RunWith
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import org.mockito.junit.MockitoJUnitRunner

@ExperimentalCoroutinesApi
@RunWith(MockitoJUnitRunner::class)
class BPMViewModelTest {

    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Mock
    private lateinit var mockApplication: Application

    @Mock
    private lateinit var mockSharedPreferences: SharedPreferences

    @Mock
    private lateinit var mockConnectivityManager: ConnectivityManager

    @Mock
    private lateinit var mockWifiManager: WifiManager

    @Mock
    private lateinit var mockBPMService: BPMService

    private lateinit var viewModel: BPMViewModel

    @Before
    fun setUp() {
        MockitoAnnotations.openMocks(this)

        // Setup Application mocks
        `when`(mockApplication.getSharedPreferences(anyString(), anyInt())).thenReturn(mockSharedPreferences)
        `when`(mockApplication.getSystemService(Context.CONNECTIVITY_SERVICE)).thenReturn(mockConnectivityManager)
        `when`(mockApplication.getSystemService(Context.WIFI_SERVICE)).thenReturn(mockWifiManager)

        // Setup WifiManager mock
        `when`(mockWifiManager.isWifiEnabled).thenReturn(true)

        viewModel = BPMViewModel(mockApplication)
    }

    @After
    fun tearDown() {
        viewModel.clearBPMService()
    }

    @Test
    fun `initial state should have loading BPM data`() {
        // Given - ViewModel is created

        // When - Check initial state
        val bpmData = viewModel.bpmDataFlow.value

        // Then - Should be loading state
        Assert.assertNotNull(bpmData)
        Assert.assertEquals("loading", bpmData?.status)
        Assert.assertEquals(0.0f, bpmData?.bpm ?: 0.0f)
    }

    @Test
    fun `setBPMService should observe service LiveData`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(true)
        `when`(mockBPMService.getServerIp()).thenReturn("192.168.1.100")

        // When
        viewModel.setBPMService(mockBPMService)

        // Then
        Assert.assertEquals(true, viewModel.isServiceRunning.value)
        Assert.assertEquals("192.168.1.100", viewModel.serverIp.value)

        // Verify observers were added
        verify(mockBPMService.bpmData).observeForever(any())
        verify(mockBPMService.connectionStatus).observeForever(any())
    }

    @Test
    fun `clearBPMService should remove observers and reset state`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(true)

        viewModel.setBPMService(mockBPMService)

        // When
        viewModel.clearBPMService()

        // Then
        Assert.assertEquals(false, viewModel.isServiceRunning.value)

        // Verify observers were removed
        verify(mockBPMService.bpmData).removeObserver(any())
        verify(mockBPMService.connectionStatus).removeObserver(any())
    }

    @Test
    fun `updateServerIp should update both ViewModel and service`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(false)
        `when`(mockBPMService.getServerIp()).thenReturn("192.168.1.100")

        viewModel.setBPMService(mockBPMService)

        // When
        viewModel.updateServerIp("192.168.1.200")

        // Then
        Assert.assertEquals("192.168.1.200", viewModel.serverIp.value)
        verify(mockBPMService).setServerIp("192.168.1.200")
    }

    @Test
    fun `updatePollingInterval should clamp values and update service`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(false)

        viewModel.setBPMService(mockBPMService)

        // When - Test clamping
        viewModel.updatePollingInterval(50L)  // Too low
        viewModel.updatePollingInterval(3000L) // Too high
        viewModel.updatePollingInterval(750L) // Valid

        // Then
        Assert.assertEquals(100L, viewModel.pollingInterval.value) // Clamped to min
        Assert.assertEquals(750L, viewModel.pollingInterval.value) // Valid value

        verify(mockBPMService).setPollingInterval(100L)
        verify(mockBPMService).setPollingInterval(750L)
    }

    @Test
    fun `getFormattedBpm should return formatted string or dash when null`() {
        // Given - Initial loading state

        // When
        val formatted = viewModel.getFormattedBpm()

        // Then
        Assert.assertEquals("--", formatted)
    }

    @Test
    fun `getConfidencePercentage should return percentage or zero when null`() {
        // Given - Initial loading state

        // When
        val confidence = viewModel.getConfidencePercentage()

        // Then
        Assert.assertEquals(0, confidence)
    }

    @Test
    fun `getStatusDescription should return disconnected when no data`() {
        // Given - Initial loading state

        // When
        val status = viewModel.getStatusDescription()

        // Then
        Assert.assertEquals("Disconnected", status)
    }

    @Test
    fun `getConnectionStatusDescription should handle all connection states`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(false)

        viewModel.setBPMService(mockBPMService)

        // When - Test CONNECTED
        mockConnectionStatus.value = ConnectionStatus.CONNECTED
        var status = viewModel.getConnectionStatusDescription()
        Assert.assertEquals("Connected", status)

        // When - Test CONNECTING
        mockConnectionStatus.value = ConnectionStatus.CONNECTING
        status = viewModel.getConnectionStatusDescription()
        Assert.assertEquals("Connecting...", status)

        // When - Test DISCONNECTED
        mockConnectionStatus.value = ConnectionStatus.DISCONNECTED
        status = viewModel.getConnectionStatusDescription()
        Assert.assertEquals("Disconnected", status)

        // When - Test ERROR
        mockConnectionStatus.value = ConnectionStatus.ERROR
        status = viewModel.getConnectionStatusDescription()
        Assert.assertEquals("Connection Error", status)
    }

    @Test
    fun `startMonitoring and stopMonitoring should call service methods`() {
        // Given
        val mockBPMData = MutableLiveData<BPMData>()
        val mockConnectionStatus = MutableLiveData<ConnectionStatus>()

        `when`(mockBPMService.bpmData).thenReturn(mockBPMData)
        `when`(mockBPMService.connectionStatus).thenReturn(mockConnectionStatus)
        `when`(mockBPMService.isPolling()).thenReturn(false)

        viewModel.setBPMService(mockBPMService)

        // When
        viewModel.startMonitoring()
        viewModel.stopMonitoring()

        // Then
        verify(mockBPMService).startPolling()
        verify(mockBPMService).stopPolling()
    }
}

// Test rule for coroutines
@ExperimentalCoroutinesApi
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
