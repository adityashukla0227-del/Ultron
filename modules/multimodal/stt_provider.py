"""
Ultron STT Provider Abstraction.

v0.56 — STT Provider Abstraction

Defines the provider-agnostic contract for speech-to-text
providers used by the Ultron voice processing architecture.

This module intentionally does not implement a concrete STT
provider or perform any external API calls.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict, Iterable, Set

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.voice_input import VoiceInput


class STTProviderError(Exception):
    """Base exception for STT provider errors."""


class STTProvider(ABC):
    """
    Abstract speech-to-text provider.

    STTProvider defines the provider-independent contract that
    concrete speech-to-text implementations must follow.

    Architecture:

        VoiceInput
             |
             v
        STTProvider
             |
             v
    MultimodalInputResult

    Concrete providers can later implement this abstraction
    without coupling provider-specific logic to the runtime.
    """

    def __init__(
        self,
        *,
        name: str,
        supported_formats: Iterable[str] | None = None,
        capabilities: Iterable[str] | None = None,
        configuration: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize an STT provider abstraction.

        Parameters:
            name:
                Human-readable provider name.

            supported_formats:
                Audio formats accepted by the provider.

            capabilities:
                Provider capability identifiers.

            configuration:
                Optional provider configuration.

            metadata:
                Optional provider metadata.
        """

        self._validate_name(name)

        normalized_formats = self._normalize_string_set(
            supported_formats,
            "supported_formats",
        )

        normalized_capabilities = self._normalize_string_set(
            capabilities,
            "capabilities",
        )

        self._validate_dictionary(
            configuration,
            "configuration",
        )

        self._validate_dictionary(
            metadata,
            "metadata",
        )

        self.name = name.strip()

        self.supported_formats: Set[str] = normalized_formats
        self.capabilities: Set[str] = normalized_capabilities

        self.configuration: Dict[str, Any] = deepcopy(
            configuration or {}
        )

        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate provider name."""

        if not isinstance(name, str):
            raise STTProviderError(
                "name must be a string."
            )

        if not name.strip():
            raise STTProviderError(
                "name cannot be empty."
            )

    @staticmethod
    def _validate_dictionary(
        value: Dict[str, Any] | None,
        field_name: str,
    ) -> None:
        """Validate an optional dictionary."""

        if value is not None and not isinstance(
            value,
            dict,
        ):
            raise STTProviderError(
                f"{field_name} must be a dictionary or None."
            )

    @staticmethod
    def _normalize_string_set(
        values: Iterable[str] | None,
        field_name: str,
    ) -> Set[str]:
        """
        Normalize a collection of strings into a set.
        """

        if values is None:
            return set()

        if isinstance(values, str):
            raise STTProviderError(
                f"{field_name} must be an iterable of strings."
            )

        try:
            normalized: Set[str] = set()

            for value in values:
                if not isinstance(value, str):
                    raise STTProviderError(
                        f"{field_name} must contain only strings."
                    )

                cleaned = value.strip().lower()

                if not cleaned:
                    raise STTProviderError(
                        f"{field_name} cannot contain empty values."
                    )

                normalized.add(cleaned)

            return normalized

        except TypeError as exc:
            raise STTProviderError(
                f"{field_name} must be an iterable of strings."
            ) from exc

    @staticmethod
    def _validate_voice_input(
        voice_input: VoiceInput,
    ) -> None:
        """Validate voice input before transcription."""

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            raise STTProviderError(
                "voice_input must be a VoiceInput instance."
            )

        if not voice_input.is_valid():
            raise STTProviderError(
                "voice_input is invalid."
            )

    # ========================================================
    # Provider Identity
    # ========================================================

    def get_name(self) -> str:
        """Return the provider name."""

        return self.name

    # ========================================================
    # Supported Formats
    # ========================================================

    def supports_format(
        self,
        audio_format: str,
    ) -> bool:
        """
        Return whether the provider supports an audio format.
        """

        if not isinstance(audio_format, str):
            raise STTProviderError(
                "audio_format must be a string."
            )

        normalized = audio_format.strip().lower()

        if not normalized:
            raise STTProviderError(
                "audio_format cannot be empty."
            )

        return normalized in self.supported_formats

    def get_supported_formats(self) -> Set[str]:
        """Return a defensive copy of supported formats."""

        return set(self.supported_formats)

    # ========================================================
    # Capabilities
    # ========================================================

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        """
        Return whether the provider supports a capability.
        """

        if not isinstance(capability, str):
            raise STTProviderError(
                "capability must be a string."
            )

        normalized = capability.strip().lower()

        if not normalized:
            raise STTProviderError(
                "capability cannot be empty."
            )

        return normalized in self.capabilities

    def get_capabilities(self) -> Set[str]:
        """Return a defensive copy of provider capabilities."""

        return set(self.capabilities)

    # ========================================================
    # Configuration
    # ========================================================

    def set_configuration(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a provider configuration value."""

        self._validate_key(
            key,
            "Configuration key",
        )

        self.configuration[key] = value

    def get_configuration(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve a provider configuration value."""

        self._validate_key(
            key,
            "Configuration key",
        )

        return self.configuration.get(
            key,
            default,
        )

    def get_all_configuration(self) -> Dict[str, Any]:
        """Return a defensive copy of provider configuration."""

        return deepcopy(
            self.configuration
        )

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set provider metadata."""

        self._validate_key(
            key,
            "Metadata key",
        )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve provider metadata."""

        self._validate_key(
            key,
            "Metadata key",
        )

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of provider metadata."""

        return deepcopy(
            self.metadata
        )

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the provider is available.

        The base abstraction assumes availability. Concrete
        providers can override this method to perform their
        own readiness checks.
        """

        return True

    def validate_availability(self) -> None:
        """
        Validate provider availability.

        Raises:
            STTProviderError:
                When the provider is unavailable.
        """

        if not self.is_available():
            raise STTProviderError(
                f"STT provider '{self.name}' is unavailable."
            )

    # ========================================================
    # Input Compatibility
    # ========================================================

    def validate_input(
        self,
        voice_input: VoiceInput,
    ) -> None:
        """
        Validate whether a VoiceInput can be processed.

        This validates the input itself and, when an audio
        format is available, validates provider compatibility.
        """

        self._validate_voice_input(
            voice_input
        )

        audio_format = voice_input.get_format()

        if (
            audio_format is not None
            and self.supported_formats
            and not self.supports_format(audio_format)
        ):
            raise STTProviderError(
                f"Unsupported audio format for provider "
                f"'{self.name}': {audio_format}"
            )

    # ========================================================
    # Transcription Contract
    # ========================================================

    @abstractmethod
    def transcribe(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Transcribe a VoiceInput.

        Concrete STT providers must implement this method and
        return a standardized MultimodalInputResult.

        No provider-specific implementation exists here.
        """

        raise NotImplementedError

    # ========================================================
    # Validation Helpers
    # ========================================================

    @staticmethod
    def _validate_key(
        key: str,
        label: str,
    ) -> None:
        """Validate configuration or metadata keys."""

        if not isinstance(key, str):
            raise STTProviderError(
                f"{label} must be a string."
            )

        if not key.strip():
            raise STTProviderError(
                f"{label} cannot be empty."
            )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"supported_formats="
            f"{sorted(self.supported_formats)!r}, "
            f"capabilities="
            f"{sorted(self.capabilities)!r}"
            ")"
        )


__all__ = [
    "STTProvider",
    "STTProviderError",
]