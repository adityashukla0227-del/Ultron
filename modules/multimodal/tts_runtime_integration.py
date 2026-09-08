"""
Runtime TTS Integration.

Ultron v0.63 — Runtime TTS Integration

Bridges Ultron runtime output with the provider-agnostic
TTSProvider abstraction.

Responsibilities:
- Accept runtime response text
- Validate response text
- Delegate synthesis to TTSProvider
- Preserve synthesized MultimodalInputResult
- Attach runtime integration metadata
- Keep TTS provider logic isolated from runtime orchestration

This module does NOT:
- Play audio
- Manage audio devices
- Execute agents or tools
- Perform speech recognition
- Control execution lifecycle
- Implement conversation loops
"""

from __future__ import annotations

from typing import Any, Dict

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.tts_provider import (
    TTSProvider,
    TTSProviderError,
)


class TTSRuntimeIntegrationError(Exception):
    """Raised when runtime TTS integration fails."""


class TTSRuntimeIntegration:
    """
    Runtime integration layer for text-to-speech.

    This class connects runtime-generated text with an
    already-configured TTSProvider.

    Provider selection and provider-specific synthesis
    remain outside this integration layer.
    """

    INTEGRATION_NAME = "tts-runtime-integration"

    def __init__(
        self,
        *,
        provider: TTSProvider,
    ) -> None:
        if not isinstance(
            provider,
            TTSProvider,
        ):
            raise TTSRuntimeIntegrationError(
                "provider must be an instance of TTSProvider."
            )

        self._provider = provider

    def get_provider(self) -> TTSProvider:
        """
        Return the configured TTS provider.
        """

        return self._provider

    def is_available(self) -> bool:
        """
        Return whether the configured provider is available.
        """

        return self._provider.is_available()

    def validate_text(
        self,
        text: str,
    ) -> None:
        """
        Validate runtime response text.
        """

        if not isinstance(text, str):
            raise TTSRuntimeIntegrationError(
                "text must be a string."
            )

        if not text.strip():
            raise TTSRuntimeIntegrationError(
                "text cannot be empty."
            )

    def synthesize(
        self,
        text: str,
        *,
        runtime_context_id: str | None = None,
        execution_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> MultimodalInputResult:
        """
        Synthesize runtime response text into audio.

        The actual synthesis remains the responsibility of
        the configured TTSProvider.
        """

        self.validate_text(text)

        try:
            result = self._provider.synthesize(
                text
            )

        except TTSProviderError:
            raise

        except Exception as exc:
            raise TTSRuntimeIntegrationError(
                str(exc)
            ) from exc

        if not isinstance(
            result,
            MultimodalInputResult,
        ):
            raise TTSRuntimeIntegrationError(
                "TTS provider returned an invalid result."
            )

        result.set_metadata(
            "integration",
            self.INTEGRATION_NAME,
        )

        result.set_metadata(
            "provider",
            self._provider.get_name(),
        )

        result.set_metadata(
            "source_text",
            text,
        )

        if runtime_context_id is not None:
            result.set_metadata(
                "runtime_context_id",
                runtime_context_id,
            )

        if execution_id is not None:
            result.set_metadata(
                "execution_id",
                execution_id,
            )

        if metadata:
            for key, value in metadata.items():
                result.set_metadata(
                    key,
                    value,
                )

        return result

    def synthesize_safe(
        self,
        text: str,
        *,
        runtime_context_id: str | None = None,
        execution_id: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> MultimodalInputResult:
        """
        Safely synthesize runtime response text.

        Integration and provider failures are converted into
        a failed MultimodalInputResult instead of propagating.
        """

        try:
            return self.synthesize(
                text,
                runtime_context_id=runtime_context_id,
                execution_id=execution_id,
                metadata=metadata,
            )

        except Exception as exc:
            result = MultimodalInputResult(
                input_id="tts-runtime-input",
                input_type="text",
            )

            result.fail(
                error=str(exc)
            )

            result.set_metadata(
                "integration",
                self.INTEGRATION_NAME,
            )

            result.set_metadata(
                "provider",
                self._provider.get_name(),
            )

            return result

    def __repr__(self) -> str:
        return (
            f"TTSRuntimeIntegration("
            f"provider={self._provider.get_name()!r}"
            f")"
        )


__all__ = [
    "TTSRuntimeIntegration",
    "TTSRuntimeIntegrationError",
]