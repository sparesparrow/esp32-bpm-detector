package com.sparesparrow.bpmdetector

import android.Manifest
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.IBinder
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.core.view.WindowCompat
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.ui.BPMApp
import com.sparesparrow.bpmdetector.ui.theme.BPMDetectorTheme
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import timber.log.Timber

class MainActivity : ComponentActivity() {

    // Service binding
    private var bpmService: BPMService? = null
    private var isServiceBound = false

    // ViewModel reference for service binding
    private lateinit var viewModel: BPMViewModel

    // Audio permission launcher
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            Timber.d("Audio recording permission granted")
        } else {
            Timber.w("Audio recording permission denied")
        }
    }

    // Location permission launcher for WiFi scanning
    private val requestLocationPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val fineLocationGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseLocationGranted = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] ?: false

        if (fineLocationGranted || coarseLocationGranted) {
            Timber.d("Location permissions granted - WiFi scanning enabled")
            viewModel.autoDiscoverDevice()
        } else {
            Timber.w("Location permissions denied - WiFi scanning disabled")
        }
    }

    /**
     * Check and request audio recording permission if needed
     */
    fun checkAudioPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            when {
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.RECORD_AUDIO
                ) == PackageManager.PERMISSION_GRANTED -> {
                    true
                }
                else -> {
                    requestPermissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                    false
                }
            }
        } else {
            true // Permission granted by default on older Android versions
        }
    }

    /**
     * Check if location permissions are granted
     */
    fun checkLocationPermissions(): Boolean {
        val fineLocationGranted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        val coarseLocationGranted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.ACCESS_COARSE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        return fineLocationGranted || coarseLocationGranted
    }

    /**
     * Request location permissions if needed
     */
    fun requestLocationPermissionsIfNeeded() {
        if (!checkLocationPermissions()) {
            requestLocationPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_FINE_LOCATION,
                    Manifest.permission.ACCESS_COARSE_LOCATION
                )
            )
        }
    }

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            Timber.d("BPM service connected")
            try {
                val binder = service as? BPMService.LocalBinder ?: run {
                    Timber.e("Invalid service binder type")
                    return
                }

                bpmService = binder.getService()
                isServiceBound = true

                // Ensure ViewModel is initialized
                if (::viewModel.isInitialized) {
                    viewModel.setBPMService(bpmService!!)
                } else {
                    Timber.w("ViewModel not initialized yet, deferring service setup")
                    // Retry after a short delay
                    lifecycleScope.launch {
                        delay(100)
                        if (::viewModel.isInitialized) {
                            viewModel.setBPMService(bpmService!!)
                        }
                    }
                }
            } catch (e: Exception) {
                Timber.e(e, "Error setting up service connection")
            }
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            Timber.d("BPM service disconnected")
            if (::viewModel.isInitialized) {
                viewModel.clearBPMService()
            }

            bpmService = null
            isServiceBound = false
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Enable edge-to-edge display
        enableEdgeToEdge()
        WindowCompat.setDecorFitsSystemWindows(window, false)

        // Initialize Timber logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        Timber.d("MainActivity created")

        // Initialize ViewModel for service binding
        viewModel = androidx.lifecycle.ViewModelProvider(this)[BPMViewModel::class.java]

        setContent {
            BPMDetectorTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    BPMApp(viewModel = this@MainActivity.viewModel)
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        Timber.d("MainActivity started")

        // Request location permissions for WiFi scanning
        requestLocationPermissionsIfNeeded()

        // Bind to BPM service
        Intent(this, BPMService::class.java).also { intent ->
            bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE)
        }
    }

    override fun onStop() {
        super.onStop()
        Timber.d("MainActivity stopped")

        // Unbind from service
        if (isServiceBound) {
            unbindService(serviceConnection)
            isServiceBound = false
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        Timber.d("MainActivity destroyed")
    }

    companion object {
        /**
         * Create intent for MainActivity with server IP
         */
        fun createIntent(context: Context, serverIp: String? = null): Intent {
            return Intent(context, MainActivity::class.java).apply {
                serverIp?.let { putExtra("server_ip", it) }
            }
        }
    }
}

