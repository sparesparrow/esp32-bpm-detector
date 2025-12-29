package com.sparesparrow.bpmdetector.ui

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.Settings
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Navigation screens
 */
sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object BPMDisplay : Screen("bpm_display", "BPM", Icons.Filled.Favorite)
    object Settings : Screen("settings", "Settings", Icons.Filled.Settings)
    object DeviceInfo : Screen("device_info", "Device Info", Icons.Filled.Info)
}

