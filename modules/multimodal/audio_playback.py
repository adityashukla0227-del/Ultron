"""
Ultron Audio Playback Foundation

v0.66 — Audio Playback Foundation

Defines the provider- and device-independent abstraction
for playing synthesized audio output.

Responsibilities:
- Define the audio playback contract
- Manage playback lifecycle state
- Validate audio input
- Expose playback status
- Expose device information
- Maintain playback metadata

This module does NOT:
- Implement a concrete audio device
- Play audio directly
- Manage operating-system audio devices
- Contain provider-specific TTS logic
- Perform TTS synthesis
- Perform STT
- Execute agents or tools
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict


class AudioPlaybackError(Exception):
    """Base exception for audio playback errors."""


class AudioPlayback(ABC):
    """
    Abstract interface for audio playback.

    AudioPlayback defines the contract required by future
    concrete audio output implementations.

    Lifecycle:

        idle
          ↓
        playing
          ↓
        paused
          ↓
        playing
          ↓
        stopped
    """

    STATUS_IDLE = "idle"
    STATUS_PLAYING = "playing"
    STATUS_PAUSED = "paused"
    STATUS_STOPPED = "stopped"
    STATUS_FAILED = "failed"

    VALID_STATUSES = {
        STATUS_IDLE,
        STATUS_PLAYING,
        STATUS_PAUSED,
        STATUS_STOPPED,
        STATUS_FAILED,
    }

    def __init__(
        self,
        *,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise AudioPlaybackError(
                "metadata must be a dictionary or None."
            )

        self._status = self.STATUS_IDLE
        self._metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

        self._last_audio: Any = None

    @abstractmethod
    def play(
        self,
        audio: Any,
    ) -> None:
        """
        Start playback of audio data.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """
        Stop current playback.
        """
        raise NotImplementedError

    @abstractmethod
    def pause(self) -> None:
        """
        Pause current playback.
        """
        raise NotImplementedError

    @abstractmethod
    def resume(self) -> None:
        """
        Resume paused playback.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return whether audio playback is available.
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return information about the active output device.
        """
        raise NotImplementedError

    def get_status(self) -> str:
        """
        Return the current playback status.
        """
        return self._status

    def is_playing(self) -> bool:
        """
        Return True when audio is currently playing.
        """
        return self._status == self.STATUS_PLAYING

    def is_paused(self) -> bool:
        """
        Return True when playback is paused.
        """
        return self._status == self.STATUS_PAUSED

    def is_stopped(self) -> bool:
        """
        Return True when playback is stopped.
        """
        return self._status == self.STATUS_STOPPED

    def has_failed(self) -> bool:
        """
        Return True when playback is in a failed state.
        """
        return self._status == self.STATUS_FAILED

    def get_last_audio(self) -> Any:
        """
        Return the last audio object supplied for playback.
        """
        return self._last_audio

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return a defensive copy of playback metadata.
        """
        return deepcopy(self._metadata)

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set playback metadata.
        """
        if not isinstance(key, str) or not key.strip():
            raise AudioPlaybackError(
                "metadata key must be a non-empty string."
            )

        self._metadata[key.strip()] = value

    def get_metadata_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a metadata value.
        """
        if not isinstance(key, str) or not key.strip():
            raise AudioPlaybackError(
                "metadata key must be a non-empty string."
            )

        return self._metadata.get(
            key.strip(),
            default,
        )

    def clear_metadata(self) -> None:
        """
        Clear all playback metadata.
        """
        self._metadata.clear()

    def _validate_audio(
        self,
        audio: Any,
    ) -> None:
        """
        Validate audio data before playback.

        Concrete implementations may add provider- or
        device-specific validation.
        """
        if audio is None:
            raise AudioPlaybackError(
                "audio cannot be None."
            )

    def _set_status(
        self,
        status: str,
    ) -> None:
        """
        Update playback status.
        """
        if not isinstance(status, str):
            raise AudioPlaybackError(
                "status must be a string."
            )

        normalized = status.strip().lower()

        if normalized not in self.VALID_STATUSES:
            raise AudioPlaybackError(
                f"Invalid playback status: {status}"
            )

        self._status = normalized

    def _set_last_audio(
        self,
        audio: Any,
    ) -> None:
        """
        Store the most recently supplied audio object.
        """
        self._validate_audio(audio)
        self._last_audio = audio

    def reset(self) -> None:
        """
        Reset playback state to idle.

        Concrete implementations should override this method
        only when device-specific cleanup is required.
        """
        self._status = self.STATUS_IDLE
        self._last_audio = None

    def __repr__(self) -> str:
        return (
            "AudioPlayback("
            f"status={self._status!r}"
            ")"
        )


__all__ = [
    "AudioPlayback",
    "AudioPlaybackError",
]