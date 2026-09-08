"""
Voice Response Executor.

Ultron v0.64 — Voice Response Execution

Executes runtime-generated text responses through the
TTS runtime integration layer.

Responsibilities:
- Accept runtime execution responses
- Resolve response text
- Delegate text synthesis to TTSRuntimeIntegration
- Preserve synthesized MultimodalInputResult
- Attach execution/runtime metadata
- Provide safe voice response execution

This module does NOT:
- Perform TTS provider-specific logic
- Select TTS providers
- Play audio
- Manage audio devices
- Perform STT
- Execute agents or tools
- Control agent execution lifecycle
- Implement the full conversation loop
"""

from __future__ import annotations

from typing import Any, Dict

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.tts_runtime_integration import (
    TTSRuntimeIntegration,
    TTSRuntimeIntegrationError,
)


class VoiceResponseExecutionError(Exception):
    """Raised when voice response execution fails."""


class VoiceResponseExecutor:
    """
    Executes runtime text responses as synthesized voice responses.

    The executor remains independent from concrete TTS providers
    and delegates synthesis to TTSRuntimeIntegration.
    """

    EXECUTOR_NAME = "voice-response-executor"

    def __init__(
        self,
        *,
        tts_integration: TTSRuntimeIntegration,
    ) -> None:
        if not isinstance(
            tts_integration,
            TTSRuntimeIntegration,
        ):
            raise VoiceResponseExecutionError(
                "tts_integration must be an instance "
                "of TTSRuntimeIntegration."
            )

        self._tts_integration = tts_integration

    def get_tts_integration(
        self,
    ) -> TTSRuntimeIntegration:
        """
        Return the configured TTS runtime integration.
        """

        return self._tts_integration

    def is_available(self) -> bool:
        """
        Return whether the configured TTS system is available.
        """

        return self._tts_integration.is_available()

    def validate_response_text(
        self,
        text: str,
    ) -> None:
        """
        Validate runtime response text.
        """

        if not isinstance(text, str):
            raise VoiceResponseExecutionError(
                "response text must be a string."
            )

        if not text.strip():
            raise VoiceResponseExecutionError(
                "response text cannot be empty."
            )

    def execute(
        self,
        response_text: str,
        *,
        runtime_context_id: str | None = None,
        execution_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> MultimodalInputResult:
        """
        Execute a runtime text response as synthesized audio.
        """

        self.validate_response_text(
            response_text
        )

        try:
            result = self._tts_integration.synthesize(
                response_text,
                runtime_context_id=runtime_context_id,
                execution_id=execution_id,
                metadata=metadata,
            )

        except TTSRuntimeIntegrationError:
            raise

        except Exception as exc:
            raise VoiceResponseExecutionError(
                str(exc)
            ) from exc

        if not isinstance(
            result,
            MultimodalInputResult,
        ):
            raise VoiceResponseExecutionError(
                "TTS runtime integration returned "
                "an invalid result."
            )

        result.set_metadata(
            "executor",
            self.EXECUTOR_NAME,
        )

        result.set_metadata(
            "response_text",
            response_text,
        )

        return result

    def execute_safe(
        self,
        response_text: str,
        *,
        runtime_context_id: str | None = None,
        execution_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> MultimodalInputResult:
        """
        Safely execute a runtime text response.

        Failures are converted into a structured
        MultimodalInputResult.
        """

        try:
            return self.execute(
                response_text,
                runtime_context_id=runtime_context_id,
                execution_id=execution_id,
                metadata=metadata,
            )

        except Exception as exc:
            result = MultimodalInputResult(
                input_id="voice-response-input",
                input_type="text",
            )

            result.fail(
                error=str(exc)
            )

            result.set_metadata(
                "executor",
                self.EXECUTOR_NAME,
            )

            result.set_metadata(
                "response_text",
                response_text,
            )

            return result

    def __repr__(self) -> str:
        return (
            f"VoiceResponseExecutor("
            f"executor={self.EXECUTOR_NAME!r}"
            f")"
        )


__all__ = [
    "VoiceResponseExecutor",
    "VoiceResponseExecutionError",
]