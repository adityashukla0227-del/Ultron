"""
Ultron Audio Output Device Manager

v0.67 — Audio Output Device Integration

Provides provider- and operating-system-independent
management of audio output devices.

Responsibilities:
- Register output devices
- Remove output devices
- Discover registered devices
- Lookup devices by ID
- Select an active output device
- Manage the default output device
- Validate device selection
- Maintain device metadata

This module does NOT:
- Communicate with hardware
- Perform actual device discovery through an OS API
- Play audio
- Perform TTS synthesis
- Perform STT
- Execute agents or tools
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from modules.multimodal.audio_output_device import (
    AudioOutputDevice,
    AudioOutputDeviceError,
)


class AudioOutputDeviceManagerError(Exception):
    """Base exception for output-device manager errors."""


class AudioOutputDeviceManager:
    """
    Registry and selection manager for audio output devices.

    The manager intentionally does not discover hardware itself.
    Concrete integrations can populate it with discovered devices.
    """

    def __init__(
        self,
        *,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise AudioOutputDeviceManagerError(
                "metadata must be a dictionary or None."
            )

        self._devices: Dict[
            str,
            AudioOutputDevice,
        ] = {}

        self._active_device_id: str | None = None

        self._metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    def register_device(
        self,
        device: AudioOutputDevice,
    ) -> None:
        """Register an output device."""
        if not isinstance(
            device,
            AudioOutputDevice,
        ):
            raise AudioOutputDeviceManagerError(
                "device must be an AudioOutputDevice instance."
            )

        device_id = device.get_device_id()

        if device_id in self._devices:
            raise AudioOutputDeviceManagerError(
                f"Device already registered: {device_id}"
            )

        self._devices[device_id] = device

        if (
            self._active_device_id is None
            and device.is_default()
            and device.is_available()
        ):
            self._active_device_id = device_id

    def unregister_device(
        self,
        device_id: str,
    ) -> None:
        """Remove a registered output device."""
        self._validate_device_id(device_id)

        if device_id not in self._devices:
            raise AudioOutputDeviceManagerError(
                f"Device not registered: {device_id}"
            )

        del self._devices[device_id]

        if self._active_device_id == device_id:
            self._active_device_id = None

    def has_device(
        self,
        device_id: str,
    ) -> bool:
        """Return whether a device is registered."""
        self._validate_device_id(device_id)
        return device_id in self._devices

    def get_device(
        self,
        device_id: str,
    ) -> AudioOutputDevice:
        """Return a registered device by ID."""
        self._validate_device_id(device_id)

        try:
            return self._devices[device_id]
        except KeyError as exc:
            raise AudioOutputDeviceManagerError(
                f"Device not registered: {device_id}"
            ) from exc

    def get_devices(self) -> list[AudioOutputDevice]:
        """Return all registered devices."""
        return list(self._devices.values())

    def get_available_devices(
        self,
    ) -> list[AudioOutputDevice]:
        """Return all currently available devices."""
        return [
            device
            for device in self._devices.values()
            if device.is_available()
        ]

    def get_default_device(
        self,
    ) -> AudioOutputDevice | None:
        """Return the registered default device."""
        for device in self._devices.values():
            if device.is_default():
                return device

        return None

    def get_active_device(
        self,
    ) -> AudioOutputDevice | None:
        """Return the currently selected device."""
        if self._active_device_id is None:
            return None

        return self._devices.get(
            self._active_device_id
        )

    def get_active_device_id(
        self,
    ) -> str | None:
        """Return the active device ID."""
        return self._active_device_id

    def set_active_device(
        self,
        device_id: str,
    ) -> None:
        """Select a registered available device."""
        self._validate_device_id(device_id)

        device = self.get_device(device_id)

        if not device.is_available():
            raise AudioOutputDeviceManagerError(
                f"Device is unavailable: {device_id}"
            )

        self._active_device_id = device_id

    def set_default_device(
        self,
        device_id: str,
    ) -> None:
        """
        Mark a registered device as default.

        Only one registered device can be marked as default.
        """
        self._validate_device_id(device_id)

        target = self.get_device(device_id)

        for device in self._devices.values():
            device.set_default(
                device.get_device_id()
                == device_id
            )

        if target.is_available():
            self._active_device_id = device_id

    def clear_active_device(self) -> None:
        """Clear the active device selection."""
        self._active_device_id = None

    def clear_devices(self) -> None:
        """Remove all registered devices."""
        self._devices.clear()
        self._active_device_id = None

    def count(self) -> int:
        """Return the number of registered devices."""
        return len(self._devices)

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set manager metadata."""
        if not isinstance(key, str) or not key.strip():
            raise AudioOutputDeviceManagerError(
                "metadata key must be a non-empty string."
            )

        self._metadata[key.strip()] = value

    def get_metadata(self) -> Dict[str, Any]:
        """Return defensive manager metadata."""
        return deepcopy(self._metadata)

    def get_metadata_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return a manager metadata value."""
        if not isinstance(key, str) or not key.strip():
            raise AudioOutputDeviceManagerError(
                "metadata key must be a non-empty string."
            )

        return self._metadata.get(
            key.strip(),
            default,
        )

    def clear_metadata(self) -> None:
        """Clear manager metadata."""
        self._metadata.clear()

    @staticmethod
    def _validate_device_id(
        device_id: str,
    ) -> None:
        if not isinstance(device_id, str) or not device_id.strip():
            raise AudioOutputDeviceManagerError(
                "device_id must be a non-empty string."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize manager state."""
        return {
            "devices": [
                device.to_dict()
                for device in self._devices.values()
            ],
            "active_device_id": self._active_device_id,
            "metadata": self.get_metadata(),
        }

    def __repr__(self) -> str:
        return (
            "AudioOutputDeviceManager("
            f"devices={self.count()}, "
            f"active_device_id="
            f"{self._active_device_id!r}"
            ")"
        )


__all__ = [
    "AudioOutputDeviceManager",
    "AudioOutputDeviceManagerError",
]