package com.sparesparrow.bpmdetector.ui.screens

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.Build
import android.os.Environment
import android.os.StatFs
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import java.io.File
import java.text.DecimalFormat

/**
 * Device Info Screen - Display comprehensive Android device information
 */
@Composable
fun DeviceInfoScreen() {
    val context = LocalContext.current
    val scrollState = rememberScrollState()

    val deviceInfo by remember { mutableStateOf(getDeviceInfo(context)) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Device Information",
            style = MaterialTheme.typography.headlineMedium
        )

        // Hardware Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Hardware",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Model", deviceInfo.model)
                DeviceInfoRow("Manufacturer", deviceInfo.manufacturer)
                DeviceInfoRow("Brand", deviceInfo.brand)
                DeviceInfoRow("Device", deviceInfo.device)
                DeviceInfoRow("Product", deviceInfo.product)
                DeviceInfoRow("Hardware", deviceInfo.hardware)
                DeviceInfoRow("Board", deviceInfo.board)
                DeviceInfoRow("Serial", deviceInfo.serial)
            }
        }

        // Software Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Software",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Android Version", deviceInfo.androidVersion)
                DeviceInfoRow("API Level", deviceInfo.apiLevel.toString())
                DeviceInfoRow("Build ID", deviceInfo.buildId)
                DeviceInfoRow("Build Type", deviceInfo.buildType)
                DeviceInfoRow("Security Patch", deviceInfo.securityPatch)
                DeviceInfoRow("Bootloader", deviceInfo.bootloader)
                DeviceInfoRow("Fingerprint", deviceInfo.fingerprint)
            }
        }

        // Display Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Display",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Screen Resolution", "${deviceInfo.screenWidth}x${deviceInfo.screenHeight}")
                DeviceInfoRow("Screen Density", "${deviceInfo.screenDensity} dpi")
                DeviceInfoRow("Refresh Rate", "${deviceInfo.refreshRate} Hz")
                DeviceInfoRow("Orientation", deviceInfo.orientation)
            }
        }

        // Storage Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Storage",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Internal Total", deviceInfo.internalTotalSpace)
                DeviceInfoRow("Internal Available", deviceInfo.internalAvailableSpace)
                DeviceInfoRow("Internal Used", deviceInfo.internalUsedSpace)

                if (deviceInfo.externalTotalSpace.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(8.dp))
                    DeviceInfoRow("External Total", deviceInfo.externalTotalSpace)
                    DeviceInfoRow("External Available", deviceInfo.externalAvailableSpace)
                    DeviceInfoRow("External Used", deviceInfo.externalUsedSpace)
                }
            }
        }

        // Memory Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Memory",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Total RAM", deviceInfo.totalRam)
                DeviceInfoRow("Available RAM", deviceInfo.availableRam)
            }
        }

        // Battery Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Battery",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Level", deviceInfo.batteryLevel)
                DeviceInfoRow("Status", deviceInfo.batteryStatus)
                DeviceInfoRow("Health", deviceInfo.batteryHealth)
                DeviceInfoRow("Technology", deviceInfo.batteryTechnology)
                DeviceInfoRow("Temperature", deviceInfo.batteryTemperature)
                DeviceInfoRow("Voltage", deviceInfo.batteryVoltage)
            }
        }

        // Network Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Network",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("Network Type", deviceInfo.networkType)
                DeviceInfoRow("WiFi Connected", deviceInfo.wifiConnected)
                DeviceInfoRow("Mobile Data", deviceInfo.mobileDataEnabled)
            }
        }

        // App Information
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "App Information",
                    style = MaterialTheme.typography.titleLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(8.dp))

                DeviceInfoRow("App Version", deviceInfo.appVersion)
                DeviceInfoRow("Package Name", deviceInfo.packageName)
                DeviceInfoRow("Target SDK", deviceInfo.targetSdk.toString())
                DeviceInfoRow("Min SDK", deviceInfo.minSdk.toString())
            }
        }
    }
}

@Composable
private fun DeviceInfoRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = "$label:",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.weight(1f)
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface,
            modifier = Modifier.weight(1f)
        )
    }
}

private data class DeviceInfo(
    val model: String,
    val manufacturer: String,
    val brand: String,
    val device: String,
    val product: String,
    val hardware: String,
    val board: String,
    val serial: String,
    val androidVersion: String,
    val apiLevel: Int,
    val buildId: String,
    val buildType: String,
    val securityPatch: String,
    val bootloader: String,
    val fingerprint: String,
    val screenWidth: Int,
    val screenHeight: Int,
    val screenDensity: Int,
    val refreshRate: Float,
    val orientation: String,
    val internalTotalSpace: String,
    val internalAvailableSpace: String,
    val internalUsedSpace: String,
    val externalTotalSpace: String,
    val externalAvailableSpace: String,
    val externalUsedSpace: String,
    val totalRam: String,
    val availableRam: String,
    val batteryLevel: String,
    val batteryStatus: String,
    val batteryHealth: String,
    val batteryTechnology: String,
    val batteryTemperature: String,
    val batteryVoltage: String,
    val networkType: String,
    val wifiConnected: String,
    val mobileDataEnabled: String,
    val appVersion: String,
    val packageName: String,
    val targetSdk: Int,
    val minSdk: Int
)

private fun getDeviceInfo(context: Context): DeviceInfo {
    val packageManager = context.packageManager
    val packageName = context.packageName
    val configuration = context.resources.configuration

    return DeviceInfo(
        // Hardware
        model = Build.MODEL,
        manufacturer = Build.MANUFACTURER,
        brand = Build.BRAND,
        device = Build.DEVICE,
        product = Build.PRODUCT,
        hardware = Build.HARDWARE,
        board = Build.BOARD,
        serial = try { Build.SERIAL } catch (e: Exception) { "N/A" },

        // Software
        androidVersion = Build.VERSION.RELEASE,
        apiLevel = Build.VERSION.SDK_INT,
        buildId = Build.ID,
        buildType = Build.TYPE,
        securityPatch = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) Build.VERSION.SECURITY_PATCH else "N/A",
        bootloader = Build.BOOTLOADER,
        fingerprint = Build.FINGERPRINT,

        // Display
        screenWidth = configuration.screenWidthDp,
        screenHeight = configuration.screenHeightDp,
        screenDensity = context.resources.displayMetrics.densityDpi,
        refreshRate = context.display?.refreshRate ?: 0f,
        orientation = when (configuration.orientation) {
            android.content.res.Configuration.ORIENTATION_PORTRAIT -> "Portrait"
            android.content.res.Configuration.ORIENTATION_LANDSCAPE -> "Landscape"
            else -> "Unknown"
        },

        // Storage
        internalTotalSpace = formatBytes(getInternalTotalSpace()),
        internalAvailableSpace = formatBytes(getInternalAvailableSpace()),
        internalUsedSpace = formatBytes(getInternalTotalSpace() - getInternalAvailableSpace()),

        externalTotalSpace = formatBytes(getExternalTotalSpace(context)),
        externalAvailableSpace = formatBytes(getExternalAvailableSpace(context)),
        externalUsedSpace = formatBytes(getExternalTotalSpace(context) - getExternalAvailableSpace(context)),

        // Memory
        totalRam = formatBytes(getTotalRam(context)),
        availableRam = formatBytes(getAvailableRam(context)),

        // Battery
        batteryLevel = getBatteryLevel(context),
        batteryStatus = getBatteryStatus(context),
        batteryHealth = getBatteryHealth(context),
        batteryTechnology = getBatteryTechnology(context),
        batteryTemperature = getBatteryTemperature(context),
        batteryVoltage = getBatteryVoltage(context),

        // Network
        networkType = getNetworkType(context),
        wifiConnected = isWifiConnected(context).toString(),
        mobileDataEnabled = isMobileDataEnabled(context).toString(),

        // App
        appVersion = getAppVersion(context),
        packageName = packageName,
        targetSdk = context.applicationInfo.targetSdkVersion,
        minSdk = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            context.applicationInfo.minSdkVersion
        } else {
            1 // Minimum possible value
        }
    )
}

// Storage helper functions
private fun getInternalTotalSpace(): Long {
    return try {
        val stat = StatFs(Environment.getDataDirectory().path)
        stat.totalBytes
    } catch (e: Exception) {
        0L
    }
}

private fun getInternalAvailableSpace(): Long {
    return try {
        val stat = StatFs(Environment.getDataDirectory().path)
        stat.availableBytes
    } catch (e: Exception) {
        0L
    }
}

private fun getExternalTotalSpace(context: Context): Long {
    return try {
        val externalDir = context.getExternalFilesDir(null)
        if (externalDir != null) {
            val stat = StatFs(externalDir.path)
            stat.totalBytes
        } else 0L
    } catch (e: Exception) {
        0L
    }
}

private fun getExternalAvailableSpace(context: Context): Long {
    return try {
        val externalDir = context.getExternalFilesDir(null)
        if (externalDir != null) {
            val stat = StatFs(externalDir.path)
            stat.availableBytes
        } else 0L
    } catch (e: Exception) {
        0L
    }
}

// Memory helper functions
private fun getTotalRam(context: Context): Long {
    return try {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        val memoryInfo = android.app.ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        memoryInfo.totalMem
    } catch (e: Exception) {
        0L
    }
}

private fun getAvailableRam(context: Context): Long {
    return try {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as android.app.ActivityManager
        val memoryInfo = android.app.ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        memoryInfo.availMem
    } catch (e: Exception) {
        0L
    }
}

// Battery helper functions
private fun getBatteryLevel(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        if (level >= 0 && scale > 0) {
            "${(level * 100 / scale.toFloat()).toInt()}%"
        } else {
            "Unknown"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun getBatteryStatus(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        when (batteryIntent?.getIntExtra(BatteryManager.EXTRA_STATUS, -1)) {
            BatteryManager.BATTERY_STATUS_CHARGING -> "Charging"
            BatteryManager.BATTERY_STATUS_DISCHARGING -> "Discharging"
            BatteryManager.BATTERY_STATUS_FULL -> "Full"
            BatteryManager.BATTERY_STATUS_NOT_CHARGING -> "Not Charging"
            BatteryManager.BATTERY_STATUS_UNKNOWN -> "Unknown"
            else -> "Unknown"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun getBatteryHealth(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        when (batteryIntent?.getIntExtra(BatteryManager.EXTRA_HEALTH, -1)) {
            BatteryManager.BATTERY_HEALTH_COLD -> "Cold"
            BatteryManager.BATTERY_HEALTH_DEAD -> "Dead"
            BatteryManager.BATTERY_HEALTH_GOOD -> "Good"
            BatteryManager.BATTERY_HEALTH_OVERHEAT -> "Overheat"
            BatteryManager.BATTERY_HEALTH_OVER_VOLTAGE -> "Over Voltage"
            BatteryManager.BATTERY_HEALTH_UNKNOWN -> "Unknown"
            BatteryManager.BATTERY_HEALTH_UNSPECIFIED_FAILURE -> "Unspecified Failure"
            else -> "Unknown"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun getBatteryTechnology(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        batteryIntent?.getStringExtra(BatteryManager.EXTRA_TECHNOLOGY) ?: "Unknown"
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun getBatteryTemperature(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val temp = batteryIntent?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
        if (temp > 0) {
            "${temp / 10.0}°C"
        } else {
            "Unknown"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun getBatteryVoltage(context: Context): String {
    return try {
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val voltage = batteryIntent?.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1) ?: -1
        if (voltage > 0) {
            "${voltage / 1000.0}V"
        } else {
            "Unknown"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

// Network helper functions
private fun getNetworkType(context: Context): String {
    return try {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val capabilities = connectivityManager.getNetworkCapabilities(network)

        when {
            capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true -> "WiFi"
            capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true -> "Cellular"
            capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) == true -> "Ethernet"
            capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_BLUETOOTH) == true -> "Bluetooth"
            else -> "No Network"
        }
    } catch (e: Exception) {
        "Unknown"
    }
}

private fun isWifiConnected(context: Context): Boolean {
    return try {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val capabilities = connectivityManager.getNetworkCapabilities(network)
        capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) == true
    } catch (e: Exception) {
        false
    }
}

private fun isMobileDataEnabled(context: Context): Boolean {
    return try {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val capabilities = connectivityManager.getNetworkCapabilities(network)
        capabilities?.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) == true
    } catch (e: Exception) {
        false
    }
}

// App helper functions
private fun getAppVersion(context: Context): String {
    return try {
        val packageInfo = context.packageManager.getPackageInfo(context.packageName, 0)
        "${packageInfo.versionName} (${packageInfo.longVersionCode})"
    } catch (e: PackageManager.NameNotFoundException) {
        "Unknown"
    }
}

// Utility functions
private fun formatBytes(bytes: Long): String {
    if (bytes <= 0) return "0 B"

    val units = arrayOf("B", "KB", "MB", "GB", "TB")
    val digitGroups = (Math.log10(bytes.toDouble()) / Math.log10(1024.0)).toInt()
    val formatter = DecimalFormat("#,##0.#")

    return "${formatter.format(bytes / Math.pow(1024.0, digitGroups.toDouble()))} ${units[digitGroups]}"
}