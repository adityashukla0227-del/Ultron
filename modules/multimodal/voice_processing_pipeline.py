"""
Ultron Voice Processing Pipeline.

v0.54 — Voice Processing Pipeline Foundation

Provides the orchestration boundary between VoiceInput,
VoiceProcessor, and the standardized MultimodalInputResult.

This module intentionally does not implement a concrete
speech-to-text provider. It coordinates voice processing
while keeping the processing pipeline provider-agnostic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processor import (
    VoiceProcessor,
)


class VoiceProcessingPipelineError(Exception):
    """Base exception for voice processing pipeline errors."""


class VoiceProcessingPipeline:
    """
    Orchestrates VoiceInput processing through a VoiceProcessor.

    Architecture:

        VoiceInput
             |
             v
        VoiceProcessor
             |
             v
        VoiceProcessingPipeline
             |
             v
        MultimodalInputResult
    """

    def __init__(
        self,
        processor: VoiceProcessor,
        *,
        name: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the voice processing pipeline.

        Parameters:
            processor:
                VoiceProcessor responsible for processing input.

            name:
                Optional pipeline name.

            metadata:
                Optional pipeline metadata.
        """

        self._validate_processor(processor)

        if name is not None:
            if not isinstance(name, str):
                raise VoiceProcessingPipelineError(
                    "name must be a string or None."
                )

            if not name.strip():
                raise VoiceProcessingPipelineError(
                    "name cannot be empty."
                )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise VoiceProcessingPipelineError(
                "metadata must be a dictionary or None."
            )

        self.processor = processor
        self.name = name
        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_processor(
        processor: VoiceProcessor,
    ) -> None:
        """Validate the configured voice processor."""

        if not isinstance(processor, VoiceProcessor):
            raise VoiceProcessingPipelineError(
                "processor must be a VoiceProcessor instance."
            )

    @staticmethod
    def _validate_voice_input(
        voice_input: VoiceInput,
    ) -> None:
        """Validate voice input before pipeline processing."""

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            raise VoiceProcessingPipelineError(
                "voice_input must be a VoiceInput instance."
            )

        if not voice_input.is_valid():
            raise VoiceProcessingPipelineError(
                "voice_input is invalid."
            )

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Process a VoiceInput through the configured processor.

        The pipeline owns orchestration and error isolation while
        the processor owns the actual voice-processing behavior.
        """

        self._validate_voice_input(voice_input)

        processing_result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=InputType.VOICE,
            status="processing",
        )

        try:
            result = self.processor.process(
                voice_input
            )

        except Exception as exc:
            processing_result.fail(str(exc))
            return processing_result

        if not isinstance(
            result,
            MultimodalInputResult,
        ):
            processing_result.fail(
                "VoiceProcessor returned an invalid result."
            )
            return processing_result

        return result

    # ------------------------------------------------------------------
    # Processor Management
    # ------------------------------------------------------------------

    def set_processor(
        self,
        processor: VoiceProcessor,
    ) -> None:
        """Replace the active voice processor."""

        self._validate_processor(processor)
        self.processor = processor

    def get_processor(self) -> VoiceProcessor:
        """Return the active voice processor."""

        return self.processor

    # ------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set pipeline metadata."""

        if not isinstance(key, str):
            raise VoiceProcessingPipelineError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingPipelineError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve pipeline metadata."""

        if not isinstance(key, str):
            raise VoiceProcessingPipelineError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceProcessingPipelineError(
                "Metadata key cannot be empty."
            )

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of pipeline metadata."""

        return deepcopy(self.metadata)

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    def get_name(self) -> str | None:
        """Return the pipeline name."""

        return self.name

    def get_processor_name(self) -> str | None:
        """Return the active processor name."""

        return self.processor.get_name()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"processor={self.processor!r}"
            ")"
        )


__all__ = [
    "VoiceProcessingPipeline",
    "VoiceProcessingPipelineError",
]