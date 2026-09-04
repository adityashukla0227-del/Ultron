"""
Tests for the Ultron Microphone Capture implementation.

Version: v0.59
"""

from unittest.mock import MagicMock

import pytest

from modules.multimodal.audio_capture import AudioCapture
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.capture.microphone_capture import (
    MicrophoneCapture,
)


class FakeInputStream:
    """Fake sounddevice input stream for isolated unit tests."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.closed = False
        self.callback = kwargs.get("callback")

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def close(self):
        self.closed = True


class FakeSoundDevice:
    """Minimal fake sounddevice backend."""

    RawInputStream = FakeInputStream

    @staticmethod
    def query_devices(device=None, kind=None):
        return {
            "name": "Test Microphone",
            "max_input_channels": 1,
            "default_samplerate": 16000,
        }


def test_microphone_capture_is_audio_capture():
    """MicrophoneCapture implements the AudioCapture contract."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    assert isinstance(capture, AudioCapture)


def test_microphone_capture_defaults():
    """Default microphone configuration is correct."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    assert capture.get_sample_rate() == 16000
    assert capture.get_channels() == 1
    assert capture.is_recording() is False
    assert capture.get_last_capture() is None


def test_microphone_capture_custom_configuration():
    """Custom microphone configuration is preserved."""
    capture = MicrophoneCapture(
        backend=FakeSoundDevice(),
        sample_rate=44100,
        channels=2,
        device=3,
    )

    assert capture.get_sample_rate() == 44100
    assert capture.get_channels() == 2
    assert capture.get_device() == 3


def test_microphone_capture_is_available():
    """Microphone availability is detected through the backend."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    assert capture.is_available() is True


def test_microphone_capture_device_info():
    """Microphone device information is returned."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    info = capture.get_device_info()

    assert info["name"] == "Test Microphone"
    assert info["max_input_channels"] == 1
    assert info["default_samplerate"] == 16000


def test_microphone_capture_start():
    """Starting microphone capture creates and starts the stream."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()

    assert capture.is_recording() is True
    assert capture._stream is not None
    assert capture._stream.started is True


def test_microphone_capture_start_is_idempotent():
    """Starting an already active capture does not create another stream."""
    backend = FakeSoundDevice()
    capture = MicrophoneCapture(backend=backend)

    capture.start()
    first_stream = capture._stream

    capture.start()

    assert capture._stream is first_stream
    assert capture.is_recording() is True


def test_microphone_capture_stop_returns_voice_input():
    """Stopping capture returns a VoiceInput."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()

    # Simulate captured PCM audio.
    capture._audio_buffer.extend(b"\x00\x00" * 1600)
    capture._captured_frames = 1600

    voice_input = capture.stop()

    assert isinstance(voice_input, VoiceInput)
    assert voice_input.get_format() == "wav"
    assert voice_input.get_sample_rate() == 16000
    assert voice_input.get_channels() == 1
    assert voice_input.get_audio_data()


def test_microphone_capture_stop_updates_recording_state():
    """Stopping capture marks the capture as inactive."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()

    # Simulate captured PCM audio so stop() can produce a valid VoiceInput.
    capture._audio_buffer.extend(b"\x00\x00" * 100)
    capture._captured_frames = 100

    capture.stop()

    assert capture.is_recording() is False


def test_microphone_capture_stop_closes_stream():
    """Stopping capture closes the underlying stream."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()
    stream = capture._stream

    # Simulate captured PCM audio so stop() can complete successfully.
    capture._audio_buffer.extend(b"\x00\x00" * 100)
    capture._captured_frames = 100

    capture.stop()

    assert stream.stopped is True
    assert stream.closed is True
    assert capture._stream is None


def test_microphone_capture_last_capture():
    """Successful capture is stored as the last capture."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()
    capture._audio_buffer.extend(b"\x00\x00" * 1600)
    capture._captured_frames = 1600

    voice_input = capture.stop()

    assert capture.get_last_capture() is voice_input


def test_microphone_capture_source_metadata():
    """Captured VoiceInput contains microphone source metadata."""
    capture = MicrophoneCapture(
        backend=FakeSoundDevice(),
        metadata={"test": True},
    )

    capture.start()
    capture._audio_buffer.extend(b"\x00\x00" * 1600)
    capture._captured_frames = 1600

    voice_input = capture.stop()

    assert voice_input.get_metadata("source") == "microphone"
    assert voice_input.get_metadata("test") is True


def test_microphone_capture_wav_header():
    """Captured audio is encoded as a valid WAV container."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()
    capture._audio_buffer.extend(b"\x00\x00" * 1600)
    capture._captured_frames = 1600

    voice_input = capture.stop()

    audio_data = voice_input.get_audio_data()

    assert audio_data[:4] == b"RIFF"
    assert audio_data[8:12] == b"WAVE"


def test_microphone_capture_callback_collects_audio():
    """The stream callback stores incoming PCM audio."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()

    callback = capture._callback

    callback(
        b"\x01\x02" * 100,
        100,
        MagicMock(),
        None,
    )

    assert len(capture._audio_buffer) == 200
    assert capture._captured_frames == 100


def test_microphone_capture_callback_records_errors():
    """Callback stream errors are recorded."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()

    callback = capture._callback

    callback(
        b"\x01\x02",
        1,
        MagicMock(),
        "input overflow",
    )

    assert capture._capture_error is not None


def test_microphone_capture_stop_without_start_raises():
    """Stopping an inactive capture raises an error."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    with pytest.raises(Exception):
        capture.stop()


def test_microphone_capture_rejects_invalid_device():
    """Invalid device values are rejected."""
    with pytest.raises(ValueError):
        MicrophoneCapture(
            backend=FakeSoundDevice(),
            device=-1,
        )


def test_microphone_capture_device_setter():
    """The configured device can be changed."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.set_device(2)

    assert capture.get_device() == 2


def test_microphone_capture_reset():
    """Reset clears the previous capture state."""
    capture = MicrophoneCapture(backend=FakeSoundDevice())

    capture.start()
    capture._audio_buffer.extend(b"\x00\x00" * 100)
    capture._captured_frames = 100
    capture.stop()

    assert capture.get_last_capture() is not None

    capture.reset()

    assert capture.get_last_capture() is None
    assert capture.is_recording() is False
    assert len(capture._audio_buffer) == 0
    assert capture._captured_frames == 0
