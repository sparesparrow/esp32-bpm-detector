package com.sparesparrow.bpmdetector

import android.app.Application
import timber.log.Timber

/**
 * Application class for BPM Detector app
 */
class BPMApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Initialize Timber logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }

        Timber.d("BPMApplication created")
    }
}

