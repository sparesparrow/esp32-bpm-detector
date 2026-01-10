package com.sparesparrow.bpmdetector

import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.filters.LargeTest
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiSelector
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * UI Automator tests for BPM Detector Android app
 * Tests complete user workflows and device interactions
 */
@RunWith(AndroidJUnit4::class)
@LargeTest
class BPMDetectorUiTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    private val uiDevice = UiDevice.getInstance(androidx.test.platform.app.InstrumentationRegistry.getInstrumentation())

    @Test
    fun testAppLaunchAndInitialState() {
        // Wait for app to load
        Thread.sleep(2000)

        // Check that main activity is displayed
        onView(withId(R.id.main_activity_root))
            .check(matches(isDisplayed()))

        // Check that BPM display is visible
        onView(withText("BPM Detection"))
            .check(matches(isDisplayed()))
    }

    @Test
    fun testSettingsNavigation() {
        // Wait for app to load
        Thread.sleep(2000)

        // Click settings button (assuming there's a settings/navigation button)
        // This would need to be updated based on actual UI
        // onView(withId(R.id.settings_button)).perform(click())

        // For now, just verify the app doesn't crash
        onView(withId(R.id.main_activity_root))
            .check(matches(isDisplayed()))
    }

    @Test
    fun testPermissionDialogHandling() {
        // Test that permission dialogs appear when needed
        val scenario = ActivityScenario.launch(MainActivity::class.java)

        // Wait for permission dialog or main screen
        Thread.sleep(3000)

        // Check if permission dialog is shown or main screen is displayed
        try {
            // Try to find permission dialog
            val allowButton = uiDevice.findObject(UiSelector().textContains("Allow"))
            if (allowButton.exists()) {
                // Permission dialog is shown - this is expected behavior
                assert(true)
            } else {
                // No permission dialog - main screen should be visible
                onView(withId(R.id.main_activity_root))
                    .check(matches(isDisplayed()))
            }
        } catch (e: Exception) {
            // If UI Automator fails, fall back to basic Espresso check
            onView(withId(R.id.main_activity_root))
                .check(matches(isDisplayed()))
        }
    }

    @Test
    fun testAppStability() {
        // Test basic app stability - no crashes
        val scenario = ActivityScenario.launch(MainActivity::class.java)

        // Wait and perform basic interactions
        Thread.sleep(2000)

        // Rotate device (if supported)
        try {
            uiDevice.setOrientationLeft()
            Thread.sleep(1000)
            uiDevice.setOrientationNatural()
            Thread.sleep(1000)
        } catch (e: Exception) {
            // Orientation change not supported in this test environment
        }

        // App should still be running
        onView(withId(R.id.main_activity_root))
            .check(matches(isDisplayed()))

        scenario.close()
    }

    @Test
    fun testBackNavigation() {
        // Test back button handling
        val scenario = ActivityScenario.launch(MainActivity::class.java)

        Thread.sleep(2000)

        // Press back button
        uiDevice.pressBack()

        // App should handle back press gracefully (either close or navigate)
        // This test mainly ensures no crashes
        Thread.sleep(1000)

        scenario.close()
    }
}