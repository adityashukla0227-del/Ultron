"""
Ultron Audio Output Device

v0.67 — Audio Output Device Integration

Defines the provider- and operating-system-independent
representation of an audio output device.

Responsibilities:
- Represent an output device
- Store device identity
- Store device capabilities
- Track availability
- Track default-device state
- Maintain device metadata
- Validate device configuration

This module does NOT:
- Open or control hardware directly
- Perform audio playback
- Depend on a specific audio library
- Manage operating-system APIs
- Perform TTS synthesis
- Perform STT
- Execute agents or tools
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class AudioOutputDeviceError(Exception):
    """Base exception for audio output device errors."""


class AudioOutputDevice:
    """
    Representation of an audio output device.

    AudioOutputDevice is intentionally independent from
    any concrete operating-system or audio backend.

    Example:

        device = AudioOutputDevice(
            device_id="default",
            name="Default Speaker",
            device_type="speaker",
            available=True,
            is_default=True,
        )
    """

    DEVICE_TYPE_SPEAKER = "speaker"
    DEVICE_TYPE_HEADPHONES = "headphones"
    DEVICE_TYPE_HEADSET = "headset"
    DEVICE_TYPE_HDMI = "hdmi"
    DEVICE_TYPE_BLUETOOTH = "bluetooth"
    DEVICE_TYPE_VIRTUAL = "virtual"
    DEVICE_TYPE_UNKNOWN = "unknown"

    VALID_DEVICE_TYPES = {
        DEVICE_TYPE_SPEAKER,
        DEVICE_TYPE_HEADPHONES,
        DEVICE_TYPE_HEADSET,
        DEVICE_TYPE_HDMI,
        DEVICE_TYPE_BLUETOOTH,
        DEVICE_TYPE_VIRTUAL,
        DEVICE_TYPE_UNKNOWN,
    }

    def __init__(
        self,
        *,
        device_id: str,
        name: str,
        device_type: str = DEVICE_TYPE_UNKNOWN,
        available: bool = True,
        is_default: bool = False,
        sample_rates: list[int] | None = None,
        supported_formats: list[str] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self._validate_device_id(device_id)
        self._validate_name(name)
        normalized_type = self._validate_device_type(device_type)

        if not isinstance(available, bool):
            raise AudioOutputDeviceError(
                "available must be a boolean."
            )

        if not isinstance(is_default, bool):
            raise AudioOutputDeviceError(
                "is_default must be a boolean."
            )

        self._device_id = device_id.strip()
        self._name = name.strip()
        self._device_type = normalized_type
        self._available = available
        self._is_default = is_default

        self._sample_rates = self._validate_sample_rates(
            sample_rates
        )

        self._supported_formats = (
            self._validate_supported_formats(
                supported_formats
            )
        )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise AudioOutputDeviceError(
                "metadata must be a dictionary or None."
            )

        self._metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    @staticmethod
    def _validate_device_id(
        device_id: str,
    ) -> None:
        if not isinstance(device_id, str) or not device_id.strip():
            raise AudioOutputDeviceError(
                "device_id must be a non-empty string."
            )

    @staticmethod
    def _validate_name(
        name: str,
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise AudioOutputDeviceError(
                "name must be a non-empty string."
            )

    @classmethod
    def _validate_device_type(
        cls,
        device_type: str,
    ) -> str:
        if not isinstance(device_type, str):
            raise AudioOutputDeviceError(
                "device_type must be a string."
            )

        normalized = device_type.strip().lower()

        if normalized not in cls.VALID_DEVICE_TYPES:
            raise AudioOutputDeviceError(
                f"Invalid device type: {device_type}"
            )

        return normalized

    @staticmethod
    def _validate_sample_rates(
        sample_rates: list[int] | None,
    ) -> list[int]:
        if sample_rates is None:
            return []

        if not isinstance(sample_rates, list):
            raise AudioOutputDeviceError(
                "sample_rates must be a list or None."
            )

        validated: list[int] = []

        for rate in sample_rates:
            if not isinstance(rate, int) or rate <= 0:
                raise AudioOutputDeviceError(
                    "sample_rates must contain positive integers."
                )

            if rate not in validated:
                validated.append(rate)

        return validated

    @staticmethod
    def _validate_supported_formats(
        supported_formats: list[str] | None,
    ) -> list[str]:
        if supported_formats is None:
            return []

        if not isinstance(supported_formats, list):
            raise AudioOutputDeviceError(
                "supported_formats must be a list or None."
            )

        validated: list[str] = []

        for audio_format in supported_formats:
            if (
                not isinstance(audio_format, str)
                or not audio_format.strip()
            ):
                raise AudioOutputDeviceError(
                    "supported_formats must contain "
                    "non-empty strings."
                )

            normalized = audio_format.strip().lower()

            if normalized not in validated:
                validated.append(normalized)

        return validated

    def get_device_id(self) -> str:
        """Return the unique device identifier."""
        return self._device_id

    def get_name(self) -> str:
        """Return the human-readable device name."""
        return self._name

    def get_device_type(self) -> str:
        """Return the normalized device type."""
        return self._device_type

    def is_available(self) -> bool:
        """Return whether the device is currently available."""
        return self._available

    def is_default(self) -> bool:
        """Return whether this device is marked as default."""
        return self._is_default

    def set_available(
        self,
        available: bool,
    ) -> None:
        """Update device availability."""
        if not isinstance(available, bool):
            raise AudioOutputDeviceError(
                "available must be a boolean."
            )

        self._available = available

    def set_default(
        self,
        is_default: bool,
    ) -> None:
        """Update default-device state."""
        if not isinstance(is_default, bool):
            raise AudioOutputDeviceError(
                "is_default must be a boolean."
            )

        self._is_default = is_default

    def get_sample_rates(self) -> list[int]:
        """Return supported sample rates."""
        return list(self._sample_rates)

    def supports_sample_rate(
        self,
        sample_rate: int,
    ) -> bool:
        """Return whether the device supports a sample rate."""
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            raise AudioOutputDeviceError(
                "sample_rate must be a positive integer."
            )

        return sample_rate in self._sample_rates

    def get_supported_formats(self) -> list[str]:
        """Return supported audio formats."""
        return list(self._supported_formats)

    def supports_format(
        self,
        audio_format: str,
    ) -> bool:
        """Return whether the device supports an audio format."""
        if (
            not isinstance(audio_format, str)
            or not audio_format.strip()
        ):
            raise AudioOutputDeviceError(
                "audio_format must be a non-empty string."
            )

        return (
            audio_format.strip().lower()
            in self._supported_formats
        )

    def get_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of metadata."""
        return deepcopy(self._metadata)

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set device metadata."""
        if not isinstance(key, str) or not key.strip():
            raise AudioOutputDeviceError(
                "metadata key must be a non-empty string."
            )

        self._metadata[key.strip()] = value

    def get_metadata_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return a metadata value."""
        if not isinstance(key, str) or not key.strip():
            raise AudioOutputDeviceError(
                "metadata key must be a non-empty string."
            )

        return self._metadata.get(
            key.strip(),
            default,
        )

    def clear_metadata(self) -> None:
        """Clear all device metadata."""
        self._metadata.clear()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the device configuration."""
        return {
            "device_id": self._device_id,
            "name": self._name,
            "device_type": self._device_type,
            "available": self._available,
            "is_default": self._is_default,
            "sample_rates": self.get_sample_rates(),
            "supported_formats": self.get_supported_formats(),
            "metadata": self.get_metadata(),
        }

    def __repr__(self) -> str:
        return (
            "AudioOutputDevice("
            f"device_id={self._device_id!r}, "
            f"name={self._name!r}, "
            f"device_type={self._device_type!r}, "
            f"available={self._available!r}, "
            f"is_default={self._is_default!r}"
            ")"
        )


__all__ = [
    "AudioOutputDevice",
    "AudioOutputDeviceError",
]