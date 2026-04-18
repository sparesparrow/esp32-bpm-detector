"""
Host-side roundtrip tests for the ESP32 BPM FlatBuffers wire protocol.

These tests build FlatBuffers messages using the generated Python bindings
under android-app/app/src/main/python/sparetools/bpm/, serialize them,
parse them back, and assert field equality.

This catches:
- Silent schema field reordering when flatc is re-run.
- Missing builder functions after schema changes.
- Python binding correctness independently of the Android app.
"""

import sys
from pathlib import Path

import flatbuffers
import pytest

# Make sparetools.bpm importable without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent / "android-app" / "app" / "src" / "main" / "python"))

from sparetools.bpm import (
    BPMAnalysis,
    BPMUpdate,
    DetectionStatus,
    StatusEnum,
)


# ---------------------------------------------------------------------------
# Enum stability
# ---------------------------------------------------------------------------

class TestEnumStability:
    def test_detection_status_ordinals(self):
        assert DetectionStatus.DetectionStatus.INITIALIZING == 0
        assert DetectionStatus.DetectionStatus.DETECTING == 1
        assert DetectionStatus.DetectionStatus.LOW_SIGNAL == 2
        assert DetectionStatus.DetectionStatus.NO_SIGNAL == 3
        assert DetectionStatus.DetectionStatus.ERROR == 4
        assert DetectionStatus.DetectionStatus.CALIBRATING == 5

    def test_status_enum_ordinals(self):
        assert StatusEnum.StatusEnum.Success == 0
        assert StatusEnum.StatusEnum.Error == 1
        assert StatusEnum.StatusEnum.Warning == 2
        assert StatusEnum.StatusEnum.Info == 3


# ---------------------------------------------------------------------------
# BPMAnalysis roundtrip
# ---------------------------------------------------------------------------

class TestBPMAnalysisRoundtrip:
    def test_all_float_fields_roundtrip(self):
        builder = flatbuffers.Builder(128)
        BPMAnalysis.Start(builder)
        BPMAnalysis.AddStability(builder, 0.85)
        BPMAnalysis.AddRegularity(builder, 0.92)
        BPMAnalysis.AddDominantFrequency(builder, 2.01)
        BPMAnalysis.AddSpectralCentroid(builder, 3.14)
        BPMAnalysis.AddBeatPosition(builder, 0.5)
        BPMAnalysis.AddTempoConsistency(builder, 0.78)
        end = BPMAnalysis.End(builder)
        builder.Finish(end)

        parsed = BPMAnalysis.BPMAnalysis.GetRootAs(builder.Output(), 0)
        assert parsed.Stability() == pytest.approx(0.85, abs=1e-4)
        assert parsed.Regularity() == pytest.approx(0.92, abs=1e-4)
        assert parsed.DominantFrequency() == pytest.approx(2.01, abs=1e-4)
        assert parsed.SpectralCentroid() == pytest.approx(3.14, abs=1e-4)
        assert parsed.BeatPosition() == pytest.approx(0.5, abs=1e-4)
        assert parsed.TempoConsistency() == pytest.approx(0.78, abs=1e-4)

    def test_defaults_when_unset(self):
        builder = flatbuffers.Builder(64)
        BPMAnalysis.Start(builder)
        end = BPMAnalysis.End(builder)
        builder.Finish(end)

        parsed = BPMAnalysis.BPMAnalysis.GetRootAs(builder.Output(), 0)
        assert parsed.Stability() == pytest.approx(0.0)
        assert parsed.Regularity() == pytest.approx(0.0)
        assert parsed.DominantFrequency() == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# BPMUpdate roundtrip (scalar fields only — nested tables skipped for brevity)
# ---------------------------------------------------------------------------

class TestBPMUpdateRoundtrip:
    def test_scalar_fields_roundtrip(self):
        builder = flatbuffers.Builder(128)
        BPMUpdate.Start(builder)
        BPMUpdate.AddBpm(builder, 128.5)
        BPMUpdate.AddConfidence(builder, 0.87)
        BPMUpdate.AddSignalLevel(builder, 0.72)
        BPMUpdate.AddStatus(builder, DetectionStatus.DetectionStatus.DETECTING)
        BPMUpdate.AddTimestamp(builder, 1_700_000_000_000)
        end = BPMUpdate.End(builder)
        builder.Finish(end)

        parsed = BPMUpdate.BPMUpdate.GetRootAs(builder.Output(), 0)
        assert parsed.Bpm() == pytest.approx(128.5, abs=1e-2)
        assert parsed.Confidence() == pytest.approx(0.87, abs=1e-4)
        assert parsed.SignalLevel() == pytest.approx(0.72, abs=1e-4)
        assert parsed.Status() == DetectionStatus.DetectionStatus.DETECTING
        assert parsed.Timestamp() == 1_700_000_000_000

    def test_no_signal_status(self):
        builder = flatbuffers.Builder(64)
        BPMUpdate.Start(builder)
        BPMUpdate.AddBpm(builder, 0.0)
        BPMUpdate.AddConfidence(builder, 0.0)
        BPMUpdate.AddStatus(builder, DetectionStatus.DetectionStatus.NO_SIGNAL)
        end = BPMUpdate.End(builder)
        builder.Finish(end)

        parsed = BPMUpdate.BPMUpdate.GetRootAs(builder.Output(), 0)
        assert parsed.Bpm() == pytest.approx(0.0)
        assert parsed.Status() == DetectionStatus.DetectionStatus.NO_SIGNAL

    def test_defaults_when_unset(self):
        builder = flatbuffers.Builder(64)
        BPMUpdate.Start(builder)
        end = BPMUpdate.End(builder)
        builder.Finish(end)

        parsed = BPMUpdate.BPMUpdate.GetRootAs(builder.Output(), 0)
        assert parsed.Bpm() == pytest.approx(0.0)
        assert parsed.Confidence() == pytest.approx(0.0)
        assert parsed.Status() == DetectionStatus.DetectionStatus.INITIALIZING
        assert parsed.Timestamp() == 0

    def test_update_with_nested_analysis_roundtrips(self):
        """Build a BPMUpdate embedding a BPMAnalysis sub-table."""
        builder = flatbuffers.Builder(256)

        # Build nested table first.
        BPMAnalysis.Start(builder)
        BPMAnalysis.AddStability(builder, 0.9)
        BPMAnalysis.AddDominantFrequency(builder, 2.0)
        analysis = BPMAnalysis.End(builder)

        BPMUpdate.Start(builder)
        BPMUpdate.AddBpm(builder, 120.0)
        BPMUpdate.AddConfidence(builder, 0.95)
        BPMUpdate.AddStatus(builder, DetectionStatus.DetectionStatus.DETECTING)
        BPMUpdate.AddAnalysis(builder, analysis)
        BPMUpdate.AddTimestamp(builder, 42)
        end = BPMUpdate.End(builder)
        builder.Finish(end)

        parsed = BPMUpdate.BPMUpdate.GetRootAs(builder.Output(), 0)
        assert parsed.Bpm() == pytest.approx(120.0, abs=1e-2)
        assert parsed.Confidence() == pytest.approx(0.95, abs=1e-4)
        assert parsed.Timestamp() == 42

        nested = parsed.Analysis()
        assert nested is not None
        assert nested.Stability() == pytest.approx(0.9, abs=1e-4)
        assert nested.DominantFrequency() == pytest.approx(2.0, abs=1e-4)
