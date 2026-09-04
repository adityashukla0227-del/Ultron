"""
Ultron Audio Capture Foundation

Provides the abstract contract for capturing audio input.

Version: v0.59
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from modules.multimodal.voice_input import VoiceInput


class AudioCaptureError(Exception):
    """Base exception for audio capture errors."""


class AudioCapture(ABC):
    """
    Abstract interface for audio capture implementations.

    AudioCapture is responsible only for acquiring audio from an input
    source. It does not perform speech-to-text, voice processing, or
    runtime execution.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        channels: int = 1,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            raise ValueError("sample_rate must be a positive integer")

        if not isinstance(channels, int) or channels <= 0:
            raise ValueError("channels must be a positive integer")

        self._sample_rate = sample_rate
        self._channels = channels
        self._metadata = dict(metadata or {})
        self._last_capture: VoiceInput | None = None

    @abstractmethod
    def start(self) -> None:
        """
        Start capturing audio.

        Raises:
            AudioCaptureError: If capture cannot be started.
        """
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> VoiceInput:
        """
        Stop capturing audio and return the captured VoiceInput.

        Returns:
            VoiceInput: Captured audio input.

        Raises:
            AudioCaptureError: If capture cannot be stopped or no valid
                capture is available.
        """
        raise NotImplementedError

    @abstractmethod
    def is_recording(self) -> bool:
        """
        Return whether audio capture is currently active.
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """
        Return whether the capture source is currently available.
        """
        raise NotImplementedError

    @abstractmethod
    def get_device_info(self) -> Dict[str, Any]:
        """
        Return information about the active/default capture device.
        """
        raise NotImplementedError

    def get_last_capture(self) -> VoiceInput | None:
        """
        Return the most recent successful capture.
        """
        return self._last_capture

    def get_sample_rate(self) -> int:
        """Return the configured sample rate."""
        return self._sample_rate

    def get_channels(self) -> int:
        """Return the configured channel count."""
        return self._channels

    def get_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of capture metadata."""
        return dict(self._metadata)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set capture metadata."""
        if not isinstance(key, str) or not key.strip():
            raise ValueError("metadata key must be a non-empty string")

        self._metadata[key] = value

    def _set_last_capture(self, voice_input: VoiceInput) -> None:
        """
        Store the most recent successful capture.

        Intended for subclasses.
        """
        if not isinstance(voice_input, VoiceInput):
            raise TypeError("voice_input must be a VoiceInput instance")

        self._last_capture = voice_input

    def reset_last_capture(self) -> None:
        """Clear the stored last capture."""
        self._last_capture = None