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
import androidx.lifecycle.viewmodel.compose.viewModel
import com.sparesparrow.bpmdetector.services.BPMService
import com.sparesparrow.bpmdetector.ui.BPMApp
import com.sparesparrow.bpmdetector.ui.theme.BPMDetectorTheme
import com.sparesparrow.bpmdetector.viewmodels.BPMViewModel
import timber.log.Timber

class MainActivity : ComponentActivity() {

    // Service binding
    private var bpmService: BPMService? = null
    private var isServiceBound = false

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

    private val serviceConnection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            Timber.d("BPM service connected")
            val binder = service as BPMService.LocalBinder
            bpmService = binder.getService()
            isServiceBound = true

            // Set service reference in ViewModel
            val viewModel = viewModelStore["bpm_viewmodel"] as? BPMViewModel
            viewModel?.setBPMService(bpmService!!)
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            Timber.d("BPM service disconnected")
            val viewModel = viewModelStore["bpm_viewmodel"] as? BPMViewModel
            viewModel?.clearBPMService()

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

        setContent {
            BPMDetectorTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    val viewModel: BPMViewModel = viewModel()

                    BPMApp(viewModel = viewModel)
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        Timber.d("MainActivity started")

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

