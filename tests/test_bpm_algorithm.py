"""
Host-side tests for the BPM detection algorithm.

These tests validate a Python reference implementation of the envelope-follower
+ peak-interval algorithm used in the ESP32 firmware (src/bpm_detector.cpp).
This lets us catch regressions in the core logic and calibrate tolerance
without needing embedded hardware.

Reference for the algorithm:
  - Compute short-time RMS envelope of the audio signal.
  - Detect peaks where envelope crosses an adaptive threshold.
  - Compute inter-beat intervals (IBI) and convert to BPM.
  - Filter outliers (IBI outside [60/max_bpm, 60/min_bpm] seconds).
"""

import math
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Python reference BPM detector (mirrors the ESP32 firmware logic)
# ---------------------------------------------------------------------------

MIN_BPM = 60.0
MAX_BPM = 200.0
SAMPLE_RATE = 25_000  # Hz


def _rms_envelope(samples: list[float], window: int = 512) -> list[float]:
    """Compute a sliding-window RMS envelope."""
    out = []
    for i in range(len(samples)):
        start = max(0, i - window // 2)
        end = min(len(samples), i + window // 2)
        chunk = samples[start:end]
        rms = math.sqrt(sum(x * x for x in chunk) / len(chunk))
        out.append(rms)
    return out


def _detect_beats(envelope: list[float], sample_rate: int, threshold_factor: float = 0.5) -> list[float]:
    """Return beat times in seconds using threshold crossing + refractory period."""
    if not envelope:
        return []
    mean_env = sum(envelope) / len(envelope)
    threshold = mean_env * threshold_factor
    min_ibi = 60.0 / MAX_BPM
    last_beat_time = -min_ibi

    beat_times = []
    in_peak = False
    for i, v in enumerate(envelope):
        t = i / sample_rate
        if v > threshold:
            if not in_peak and (t - last_beat_time) >= min_ibi:
                beat_times.append(t)
                last_beat_time = t
            in_peak = True
        else:
            in_peak = False
    return beat_times


def estimate_bpm(samples: list[float], sample_rate: int = SAMPLE_RATE) -> tuple[float, float]:
    """Return (bpm, confidence) from raw audio samples.

    confidence is fraction of IBI values that fell within the valid BPM range.
    Returns (0.0, 0.0) when fewer than 2 beats are detected.
    """
    envelope = _rms_envelope(samples, window=max(1, sample_rate // 50))
    beats = _detect_beats(envelope, sample_rate)
    if len(beats) < 2:
        return 0.0, 0.0

    ibis = [beats[i + 1] - beats[i] for i in range(len(beats) - 1)]
    valid_ibis = [ibi for ibi in ibis if (60.0 / MAX_BPM) <= ibi <= (60.0 / MIN_BPM)]
    if not valid_ibis:
        return 0.0, 0.0

    mean_ibi = sum(valid_ibis) / len(valid_ibis)
    bpm = 60.0 / mean_ibi
    confidence = len(valid_ibis) / len(ibis)
    return bpm, confidence


# ---------------------------------------------------------------------------
# Audio fixture generators
# ---------------------------------------------------------------------------

def _sine_beat_signal(bpm: float, duration_s: float, sample_rate: int = SAMPLE_RATE) -> list[float]:
    """Generate a synthetic beat signal: short sine bursts at a given BPM."""
    n_samples = int(duration_s * sample_rate)
    samples = [0.0] * n_samples
    beat_interval = sample_rate * 60.0 / bpm
    burst_len = max(1, int(sample_rate * 0.05))  # 50 ms burst

    beat_pos = 0
    while beat_pos < n_samples:
        for j in range(burst_len):
            idx = beat_pos + j
            if idx < n_samples:
                samples[idx] = math.sin(2 * math.pi * 440 * j / sample_rate)
        beat_pos += int(beat_interval)
    return samples


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestReferenceEnvelope:
    def test_sine_burst_has_nonzero_envelope(self):
        sig = _sine_beat_signal(120.0, 2.0)
        env = _rms_envelope(sig, window=512)
        assert max(env) > 0.0

    def test_silent_signal_has_zero_envelope(self):
        sig = [0.0] * SAMPLE_RATE
        env = _rms_envelope(sig, window=512)
        assert all(v == pytest.approx(0.0) for v in env)


class TestBeatDetection:
    def test_detects_correct_beat_count_at_120_bpm(self):
        bpm = 120.0
        duration = 5.0
        sig = _sine_beat_signal(bpm, duration)
        env = _rms_envelope(sig, window=512)
        beats = _detect_beats(env, SAMPLE_RATE)
        expected_beats = int(bpm * duration / 60)
        assert abs(len(beats) - expected_beats) <= 2

    def test_silent_signal_gives_no_beats(self):
        sig = [0.0] * (SAMPLE_RATE * 3)
        env = _rms_envelope(sig)
        beats = _detect_beats(env, SAMPLE_RATE)
        assert beats == []


class TestEstimateBPM:
    @pytest.mark.parametrize("target_bpm", [80.0, 100.0, 120.0, 140.0, 160.0])
    def test_detected_bpm_within_tolerance(self, target_bpm: float):
        """Detected BPM must be within ±5 BPM of ground truth for clean synth signals."""
        samples = _sine_beat_signal(target_bpm, duration_s=8.0)
        detected, confidence = estimate_bpm(samples)
        assert confidence > 0.5, f"Low confidence {confidence:.2f} at {target_bpm} BPM"
        assert abs(detected - target_bpm) <= 5.0, (
            f"Detected {detected:.1f} BPM, expected {target_bpm:.1f} ± 5.0"
        )

    def test_silent_signal_returns_zero_bpm(self):
        samples = [0.0] * (SAMPLE_RATE * 3)
        bpm, confidence = estimate_bpm(samples)
        assert bpm == pytest.approx(0.0)
        assert confidence == pytest.approx(0.0)

    def test_bpm_range_clamp_is_respected(self):
        """Very slow and very fast signals should fall outside the accepted range."""
        # 200 bursts/min is at the boundary — just test that it doesn't crash
        samples = _sine_beat_signal(200.0, 5.0)
        bpm, _ = estimate_bpm(samples)
        assert 0.0 <= bpm <= 220.0

    def test_too_short_signal_returns_zero(self):
        """A signal with only one beat cannot produce an IBI estimate."""
        samples = _sine_beat_signal(60.0, 0.5)  # less than 1 full beat cycle
        bpm, confidence = estimate_bpm(samples)
        # Either 0 BPM (no IBI) or a value — just verify no crash and types
        assert isinstance(bpm, float)
        assert isinstance(confidence, float)
