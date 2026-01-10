package com.sparesparrow.bpmdetector.network

import android.Manifest
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.net.wifi.ScanResult
import android.net.wifi.WifiConfiguration
import android.net.wifi.WifiManager
import android.os.Build
import androidx.core.content.ContextCompat
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import timber.log.Timber

/**
 * WiFi Manager for ESP32 BPM Detector network operations
 */
class WiFiManager(private val context: Context) {

    private val wifiManager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager

    companion object {
        const val ESP32_SSID = "ESP32-BPM-Detector"  // Match ESP32 firmware exactly
        const val ESP32_DEFAULT_PASSWORD = "bpm12345"  // Match ESP32 firmware password
    }

    /**
     * Check if location permissions are granted (required for WiFi scanning)
     */
    fun hasLocationPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }

    /**
     * Check if WiFi is enabled
     */
    fun isWifiEnabled(): Boolean = wifiManager.isWifiEnabled

    /**
     * Enable WiFi if not already enabled
     */
    fun enableWifi(): Boolean {
        return if (!wifiManager.isWifiEnabled) {
            wifiManager.isWifiEnabled = true
            wifiManager.isWifiEnabled
        } else {
            true
        }
    }

    /**
     * Scan for available WiFi networks
     */
    fun scanWifiNetworks(): Flow<List<ScanResult>> = callbackFlow {
        Timber.d("Starting WiFi scan - checking permissions and WiFi state")

        // Check location permissions
        if (!hasLocationPermissions()) {
            Timber.w("Location permissions not granted for WiFi scanning")
            Timber.d("ACCESS_FINE_LOCATION: ${ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION)}")
            Timber.d("ACCESS_COARSE_LOCATION: ${ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION)}")
            trySend(emptyList())
            close()
            return@callbackFlow
        }

        Timber.d("Location permissions granted")

        // Enable WiFi if needed
        if (!enableWifi()) {
            Timber.w("Failed to enable WiFi")
            trySend(emptyList())
            close()
            return@callbackFlow
        }

        Timber.d("WiFi enabled, starting scan")

        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                Timber.d("WiFi scan broadcast received: ${intent?.action}")
                if (intent?.action == WifiManager.SCAN_RESULTS_AVAILABLE_ACTION) {
                    val results = wifiManager.scanResults
                    Timber.d("WiFi scan completed. Found ${results.size} networks")
                    results.forEach { result ->
                        Timber.d("Found network: ${result.SSID} (BSSID: ${result.BSSID})")
                    }
                    trySend(results)
                    close()
                }
            }
        }

        val filter = IntentFilter(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION)
        context.registerReceiver(receiver, filter)

        // Start scan
        Timber.d("Initiating WiFi scan...")
        val scanStarted = wifiManager.startScan()
        Timber.d("WiFi scan initiated: $scanStarted")

        if (!scanStarted) {
            Timber.w("WiFi scan failed to start")
            trySend(emptyList())
            context.unregisterReceiver(receiver)
            close()
        }

        awaitClose {
            try {
                context.unregisterReceiver(receiver)
            } catch (e: Exception) {
                Timber.w(e, "Error unregistering receiver")
            }
        }
    }

    /**
     * Check if ESP32-BPM-DETECTOR network is available
     */
    fun isEsp32NetworkAvailable(scanResults: List<ScanResult>): Boolean {
        return scanResults.any { it.SSID == ESP32_SSID }
    }

    /**
     * Get ESP32 network from scan results
     */
    fun getEsp32Network(scanResults: List<ScanResult>): ScanResult? {
        return scanResults.find { it.SSID == ESP32_SSID }
    }

    /**
     * Connect to ESP32-BPM-DETECTOR network
     */
    fun connectToEsp32Network(): Boolean {
        if (!isWifiEnabled()) {
            Timber.w("WiFi is not enabled")
            return false
        }

        // Configure WiFi with password (WPA_PSK)
        val wifiConfig = WifiConfiguration().apply {
            SSID = "\"$ESP32_SSID\""
            preSharedKey = "\"$ESP32_DEFAULT_PASSWORD\""
            allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK)
            allowedAuthAlgorithms.set(WifiConfiguration.AuthAlgorithm.OPEN)
            allowedProtocols.set(WifiConfiguration.Protocol.WPA)
        }

        val networkId = wifiManager.addNetwork(wifiConfig)
        if (networkId == -1) {
            Timber.e("Failed to add ESP32 network configuration")
            return false
        }

        val disconnectResult = wifiManager.disconnect()
        val enableResult = wifiManager.enableNetwork(networkId, true)
        val reconnectResult = wifiManager.reconnect()

        Timber.d("WiFi connection attempt - disconnect: $disconnectResult, enable: $enableResult, reconnect: $reconnectResult")

        return enableResult && reconnectResult
    }

    /**
     * Get current connection info
     */
    fun getCurrentConnectionInfo(): String {
        val info = wifiManager.connectionInfo
        return if (info?.ssid != null && info.ssid != "<unknown ssid>") {
            "Connected to: ${info.ssid.replace("\"", "")}"
        } else {
            "Not connected to any network"
        }
    }

    /**
     * Check if currently connected to ESP32 network
     */
    fun isConnectedToEsp32(): Boolean {
        val info = wifiManager.connectionInfo
        return info?.ssid?.replace("\"", "") == ESP32_SSID
    }

    /**
     * Get WiFi state description
     */
    fun getWifiStateDescription(): String {
        return when (wifiManager.wifiState) {
            WifiManager.WIFI_STATE_ENABLED -> "WiFi Enabled"
            WifiManager.WIFI_STATE_ENABLING -> "Enabling WiFi..."
            WifiManager.WIFI_STATE_DISABLED -> "WiFi Disabled"
            WifiManager.WIFI_STATE_DISABLING -> "Disabling WiFi..."
            WifiManager.WIFI_STATE_UNKNOWN -> "WiFi State Unknown"
            else -> "WiFi State Unknown"
        }
    }

    /**
     * Check if WiFi scanning is supported on this device
     */
    fun isWifiScanningSupported(): Boolean {
        return context.packageManager.hasSystemFeature("android.hardware.wifi")
    }

    /**
     * Get detailed WiFi information for debugging
     */
    fun getWifiDebugInfo(): String {
        val sb = StringBuilder()
        sb.append("WiFi Enabled: ${isWifiEnabled()}\n")
        sb.append("Scanning Supported: ${isWifiScanningSupported()}\n")
        sb.append("Location Permissions: ${hasLocationPermissions()}\n")
        sb.append("Current Connection: ${getCurrentConnectionInfo()}\n")
        sb.append("WiFi State: ${getWifiStateDescription()}\n")
        sb.append("Last Scan Results: ${getLastScanResults()}\n")
        return sb.toString()
    }

    /**
     * Get formatted list of last scan results
     */
    private fun getLastScanResults(): String {
        val results = wifiManager.scanResults
        if (results.isEmpty()) {
            return "No networks found"
        }

        return results.take(10).joinToString("\n") { result ->
            "• ${result.SSID} (${result.level}dBm)"
        }
    }
}