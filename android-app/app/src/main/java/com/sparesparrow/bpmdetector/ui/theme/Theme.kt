package com.sparesparrow.bpmdetector.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = androidx.compose.ui.graphics.Color(0xFF4CAF50),
    onPrimary = androidx.compose.ui.graphics.Color.White,
    primaryContainer = androidx.compose.ui.graphics.Color(0xFF1B5E20),
    onPrimaryContainer = androidx.compose.ui.graphics.Color(0xFF4CAF50),
    secondary = androidx.compose.ui.graphics.Color(0xFFFF9800),
    onSecondary = androidx.compose.ui.graphics.Color.Black,
    tertiary = androidx.compose.ui.graphics.Color(0xFF2196F3),
    onTertiary = androidx.compose.ui.graphics.Color.White,
    error = androidx.compose.ui.graphics.Color(0xFFF44336),
    onError = androidx.compose.ui.graphics.Color.White,
    background = androidx.compose.ui.graphics.Color(0xFF121212),
    onBackground = androidx.compose.ui.graphics.Color.White,
    surface = androidx.compose.ui.graphics.Color(0xFF1E1E1E),
    onSurface = androidx.compose.ui.graphics.Color.White,
    surfaceVariant = androidx.compose.ui.graphics.Color(0xFF2D2D2D),
    onSurfaceVariant = androidx.compose.ui.graphics.Color(0xFFBDBDBD)
)

private val LightColorScheme = lightColorScheme(
    primary = androidx.compose.ui.graphics.Color(0xFF4CAF50),
    onPrimary = androidx.compose.ui.graphics.Color.White,
    primaryContainer = androidx.compose.ui.graphics.Color(0xFFE8F5E8),
    onPrimaryContainer = androidx.compose.ui.graphics.Color(0xFF1B5E20),
    secondary = androidx.compose.ui.graphics.Color(0xFFFF9800),
    onSecondary = androidx.compose.ui.graphics.Color.Black,
    tertiary = androidx.compose.ui.graphics.Color(0xFF2196F3),
    onTertiary = androidx.compose.ui.graphics.Color.White,
    error = androidx.compose.ui.graphics.Color(0xFFF44336),
    onError = androidx.compose.ui.graphics.Color.White,
    background = androidx.compose.ui.graphics.Color(0xFFFAFAFA),
    onBackground = androidx.compose.ui.graphics.Color.Black,
    surface = androidx.compose.ui.graphics.Color.White,
    onSurface = androidx.compose.ui.graphics.Color.Black,
    surfaceVariant = androidx.compose.ui.graphics.Color(0xFFF5F5F5),
    onSurfaceVariant = androidx.compose.ui.graphics.Color(0xFF424242)
)

@Composable
fun BPMDetectorTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    // Dynamic color is available on Android 12+
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }

        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }

    // Update status bar color
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.primary.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
