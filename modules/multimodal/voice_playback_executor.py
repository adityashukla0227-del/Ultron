"""
Ultron Voice Playback Executor

v0.68 — Voice Playback Execution

Executes synthesized audio playback through the selected
audio output device.

Responsibilities:
- Validate synthesized audio
- Resolve active/default output device
- Validate output-device availability
- Execute playback through an injected playback backend
- Manage playback lifecycle state
- Track playback metadata
- Return structured playback results
- Handle playback failures safely

This module does NOT:
- Perform TTS synthesis
- Perform STT
- Discover physical devices
- Manage operating-system devices directly
- Select audio hardware through OS APIs
- Execute agents or tools
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict

from modules.multimodal.audio_output_device import AudioOutputDevice
from modules.multimodal.audio_output_device_manager import (
    AudioOutputDeviceManager,
    AudioOutputDeviceManagerError,
)
from modules.multimodal.audio_playback import (
    AudioPlayback,
    AudioPlaybackError,
)


class VoicePlaybackExecutorError(Exception):
    """Base exception for voice playback executor errors."""


class VoicePlaybackExecutor(AudioPlayback):
    """
    Concrete playback execution layer for synthesized voice output.

    VoicePlaybackExecutor integrates the existing AudioPlayback
    abstraction with AudioOutputDeviceManager.

    The actual playback implementation is supplied through an
    injectable playback backend.

    Expected backend contract:

        backend(audio, device)

    The backend is responsible only for delivering audio to the
    supplied device.

    Example:

        executor = VoicePlaybackExecutor(
            device_manager=device_manager,
            playback_backend=my_backend,
        )

        result = executor.execute(audio)
    """

    def __init__(
        self,
        *,
        device_manager: AudioOutputDeviceManager,
        playback_backend: Callable[
            [Any, AudioOutputDevice],
            Any,
        ],
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if not isinstance(
            device_manager,
            AudioOutputDeviceManager,
        ):
            raise VoicePlaybackExecutorError(
                "device_manager must be an "
                "AudioOutputDeviceManager instance."
            )

        if not callable(playback_backend):
            raise VoicePlaybackExecutorError(
                "playback_backend must be callable."
            )

        super().__init__(
            metadata=metadata,
        )

        self._device_manager = device_manager
        self._playback_backend = playback_backend
        self._last_device_id: str | None = None
        self._last_result: Dict[str, Any] | None = None

    def play(
        self,
        audio: Any,
    ) -> None:
        """
        Execute playback through the active output device.

        Raises:
            AudioPlaybackError:
                If audio validation, device resolution, or
                backend playback fails.
        """
        self._validate_audio(audio)

        device = self._resolve_output_device()

        self._set_status(
            self.STATUS_PLAYING
        )
        self._set_last_audio(audio)
        self._last_device_id = (
            device.get_device_id()
        )

        try:
            self._playback_backend(
                audio,
                device,
            )
        except Exception as exc:
            self._set_status(
                self.STATUS_FAILED
            )

            self._last_result = {
                "success": False,
                "status": self.STATUS_FAILED,
                "device_id": device.get_device_id(),
                "device_name": device.get_name(),
                "error": str(exc),
            }

            raise AudioPlaybackError(
                f"Audio playback failed: {exc}"
            ) from exc

        self._set_status(
            self.STATUS_STOPPED
        )

        self._last_result = {
            "success": True,
            "status": self.STATUS_STOPPED,
            "device_id": device.get_device_id(),
            "device_name": device.get_name(),
        }

    def execute(
        self,
        audio: Any,
    ) -> Dict[str, Any]:
        """
        Execute playback and return a structured result.

        Playback failures are converted into a failed result
        instead of propagating the exception.
        """
        try:
            self.play(audio)
        except (
            AudioPlaybackError,
            VoicePlaybackExecutorError,
        ) as exc:
            result = {
                "success": False,
                "status": self.STATUS_FAILED,
                "device_id": self._last_device_id,
                "error": str(exc),
            }

            self._last_result = result

            return deepcopy(result)

        return self.get_last_result()

    def stop(self) -> None:
        """
        Stop current playback.

        The backend may optionally expose a stop() method.
        """
        if self._status not in {
            self.STATUS_PLAYING,
            self.STATUS_PAUSED,
        }:
            self._set_status(
                self.STATUS_STOPPED
            )
            return

        stop_method = getattr(
            self._playback_backend,
            "stop",
            None,
        )

        if callable(stop_method):
            try:
                stop_method()
            except Exception as exc:
                self._set_status(
                    self.STATUS_FAILED
                )

                self._last_result = {
                    "success": False,
                    "status": self.STATUS_FAILED,
                    "device_id": self._last_device_id,
                    "error": str(exc),
                }

                raise AudioPlaybackError(
                    f"Audio stop failed: {exc}"
                ) from exc

        self._set_status(
            self.STATUS_STOPPED
        )

        if self._last_result is not None:
            self._last_result["status"] = (
                self.STATUS_STOPPED
            )

    def pause(self) -> None:
        """
        Pause current playback.

        The backend may optionally expose a pause() method.
        """
        if self._status != self.STATUS_PLAYING:
            raise AudioPlaybackError(
                "Playback must be playing before it can be paused."
            )

        pause_method = getattr(
            self._playback_backend,
            "pause",
            None,
        )

        if not callable(pause_method):
            raise AudioPlaybackError(
                "Playback backend does not support pause."
            )

        try:
            pause_method()
        except Exception as exc:
            self._set_status(
                self.STATUS_FAILED
            )

            raise AudioPlaybackError(
                f"Audio pause failed: {exc}"
            ) from exc

        self._set_status(
            self.STATUS_PAUSED
        )

    def resume(self) -> None:
        """
        Resume paused playback.

        The backend may optionally expose a resume() method.
        """
        if self._status != self.STATUS_PAUSED:
            raise AudioPlaybackError(
                "Playback must be paused before it can be resumed."
            )

        resume_method = getattr(
            self._playback_backend,
            "resume",
            None,
        )

        if not callable(resume_method):
            raise AudioPlaybackError(
                "Playback backend does not support resume."
            )

        try:
            resume_method()
        except Exception as exc:
            self._set_status(
                self.STATUS_FAILED
            )

            raise AudioPlaybackError(
                f"Audio resume failed: {exc}"
            ) from exc

        self._set_status(
            self.STATUS_PLAYING
        )

    def is_available(self) -> bool:
        """
        Return whether a usable output device is available.
        """
        return bool(
            self._resolve_output_device(
                raise_on_missing=False
            )
        )

    def get_device_info(self) -> Dict[str, Any]:
        """
        Return information about the active output device.
        """
        device = self._resolve_output_device()

        return device.to_dict()

    def get_device_manager(
        self,
    ) -> AudioOutputDeviceManager:
        """Return the configured output-device manager."""
        return self._device_manager

    def get_last_device_id(self) -> str | None:
        """Return the device used for the latest playback."""
        return self._last_device_id

    def get_last_result(self) -> Dict[str, Any]:
        """
        Return a defensive copy of the latest playback result.
        """
        return deepcopy(
            self._last_result
            or {
                "success": False,
                "status": self.get_status(),
                "device_id": self._last_device_id,
            }
        )

    def reset(self) -> None:
        """
        Reset playback execution state.
        """
        super().reset()

        self._last_device_id = None
        self._last_result = None

    def _resolve_output_device(
        self,
        *,
        raise_on_missing: bool = True,
    ) -> AudioOutputDevice | None:
        """
        Resolve the active output device.

        Selection order:

            1. Active device
            2. Default device
        """
        device = (
            self._device_manager.get_active_device()
        )

        if device is None:
            device = (
                self._device_manager.get_default_device()
            )

        if device is None:
            if raise_on_missing:
                raise VoicePlaybackExecutorError(
                    "No active or default output device is available."
                )

            return None

        if not device.is_available():
            if raise_on_missing:
                raise VoicePlaybackExecutorError(
                    "Selected output device is unavailable: "
                    f"{device.get_device_id()}"
                )

            return None

        return device

    def __repr__(self) -> str:
        return (
            "VoicePlaybackExecutor("
            f"status={self.get_status()!r}, "
            f"device_id={self._last_device_id!r}"
            ")"
        )


__all__ = [
    "VoicePlaybackExecutor",
    "VoicePlaybackExecutorError",
]