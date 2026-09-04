"""
Voice → Runtime Integration.

Ultron v0.58 — Voice → Text Runtime Integration

Connects the voice processing pipeline with the
AgentRuntimeContext.

Architecture:

    VoiceInput
        ↓
    VoiceProcessingPipeline
        ↓
    VoiceProcessor
        ↓
    STTProvider
        ↓
    MultimodalInputResult
        ↓
    VoiceRuntimeIntegration
        ↓
    AgentRuntimeContext.query
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.agent.agent_runtime_context import (
    AgentRuntimeContext,
    AgentRuntimeContextError,
)
from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processing_pipeline import (
    VoiceProcessingPipeline,
    VoiceProcessingPipelineError,
)


class VoiceRuntimeIntegrationError(Exception):
    """Raised when voice-to-runtime integration fails."""


class VoiceRuntimeIntegration:
    """
    Integrate voice processing with AgentRuntimeContext.

    This component is responsible only for transferring a
    successful voice transcription into the runtime query.

    It does not:
    - execute commands,
    - execute tools,
    - create plans,
    - control execution lifecycle,
    - perform STT directly.
    """

    def __init__(
        self,
        *,
        pipeline: VoiceProcessingPipeline,
        context: AgentRuntimeContext,
        name: str = "voice-runtime-integration",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not isinstance(
            pipeline,
            VoiceProcessingPipeline,
        ):
            raise VoiceRuntimeIntegrationError(
                "pipeline must be a VoiceProcessingPipeline instance."
            )

        if not isinstance(
            context,
            AgentRuntimeContext,
        ):
            raise VoiceRuntimeIntegrationError(
                "context must be an AgentRuntimeContext instance."
            )

        if not isinstance(
            name,
            str,
        ) or not name.strip():
            raise VoiceRuntimeIntegrationError(
                "name must be a non-empty string."
            )

        self._pipeline = pipeline
        self._context = context
        self._name = name.strip()
        self._metadata = dict(
            metadata or {}
        )

    # ========================================================
    # Integration
    # ========================================================

    def process_voice(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Process voice input and update the runtime query.

        Returns the result produced by the voice processing
        pipeline.
        """

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            raise VoiceRuntimeIntegrationError(
                "voice_input must be a VoiceInput instance."
            )

        try:
            result = self._pipeline.process(
                voice_input
            )

        except VoiceProcessingPipelineError:
            raise

        except Exception as exc:
            raise VoiceRuntimeIntegrationError(
                str(exc)
            ) from exc

        if not isinstance(
            result,
            MultimodalInputResult,
        ):
            raise VoiceRuntimeIntegrationError(
                "Voice processing pipeline returned an invalid result."
            )

        if not result.is_successful():
            return result

        text = result.get_data()

        if not isinstance(
            text,
            str,
        ):
            result.fail(
                error=(
                    "Voice processing result "
                    "does not contain text data."
                )
            )

            return result

        text = text.strip()

        if not text:
            result.fail(
                error="Voice processing returned empty text."
            )

            return result

        try:
            self._context.set_query(
                text
            )

        except AgentRuntimeContextError as exc:
            result.fail(
                error=str(exc)
            )

            return result

        self._context.set_status(
            "ready"
        )

        result.set_metadata(
            "runtime_context_id",
            self._context.id,
        )

        result.set_metadata(
            "runtime_query",
            text,
        )

        result.set_metadata(
            "integration",
            self.get_name(),
        )

        for key, value in self._metadata.items():
            result.set_metadata(
                key,
                value,
            )

        return result

    # ========================================================
    # Context
    # ========================================================

    def get_context(
        self,
    ) -> AgentRuntimeContext:
        """
        Return the active runtime context.
        """

        return self._context

    def set_context(
        self,
        context: AgentRuntimeContext,
    ) -> None:
        """
        Replace the active runtime context.
        """

        if not isinstance(
            context,
            AgentRuntimeContext,
        ):
            raise VoiceRuntimeIntegrationError(
                "context must be an AgentRuntimeContext instance."
            )

        self._context = context

    # ========================================================
    # Pipeline
    # ========================================================

    def get_pipeline(
        self,
    ) -> VoiceProcessingPipeline:
        """
        Return the configured voice processing pipeline.
        """

        return self._pipeline

    def set_pipeline(
        self,
        pipeline: VoiceProcessingPipeline,
    ) -> None:
        """
        Replace the configured voice processing pipeline.
        """

        if not isinstance(
            pipeline,
            VoiceProcessingPipeline,
        ):
            raise VoiceRuntimeIntegrationError(
                "pipeline must be a VoiceProcessingPipeline instance."
            )

        self._pipeline = pipeline

    # ========================================================
    # Metadata
    # ========================================================

    def get_name(self) -> str:
        """
        Return the integration component name.
        """

        return self._name

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store integration metadata.
        """

        if not isinstance(
            key,
            str,
        ) or not key.strip():
            raise VoiceRuntimeIntegrationError(
                "Metadata key must be a non-empty string."
            )

        self._metadata[key.strip()] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve integration metadata.
        """

        if not isinstance(
            key,
            str,
        ) or not key.strip():
            raise VoiceRuntimeIntegrationError(
                "Metadata key must be a non-empty string."
            )

        return self._metadata.get(
            key.strip(),
            default,
        )

    def get_all_metadata(
        self,
    ) -> Dict[str, Any]:
        """
        Return a copy of integration metadata.
        """

        return dict(
            self._metadata
        )


__all__ = [
    "VoiceRuntimeIntegration",
    "VoiceRuntimeIntegrationError",
]