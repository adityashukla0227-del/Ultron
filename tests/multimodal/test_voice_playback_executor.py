"""
Tests for ULTRON v0.68 Voice Playback Execution.
"""

from __future__ import annotations

import pytest

from modules.multimodal.audio_output_device import (
    AudioOutputDevice,
)
from modules.multimodal.audio_output_device_manager import (
    AudioOutputDeviceManager,
)
from modules.multimodal.audio_playback import (
    AudioPlaybackError,
)
from modules.multimodal.voice_playback_executor import (
    VoicePlaybackExecutor,
    VoicePlaybackExecutorError,
)


class MockPlaybackBackend:
    """Mock backend used for executor tests."""

    def __init__(self) -> None:
        self.play_calls = []
        self.stop_calls = 0
        self.pause_calls = 0
        self.resume_calls = 0

        self.fail_play = False
        self.fail_stop = False
        self.fail_pause = False
        self.fail_resume = False

    def __call__(
        self,
        audio,
        device,
    ) -> None:
        if self.fail_play:
            raise RuntimeError(
                "mock playback failure"
            )

        self.play_calls.append(
            {
                "audio": audio,
                "device": device,
            }
        )

    def stop(self) -> None:
        if self.fail_stop:
            raise RuntimeError(
                "mock stop failure"
            )

        self.stop_calls += 1

    def pause(self) -> None:
        if self.fail_pause:
            raise RuntimeError(
                "mock pause failure"
            )

        self.pause_calls += 1

    def resume(self) -> None:
        if self.fail_resume:
            raise RuntimeError(
                "mock resume failure"
            )

        self.resume_calls += 1


def create_device_manager(
    *,
    available: bool = True,
    is_default: bool = True,
) -> AudioOutputDeviceManager:
    manager = AudioOutputDeviceManager()

    device = AudioOutputDevice(
        device_id="speaker-1",
        name="Test Speaker",
        device_type="speaker",
        available=available,
        is_default=is_default,
        sample_rates=[16000, 44100, 48000],
        supported_formats=["mp3", "wav"],
    )

    manager.register_device(device)

    return manager


def create_executor(
    *,
    available: bool = True,
    is_default: bool = True,
):
    manager = create_device_manager(
        available=available,
        is_default=is_default,
    )

    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    return executor, backend, manager


def test_initial_state():
    executor, backend, manager = create_executor()

    assert executor.get_status() == executor.STATUS_IDLE
    assert executor.get_last_audio() is None
    assert executor.get_last_device_id() is None
    assert executor.get_last_result()["success"] is False


def test_play_executes_backend():
    executor, backend, manager = create_executor()

    audio = b"audio-data"

    executor.play(audio)

    assert len(backend.play_calls) == 1
    assert backend.play_calls[0]["audio"] == audio
    assert (
        backend.play_calls[0]["device"].get_device_id()
        == "speaker-1"
    )


def test_play_stores_last_audio():
    executor, backend, manager = create_executor()

    audio = b"audio-data"

    executor.play(audio)

    assert executor.get_last_audio() == audio


def test_play_tracks_device():
    executor, backend, manager = create_executor()

    executor.play(b"audio")

    assert executor.get_last_device_id() == "speaker-1"


def test_successful_playback_stops():
    executor, backend, manager = create_executor()

    executor.play(b"audio")

    assert executor.get_status() == executor.STATUS_STOPPED
    assert executor.is_stopped()


def test_successful_playback_result():
    executor, backend, manager = create_executor()

    result = executor.execute(b"audio")

    assert result["success"] is True
    assert result["status"] == executor.STATUS_STOPPED
    assert result["device_id"] == "speaker-1"
    assert result["device_name"] == "Test Speaker"


def test_execute_returns_defensive_result():
    executor, backend, manager = create_executor()

    result = executor.execute(b"audio")

    result["success"] = False

    assert executor.get_last_result()["success"] is True


def test_none_audio_is_rejected():
    executor, backend, manager = create_executor()

    with pytest.raises(AudioPlaybackError):
        executor.play(None)


def test_none_audio_execute_returns_failure():
    executor, backend, manager = create_executor()

    result = executor.execute(None)

    assert result["success"] is False
    assert result["status"] == executor.STATUS_FAILED


def test_backend_failure_sets_failed_state():
    executor, backend, manager = create_executor()

    backend.fail_play = True

    with pytest.raises(AudioPlaybackError):
        executor.play(b"audio")

    assert executor.has_failed()


def test_backend_failure_result():
    executor, backend, manager = create_executor()

    backend.fail_play = True

    result = executor.execute(b"audio")

    assert result["success"] is False
    assert result["status"] == executor.STATUS_FAILED
    assert result["device_id"] == "speaker-1"
    assert "mock playback failure" in result["error"]


def test_no_output_device_raises():
    manager = AudioOutputDeviceManager()
    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    with pytest.raises(
        VoicePlaybackExecutorError,
        match="No active or default output device",
    ):
        executor.play(b"audio")


def test_no_output_device_is_unavailable():
    manager = AudioOutputDeviceManager()
    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    assert executor.is_available() is False


def test_unavailable_default_device_raises():
    executor, backend, manager = create_executor(
        available=False,
        is_default=True,
    )

    with pytest.raises(
        VoicePlaybackExecutorError,
        match="unavailable",
    ):
        executor.play(b"audio")


def test_get_device_info():
    executor, backend, manager = create_executor()

    info = executor.get_device_info()

    assert info["device_id"] == "speaker-1"
    assert info["name"] == "Test Speaker"
    assert info["device_type"] == "speaker"
    assert info["available"] is True


def test_is_available_with_device():
    executor, backend, manager = create_executor()

    assert executor.is_available() is True


def test_active_device_has_priority_over_default():
    manager = AudioOutputDeviceManager()

    default_device = AudioOutputDevice(
        device_id="speaker-1",
        name="Default Speaker",
        device_type="speaker",
        available=True,
        is_default=True,
    )

    active_device = AudioOutputDevice(
        device_id="headphones-1",
        name="Headphones",
        device_type="headphones",
        available=True,
        is_default=False,
    )

    manager.register_device(default_device)
    manager.register_device(active_device)

    manager.set_active_device(
        "headphones-1"
    )

    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    executor.play(b"audio")

    assert (
        backend.play_calls[0]["device"].get_device_id()
        == "headphones-1"
    )


def test_default_device_used_when_no_active_device():
    manager = AudioOutputDeviceManager()

    device = AudioOutputDevice(
        device_id="speaker-1",
        name="Default Speaker",
        device_type="speaker",
        available=True,
        is_default=True,
    )

    manager.register_device(device)
    manager.clear_active_device()

    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    executor.play(b"audio")

    assert (
        backend.play_calls[0]["device"].get_device_id()
        == "speaker-1"
    )


def test_stop_delegates_to_backend():
    executor, backend, manager = create_executor()

    executor._set_status(
        executor.STATUS_PLAYING
    )

    executor.stop()

    assert backend.stop_calls == 1
    assert executor.is_stopped()


def test_pause_delegates_to_backend():
    executor, backend, manager = create_executor()

    executor._set_status(
        executor.STATUS_PLAYING
    )

    executor.pause()

    assert backend.pause_calls == 1
    assert executor.is_paused()


def test_resume_delegates_to_backend():
    executor, backend, manager = create_executor()

    executor._set_status(
        executor.STATUS_PAUSED
    )

    executor.resume()

    assert backend.resume_calls == 1
    assert executor.is_playing()


def test_pause_requires_playing_state():
    executor, backend, manager = create_executor()

    with pytest.raises(
        AudioPlaybackError,
        match="must be playing",
    ):
        executor.pause()


def test_resume_requires_paused_state():
    executor, backend, manager = create_executor()

    with pytest.raises(
        AudioPlaybackError,
        match="must be paused",
    ):
        executor.resume()


def test_pause_requires_backend_support():
    manager = create_device_manager()

    def backend(audio, device):
        return None

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    executor._set_status(
        executor.STATUS_PLAYING
    )

    with pytest.raises(
        AudioPlaybackError,
        match="does not support pause",
    ):
        executor.pause()


def test_resume_requires_backend_support():
    manager = create_device_manager()

    def backend(audio, device):
        return None

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    executor._set_status(
        executor.STATUS_PAUSED
    )

    with pytest.raises(
        AudioPlaybackError,
        match="does not support resume",
    ):
        executor.resume()


def test_stop_without_active_playback_is_safe():
    executor, backend, manager = create_executor()

    executor.stop()

    assert executor.is_stopped()


def test_reset_clears_execution_state():
    executor, backend, manager = create_executor()

    executor.play(b"audio")

    executor.reset()

    assert executor.get_status() == executor.STATUS_IDLE
    assert executor.get_last_audio() is None
    assert executor.get_last_device_id() is None
    assert executor.get_last_result()["success"] is False


def test_invalid_device_manager_is_rejected():
    backend = MockPlaybackBackend()

    with pytest.raises(
        VoicePlaybackExecutorError,
        match="device_manager",
    ):
        VoicePlaybackExecutor(
            device_manager=object(),
            playback_backend=backend,
        )


def test_invalid_backend_is_rejected():
    manager = AudioOutputDeviceManager()

    with pytest.raises(
        VoicePlaybackExecutorError,
        match="playback_backend",
    ):
        VoicePlaybackExecutor(
            device_manager=manager,
            playback_backend=object(),
        )


def test_repr():
    executor, backend, manager = create_executor()

    representation = repr(executor)

    assert "VoicePlaybackExecutor" in representation
    assert "status='idle'" in representation