"""
Tests for the Ultron Audio Capture Foundation.

Version: v0.59
"""

import pytest

from modules.multimodal.audio_capture import AudioCapture, AudioCaptureError
from modules.multimodal.voice_input import VoiceInput


class DummyAudioCapture(AudioCapture):
    """Test implementation of the AudioCapture contract."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._recording = False
        self._device_info = {
            "name": "Test Microphone",
            "available": True,
        }

    def start(self) -> None:
        self._recording = True

    def stop(self) -> VoiceInput:
        self._recording = False

        voice_input = VoiceInput(
            b"test-audio",
            source="test",
            audio_format="wav",
            sample_rate=self.get_sample_rate(),
            channels=self.get_channels(),
        )

        self._set_last_capture(voice_input)
        return voice_input

    def is_recording(self) -> bool:
        return self._recording

    def is_available(self) -> bool:
        return True

    def get_device_info(self):
        return dict(self._device_info)


def test_audio_capture_is_abstract():
    """AudioCapture cannot be instantiated directly."""
    with pytest.raises(TypeError):
        AudioCapture()


def test_audio_capture_defaults():
    """Default capture configuration is correct."""
    capture = DummyAudioCapture()

    assert capture.get_sample_rate() == 16000
    assert capture.get_channels() == 1
    assert capture.get_metadata() == {}
    assert capture.get_last_capture() is None


def test_audio_capture_custom_configuration():
    """Custom capture configuration is preserved."""
    capture = DummyAudioCapture(
        sample_rate=44100,
        channels=2,
        metadata={"source": "test"},
    )

    assert capture.get_sample_rate() == 44100
    assert capture.get_channels() == 2
    assert capture.get_metadata() == {"source": "test"}


def test_audio_capture_rejects_invalid_sample_rate():
    """Invalid sample rates are rejected."""
    with pytest.raises(ValueError):
        DummyAudioCapture(sample_rate=0)

    with pytest.raises(ValueError):
        DummyAudioCapture(sample_rate=-16000)

    with pytest.raises(ValueError):
        DummyAudioCapture(sample_rate="16000")


def test_audio_capture_rejects_invalid_channels():
    """Invalid channel counts are rejected."""
    with pytest.raises(ValueError):
        DummyAudioCapture(channels=0)

    with pytest.raises(ValueError):
        DummyAudioCapture(channels=-1)

    with pytest.raises(ValueError):
        DummyAudioCapture(channels="1")


def test_audio_capture_start_and_recording_state():
    """Starting capture changes the recording state."""
    capture = DummyAudioCapture()

    assert capture.is_recording() is False

    capture.start()

    assert capture.is_recording() is True


def test_audio_capture_stop_returns_voice_input():
    """Stopping capture returns a VoiceInput."""
    capture = DummyAudioCapture()

    capture.start()
    voice_input = capture.stop()

    assert isinstance(voice_input, VoiceInput)
    assert voice_input.get_audio_data() == b"test-audio"
    assert voice_input.get_format() == "wav"
    assert voice_input.get_sample_rate() == 16000
    assert voice_input.get_channels() == 1


def test_audio_capture_last_capture():
    """Successful captures are stored as the last capture."""
    capture = DummyAudioCapture()

    assert capture.get_last_capture() is None

    capture.start()
    voice_input = capture.stop()

    assert capture.get_last_capture() is voice_input


def test_audio_capture_reset_last_capture():
    """Last capture can be cleared."""
    capture = DummyAudioCapture()

    capture.start()
    capture.stop()

    assert capture.get_last_capture() is not None

    capture.reset_last_capture()

    assert capture.get_last_capture() is None


def test_audio_capture_device_info():
    """Device information is exposed."""
    capture = DummyAudioCapture()

    info = capture.get_device_info()

    assert info["name"] == "Test Microphone"
    assert info["available"] is True


def test_audio_capture_metadata():
    """Metadata can be added and retrieved safely."""
    capture = DummyAudioCapture()

    capture.set_metadata("device", "Test Microphone")

    metadata = capture.get_metadata()

    assert metadata["device"] == "Test Microphone"

    metadata["device"] = "Modified"

    assert capture.get_metadata()["device"] == "Test Microphone"


def test_audio_capture_rejects_invalid_metadata_key():
    """Metadata keys must be non-empty strings."""
    capture = DummyAudioCapture()

    with pytest.raises(ValueError):
        capture.set_metadata("", "value")

    with pytest.raises(ValueError):
        capture.set_metadata("   ", "value")

    with pytest.raises(ValueError):
        capture.set_metadata(123, "value")


def test_audio_capture_set_last_capture_validates_type():
    """Only VoiceInput objects can be stored as the last capture."""
    capture = DummyAudioCapture()

    with pytest.raises(TypeError):
        capture._set_last_capture("invalid")


def test_audio_capture_error_exists():
    """AudioCaptureError is available as the capture-layer exception."""
    error = AudioCaptureError("capture failed")

    assert str(error) == "capture failed"