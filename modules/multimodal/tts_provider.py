"""
Ultron Text-to-Speech Provider.

v0.61 — Text-to-Speech Provider Abstraction

Defines the provider-independent contract for converting
text into synthesized audio.

Responsibilities:
- Define TTS provider identity
- Define supported audio formats
- Define supported voices/capabilities
- Manage provider configuration
- Manage provider metadata
- Validate text input
- Validate provider availability
- Define the abstract synthesis contract

The TTSProvider does NOT:
- Call external APIs
- Contain provider-specific logic
- Play audio
- Manage audio devices
- Own runtime orchestration
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Iterable, Set

from modules.multimodal.input_result import MultimodalInputResult


class TTSProviderError(Exception):
    """Base exception for TTS provider errors."""


class TTSProvider(ABC):
    """
    Provider-independent Text-to-Speech abstraction.

    A TTSProvider converts text into synthesized audio.

    Architecture:

        Text
          |
          v
      TTSProvider
          |
          v
    Concrete TTS Provider
          |
          v
      Audio Result

    Provider-specific implementations must implement
    ``synthesize()``.
    """

    def __init__(
        self,
        *,
        name: str,
        supported_formats: Iterable[str] | None = None,
        capabilities: Iterable[str] | None = None,
        voices: Iterable[str] | None = None,
        configuration: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self._validate_name(name)

        self._name = name.strip()

        self._supported_formats = self._normalize_string_set(
            supported_formats,
            field_name="supported_formats",
        )

        self._capabilities = self._normalize_string_set(
            capabilities,
            field_name="capabilities",
        )

        self._voices = self._normalize_string_set(
            voices,
            field_name="voices",
        )

        self._configuration = self._validate_dictionary(
            configuration,
            field_name="configuration",
        )

        self._metadata = self._validate_dictionary(
            metadata,
            field_name="metadata",
        )

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(name, str):
            raise TypeError(
                "name must be a string."
            )

        if not name.strip():
            raise ValueError(
                "name cannot be empty."
            )

    @staticmethod
    def _validate_dictionary(
        value: Dict[str, Any] | None,
        *,
        field_name: str,
    ) -> Dict[str, Any]:
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise TypeError(
                f"{field_name} must be a dictionary."
            )

        return deepcopy(value)

    @staticmethod
    def _normalize_string_set(
        values: Iterable[str] | None,
        *,
        field_name: str,
    ) -> Set[str]:
        if values is None:
            return set()

        if isinstance(values, str):
            raise TypeError(
                f"{field_name} must be an iterable of strings, "
                "not a single string."
            )

        try:
            normalized = set(values)
        except TypeError as exc:
            raise TypeError(
                f"{field_name} must be an iterable of strings."
            ) from exc

        for value in normalized:
            if not isinstance(value, str):
                raise TypeError(
                    f"All values in {field_name} must be strings."
                )

            if not value.strip():
                raise ValueError(
                    f"Values in {field_name} cannot be empty."
                )

        return {
            value.strip().lower()
            for value in normalized
        }

    @staticmethod
    def _validate_text(text: str) -> None:
        if not isinstance(text, str):
            raise TypeError(
                "text must be a string."
            )

        if not text.strip():
            raise ValueError(
                "text cannot be empty."
            )

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str):
            raise TypeError(
                "key must be a string."
            )

        if not key.strip():
            raise ValueError(
                "key cannot be empty."
            )

    # ========================================================
    # Identity
    # ========================================================

    def get_name(self) -> str:
        """Return the provider name."""
        return self._name

    # ========================================================
    # Audio Formats
    # ========================================================

    def supports_format(
        self,
        audio_format: str,
    ) -> bool:
        """Return whether the provider supports an audio format."""

        if not isinstance(audio_format, str):
            raise TypeError(
                "audio_format must be a string."
            )

        if not audio_format.strip():
            raise ValueError(
                "audio_format cannot be empty."
            )

        return (
            audio_format.strip().lower()
            in self._supported_formats
        )

    def get_supported_formats(self) -> Set[str]:
        """Return a defensive copy of supported audio formats."""
        return set(self._supported_formats)

    # ========================================================
    # Capabilities
    # ========================================================

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        """Return whether the provider supports a capability."""

        if not isinstance(capability, str):
            raise TypeError(
                "capability must be a string."
            )

        if not capability.strip():
            raise ValueError(
                "capability cannot be empty."
            )

        return (
            capability.strip().lower()
            in self._capabilities
        )

    def get_capabilities(self) -> Set[str]:
        """Return a defensive copy of provider capabilities."""
        return set(self._capabilities)

    # ========================================================
    # Voices
    # ========================================================

    def supports_voice(
        self,
        voice: str,
    ) -> bool:
        """Return whether the provider supports a voice."""

        if not isinstance(voice, str):
            raise TypeError(
                "voice must be a string."
            )

        if not voice.strip():
            raise ValueError(
                "voice cannot be empty."
            )

        return (
            voice.strip().lower()
            in self._voices
        )

    def get_voices(self) -> Set[str]:
        """Return a defensive copy of supported voices."""
        return set(self._voices)

    # ========================================================
    # Configuration
    # ========================================================

    def set_configuration(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a provider configuration value."""

        self._validate_key(key)

        self._configuration[key] = deepcopy(value)

    def get_configuration(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return a configuration value."""

        self._validate_key(key)

        return deepcopy(
            self._configuration.get(
                key,
                default,
            )
        )

    def get_all_configuration(self) -> Dict[str, Any]:
        """Return all provider configuration."""
        return deepcopy(self._configuration)

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set provider metadata."""

        self._validate_key(key)

        self._metadata[key] = deepcopy(value)

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Return provider metadata."""

        self._validate_key(key)

        return deepcopy(
            self._metadata.get(
                key,
                default,
            )
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return all provider metadata."""
        return deepcopy(self._metadata)

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the provider is currently available.

        Base implementation assumes availability.
        Concrete providers may override this.
        """

        return True

    def validate_availability(self) -> None:
        """Raise an error when the provider is unavailable."""

        if not self.is_available():
            raise TTSProviderError(
                f"TTS provider '{self.get_name()}' "
                "is currently unavailable."
            )

    # ========================================================
    # Text Validation
    # ========================================================

    def validate_text(
        self,
        text: str,
    ) -> None:
        """Validate text before synthesis."""

        self._validate_text(text)

    # ========================================================
    # Synthesis
    # ========================================================

    @abstractmethod
    def synthesize(
        self,
        text: str,
    ) -> MultimodalInputResult:
        """
        Convert text into synthesized audio.

        Concrete providers must implement this method.

        The returned MultimodalInputResult should contain
        the synthesized audio representation in ``data``.
        """

        raise NotImplementedError

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"supported_formats="
            f"{sorted(self._supported_formats)!r}, "
            f"capabilities="
            f"{sorted(self._capabilities)!r}, "
            f"voices="
            f"{sorted(self._voices)!r}"
            f")"
        )


__all__ = [
    "TTSProvider",
    "TTSProviderError",
]