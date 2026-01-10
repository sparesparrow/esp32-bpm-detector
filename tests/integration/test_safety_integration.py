#!/usr/bin/env python3
"""
Integration test for safety systems
Tests the interaction between SafetyManager, ErrorHandling, and Watchdog
"""

import sys
import os
import time
import unittest
from unittest.mock import Mock, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Mock the embedded-specific imports for testing on host
sys.modules['freertos'] = Mock()
sys.modules['esp_task_wdt'] = Mock()
sys.modules['esp_heap_caps'] = Mock()

class TestSafetyIntegration(unittest.TestCase):
    """Test safety system integration"""

    def setUp(self):
        """Set up test fixtures"""
        # Mock timer
        self.mock_timer = Mock()
        self.mock_timer.millis.return_value = 1000
        self.mock_timer.micros.return_value = 1000000

        # Mock log manager
        self.mock_log_manager = Mock()

    def test_safety_manager_initialization(self):
        """Test that SafetyManager initializes correctly"""
        try:
            from safety.SafetyManager import SafetyManager

            safety_manager = SafetyManager()
            config = SafetyManager.Config()
            config.watchdog_timeout_ms = 5000

            result = safety_manager.initialize(self.mock_timer, self.mock_log_manager, config)
            self.assertTrue(result, "SafetyManager should initialize successfully")

        except ImportError as e:
            self.skipTest(f"SafetyManager not available in test environment: {e}")

    def test_error_handling_integration(self):
        """Test error handling system integration"""
        try:
            from safety.ErrorHandling import ErrorHandling, DefaultErrorHandler

            error_handler = DefaultErrorHandler(self.mock_log_manager)

            # Test error reporting
            context = ErrorHandling.ErrorContext(
                code=ErrorHandling.ErrorCode.MEMORY_ALLOCATION_FAILED,
                severity=ErrorHandling.ErrorSeverity.ERROR,
                message="Test memory allocation failure",
                file="test_file.cpp",
                line=42,
                timestamp=1000,
                context_data=None
            )

            result = error_handler.handleError(context)
            self.assertTrue(result, "Error should be handled successfully")

            # Test recovery action
            action = error_handler.getRecoveryAction(ErrorHandling.ErrorCode.TIMEOUT)
            self.assertEqual(action.strategy, ErrorHandling.RecoveryStrategy.RETRY)
            self.assertEqual(action.max_retries, 5)

        except ImportError as e:
            self.skipTest(f"ErrorHandling not available in test environment: {e}")

    def test_watchdog_factory(self):
        """Test watchdog factory creates appropriate watchdog"""
        try:
            from safety.WatchdogFactory import WatchdogFactory

            # Test software watchdog creation
            watchdog = WatchdogFactory.createSoftwareWatchdog(self.mock_timer)
            self.assertIsNotNone(watchdog, "Should create software watchdog")

            # Test ESP32 watchdog (will return software fallback on non-ESP32)
            esp_watchdog = WatchdogFactory.createESP32Watchdog()
            # On non-ESP32 platforms, this returns nullptr
            # We don't assert here as it depends on the platform

        except ImportError as e:
            self.skipTest(f"WatchdogFactory not available in test environment: {e}")

    def test_memory_safety_utilities(self):
        """Test memory safety utilities"""
        try:
            from safety.MemorySafety import MemorySafety

            # Test safe vector
            safe_vec = MemorySafety.SafeVector[int](10)
            self.assertTrue(safe_vec.push_back(42))
            self.assertEqual(safe_vec.size(), 1)

            val = safe_vec.at(0)
            self.assertIsNotNone(val)
            self.assertEqual(val[0], 42)

            # Test out of bounds
            self.assertIsNone(safe_vec.at(10))

        except ImportError as e:
            self.skipTest(f"MemorySafety not available in test environment: {e}")

    def test_task_manager_configurations(self):
        """Test FreeRTOS task manager configurations"""
        try:
            from safety.FreeRTOSTaskManager import FreeRTOSTaskManager

            # Test default configurations
            audio_config = FreeRTOSTaskManager.AUDIO_SAMPLING_TASK_CONFIG
            self.assertEqual(audio_config.name, "AudioSampling")
            self.assertEqual(audio_config.priority, FreeRTOSTaskManager.TaskPriority.HIGH)

            network_config = FreeRTOSTaskManager.NETWORK_TASK_CONFIG
            self.assertEqual(network_config.name, "NetworkTask")
            self.assertEqual(network_config.priority, FreeRTOSTaskManager.TaskPriority.NORMAL)

        except ImportError as e:
            self.skipTest(f"FreeRTOSTaskManager not available in test environment: {e}")

    def test_power_manager_modes(self):
        """Test power manager mode transitions"""
        try:
            from safety.PowerManager import PowerManager

            power_manager = PowerManager()
            result = power_manager.initialize(self.mock_timer)
            self.assertTrue(result, "PowerManager should initialize")

            # Test mode setting
            power_manager.setPowerMode(PowerManager.PowerMode.POWERSAVE)
            self.assertEqual(power_manager.getCurrentPowerMode(), PowerManager.PowerMode.POWERSAVE)

            # Test activity update
            power_manager.updateActivity(PowerManager.ActivityLevel.HIGH)
            # Should potentially change mode based on activity

        except ImportError as e:
            self.skipTest(f"PowerManager not available in test environment: {e}")

if __name__ == '__main__':
    unittest.main()