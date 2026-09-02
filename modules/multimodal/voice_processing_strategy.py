"""
Ultron Voice Processing Strategy.

v0.55 — Voice Processing Intelligence Foundation

Provides the provider-agnostic strategy abstraction for voice
processing.

This module intentionally does not implement a concrete speech-to-text
provider. It defines the contract and configuration boundary that
future voice-processing providers can implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.voice_input import VoiceInput


class VoiceProcessingStrategyError(Exception):
    """Base exception for voice processing strategy errors."""


class VoiceProcessingStrategy(ABC):
    """
    Abstract strategy for processing VoiceInput.

    The strategy owns the processing behavior contract while remaining
    independent from the VoiceProcessingPipeline.

    Architecture:

        VoiceInput
             |
             v
        VoiceProcessingStrategy
             |
             v
        MultimodalInputResult

    Concrete providers can implement this abstraction later without
    coupling provider-specific behavior to the pipeline.
    """

    def __init__(
        self,
        *,
        name: str,
        mode: str = "default",
        configuration: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the voice processing strategy.

        Parameters:
            name:
                Human-readable strategy name.

            mode:
                Processing mode identifier.

            configuration:
                Optional strategy configuration.

            metadata:
                Optional strategy metadata.
        """

        self._validate_name(name)
        self._validate_mode(mode)
        self._validate_dictionary(
            configuration,
            "configuration",
        )
        self._validate_dictionary(
            metadata,
            "metadata",
        )

        self.name = name.strip()
        self.mode = mode.strip()

        self.configuration: Dict[str, Any] = deepcopy(
            configuration or {}
        )

        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate strategy name."""

        if not isinstance(name, str):
            raise VoiceProcessingStrategyError(
                "name must be a string."
            )

        if not name.strip():
            raise VoiceProcessingStrategyError(
                "name cannot be empty."
            )

    @staticmethod
    def _validate_mode(mode: str) -> None:
        """Validate processing mode."""

        if not isinstance(mode, str):
            raise VoiceProcessingStrategyError(
                "mode must be a string."
            )

        if not mode.strip():
            raise VoiceProcessingStrategyError(
                "mode cannot be empty."
            )

    @staticmethod
    def _validate_dictionary(
        value: Dict[str, Any] | None,
        field_name: str,
    ) -> None:
        """Validate optional dictionary fields."""

        if value is not None and not isinstance(
            value,
            dict,
        ):
            raise VoiceProcessingStrategyError(
                f"{field_name} must be a dictionary or None."
            )

    @staticmethod
    def _validate_voice_input(
        voice_input: VoiceInput,
    ) -> None:
        """Validate voice input before processing."""

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            raise VoiceProcessingStrategyError(
                "voice_input must be a VoiceInput instance."
            )

        if not voice_input.is_valid():
            raise VoiceProcessingStrategyError(
                "voice_input is invalid."
            )

    # ------------------------------------------------------------------
    # Processing Contract
    # ------------------------------------------------------------------

    @abstractmethod
    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Process a VoiceInput.

        Concrete strategies must implement this method.
        """

        raise NotImplementedError

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return the strategy name."""

        return self.name

    def get_mode(self) -> str:
        """Return the processing mode."""

        return self.mode

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def set_configuration(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set a strategy configuration value."""

        if not isinstance(key, str):
            raise VoiceProcessingStrategyError(
                "Configuration key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingStrategyError(
                "Configuration key cannot be empty."
            )

        self.configuration[key] = value

    def get_configuration(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve a strategy configuration value."""

        if not isinstance(key, str):
            raise VoiceProcessingStrategyError(
                "Configuration key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingStrategyError(
                "Configuration key cannot be empty."
            )

        return self.configuration.get(
            key,
            default,
        )

    def get_all_configuration(self) -> Dict[str, Any]:
        """Return a defensive copy of strategy configuration."""

        return deepcopy(self.configuration)

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set strategy metadata."""

        if not isinstance(key, str):
            raise VoiceProcessingStrategyError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingStrategyError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve strategy metadata."""

        if not isinstance(key, str):
            raise VoiceProcessingStrategyError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingStrategyError(
                "Metadata key cannot be empty."
            )

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of strategy metadata."""

        return deepcopy(self.metadata)

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"mode={self.mode!r}"
            ")"
        )


__all__ = [
    "VoiceProcessingStrategy",
    "VoiceProcessingStrategyError",
]