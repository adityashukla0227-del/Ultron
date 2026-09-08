"""
Tests for Ultron Audio Playback Foundation.

v0.66 — Audio Playback Foundation
"""

from typing import Any, Dict

import pytest

from modules.multimodal.audio_playback import (
    AudioPlayback,
    AudioPlaybackError,
)


class MockAudioPlayback(AudioPlayback):
    """Test implementation of AudioPlayback."""

    def __init__(
        self,
        *,
        metadata=None,
        available=True,
    ):
        super().__init__(
            metadata=metadata,
        )

        self.available = available
        self.play_calls = []
        self.stop_calls = 0
        self.pause_calls = 0
        self.resume_calls = 0

    def play(
        self,
        audio: Any,
    ) -> None:
        self._validate_audio(audio)
        self._set_last_audio(audio)
        self._set_status(
            self.STATUS_PLAYING
        )
        self.play_calls.append(audio)

    def stop(self) -> None:
        self.stop_calls += 1
        self._set_status(
            self.STATUS_STOPPED
        )

    def pause(self) -> None:
        self.pause_calls += 1
        self._set_status(
            self.STATUS_PAUSED
        )

    def resume(self) -> None:
        self.resume_calls += 1
        self._set_status(
            self.STATUS_PLAYING
        )

    def is_available(self) -> bool:
        return self.available

    def get_device_info(self) -> Dict[str, Any]:
        return {
            "name": "test-output-device",
            "type": "test",
        }


class TestAudioPlayback:
    """Test AudioPlayback behavior."""

    def test_initial_status_is_idle(self):
        playback = MockAudioPlayback()

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_IDLE
        )

    def test_initial_state_is_not_playing(self):
        playback = MockAudioPlayback()

        assert playback.is_playing() is False

    def test_initial_state_is_not_paused(self):
        playback = MockAudioPlayback()

        assert playback.is_paused() is False

    def test_initial_state_is_not_stopped(self):
        playback = MockAudioPlayback()

        assert playback.is_stopped() is False

    def test_initial_state_has_no_failure(self):
        playback = MockAudioPlayback()

        assert playback.has_failed() is False

    def test_play_changes_status_to_playing(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_PLAYING
        )

        assert playback.is_playing() is True

    def test_play_stores_last_audio(self):
        playback = MockAudioPlayback()

        audio = b"test-audio"

        playback.play(audio)

        assert (
            playback.get_last_audio()
            == audio
        )

    def test_play_records_audio(self):
        playback = MockAudioPlayback()

        audio = b"test-audio"

        playback.play(audio)

        assert playback.play_calls == [
            audio
        ]

    def test_stop_changes_status_to_stopped(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        playback.stop()

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_STOPPED
        )

        assert playback.is_stopped() is True

    def test_stop_increments_call_count(self):
        playback = MockAudioPlayback()

        playback.stop()

        assert playback.stop_calls == 1

    def test_pause_changes_status_to_paused(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        playback.pause()

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_PAUSED
        )

        assert playback.is_paused() is True

    def test_pause_increments_call_count(self):
        playback = MockAudioPlayback()

        playback.pause()

        assert playback.pause_calls == 1

    def test_resume_changes_status_to_playing(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        playback.pause()
        playback.resume()

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_PLAYING
        )

        assert playback.is_playing() is True

    def test_resume_increments_call_count(self):
        playback = MockAudioPlayback()

        playback.resume()

        assert playback.resume_calls == 1

    def test_none_audio_is_rejected(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback.play(None)

    def test_metadata_is_copied_on_initialization(self):
        metadata = {
            "provider": "test"
        }

        playback = MockAudioPlayback(
            metadata=metadata
        )

        metadata["provider"] = "changed"

        assert (
            playback.get_metadata_value(
                "provider"
            )
            == "test"
        )

    def test_metadata_is_defensive(self):
        playback = MockAudioPlayback(
            metadata={
                "provider": "test"
            }
        )

        metadata = playback.get_metadata()

        metadata["provider"] = "changed"

        assert (
            playback.get_metadata_value(
                "provider"
            )
            == "test"
        )

    def test_set_metadata(self):
        playback = MockAudioPlayback()

        playback.set_metadata(
            "provider",
            "test",
        )

        assert (
            playback.get_metadata_value(
                "provider"
            )
            == "test"
        )

    def test_set_metadata_rejects_invalid_key(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback.set_metadata(
                "",
                "value",
            )

    def test_get_metadata_rejects_invalid_key(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback.get_metadata_value(
                "",
            )

    def test_clear_metadata(self):
        playback = MockAudioPlayback(
            metadata={
                "provider": "test"
            }
        )

        playback.clear_metadata()

        assert (
            playback.get_metadata()
            == {}
        )

    def test_status_validation(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback._set_status(
                "invalid"
            )

    def test_audio_validation(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback._validate_audio(
                None
            )

    def test_set_last_audio(self):
        playback = MockAudioPlayback()

        audio = b"test-audio"

        playback._set_last_audio(audio)

        assert (
            playback.get_last_audio()
            == audio
        )

    def test_set_last_audio_rejects_none(self):
        playback = MockAudioPlayback()

        with pytest.raises(
            AudioPlaybackError
        ):
            playback._set_last_audio(
                None
            )

    def test_reset_returns_to_idle(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        playback.reset()

        assert (
            playback.get_status()
            == AudioPlayback.STATUS_IDLE
        )

        assert playback.get_last_audio() is None

    def test_reset_clears_last_audio(self):
        playback = MockAudioPlayback()

        playback.play(
            b"test-audio"
        )

        playback.reset()

        assert (
            playback.get_last_audio()
            is None
        )

    def test_availability(self):
        playback = MockAudioPlayback(
            available=True
        )

        assert playback.is_available() is True

    def test_unavailable_playback(self):
        playback = MockAudioPlayback(
            available=False
        )

        assert playback.is_available() is False

    def test_device_info(self):
        playback = MockAudioPlayback()

        info = playback.get_device_info()

        assert info["name"] == (
            "test-output-device"
        )

        assert info["type"] == "test"

    def test_repr(self):
        playback = MockAudioPlayback()

        assert repr(playback) == (
            "AudioPlayback("
            "status='idle'"
            ")"
        )