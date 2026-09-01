"""
Ultron Voice Processor.

v0.53 — Voice Processing Foundation

Provides the processing abstraction for normalized voice
inputs entering the Ultron multimodal runtime.

This module intentionally does not implement a concrete
speech-to-text provider. It establishes the processing
boundary required for future STT integrations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Dict

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import (
    VoiceInput,
    VoiceInputError,
)


class VoiceProcessorError(Exception):
    """Base exception for voice processor errors."""


class VoiceProcessor(ABC):
    """
    Abstract foundation for voice input processing.

    VoiceProcessor defines the contract between the
    VoiceInput layer and future speech-processing or
    speech-to-text providers.

    Architecture:

        VoiceInput
             |
             v
        VoiceProcessor
             |
             +---- Future STT Provider
             |
             v
        MultimodalInputResult
    """

    def __init__(
        self,
        *,
        name: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize a voice processor.

        Parameters:
            name:
                Optional processor name.

            metadata:
                Optional processor metadata.
        """

        if name is not None:
            if not isinstance(name, str):
                raise VoiceProcessorError(
                    "name must be a string or None."
                )

            if not name.strip():
                raise VoiceProcessorError(
                    "name cannot be empty."
                )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise VoiceProcessorError(
                "metadata must be a dictionary or None."
            )

        self.name = name
        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    # ========================================================
    # Processing Contract
    # ========================================================

    @abstractmethod
    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Process a VoiceInput.

        Concrete implementations must return a
        MultimodalInputResult.
        """

        raise NotImplementedError

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def validate_input(
        voice_input: VoiceInput,
    ) -> None:
        """
        Validate a voice input before processing.
        """

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            raise VoiceProcessorError(
                "voice_input must be a VoiceInput instance."
            )

        if not voice_input.is_valid():
            raise VoiceProcessorError(
                "voice_input is invalid."
            )

    # ========================================================
    # Result Helpers
    # ========================================================

    @staticmethod
    def create_processing_result(
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Create a processing-state result.
        """

        VoiceProcessor.validate_input(
            voice_input
        )

        return MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=InputType.VOICE,
            status="processing",
        )

    @staticmethod
    def create_success_result(
        voice_input: VoiceInput,
        data: Any = None,
    ) -> MultimodalInputResult:
        """
        Create a successful voice processing result.
        """

        VoiceProcessor.validate_input(
            voice_input
        )

        result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=InputType.VOICE,
            status="processing",
        )

        result.complete(
            data
        )

        return result

    @staticmethod
    def create_failure_result(
        voice_input: VoiceInput,
        error: str,
    ) -> MultimodalInputResult:
        """
        Create a failed voice processing result.
        """

        VoiceProcessor.validate_input(
            voice_input
        )

        if not isinstance(error, str):
            raise VoiceProcessorError(
                "error must be a string."
            )

        if not error.strip():
            raise VoiceProcessorError(
                "error cannot be empty."
            )

        result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=InputType.VOICE,
            status="processing",
        )

        result.fail(
            error
        )

        return result

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set processor metadata."""

        if not isinstance(
            key,
            str,
        ):
            raise VoiceProcessorError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessorError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve processor metadata."""

        if not isinstance(
            key,
            str,
        ):
            raise VoiceProcessorError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessorError(
                "Metadata key cannot be empty."
            )

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of processor metadata."""

        return deepcopy(
            self.metadata
        )

    # ========================================================
    # Processor Identity
    # ========================================================

    def get_name(self) -> str | None:
        """Return the processor name."""

        return self.name

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}"
            ")"
        )


__all__ = [
    "VoiceProcessor",
    "VoiceProcessorError",
]