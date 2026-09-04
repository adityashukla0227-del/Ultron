"""
OpenAI Voice Processor.

Ultron v0.58 — Voice → Text Runtime Integration

Connects the VoiceProcessor abstraction with the
provider-agnostic STTProvider abstraction.

Architecture:

    VoiceInput
        ↓
    OpenAIVoiceProcessor
        ↓
    STTProvider
        ↓
    OpenAISTTProvider
        ↓
    MultimodalInputResult
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.stt_provider import STTProvider
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processor import VoiceProcessor


class OpenAIVoiceProcessor(VoiceProcessor):
    """
    VoiceProcessor implementation backed by an STTProvider.

    The processor does not contain provider-specific API logic.
    It delegates transcription to the injected STTProvider.
    """

    def __init__(
        self,
        *,
        stt_provider: STTProvider,
        name: str = "openai-voice-processor",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not isinstance(
            stt_provider,
            STTProvider,
        ):
            raise TypeError(
                "stt_provider must be an STTProvider instance."
            )

        super().__init__(
            name=name,
            metadata=metadata,
        )

        self._stt_provider = stt_provider

    # ========================================================
    # Processing
    # ========================================================

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Process voice input through the configured STT provider.
        """

        self.validate_input(voice_input)

        result = self.create_processing_result(
            voice_input
        )

        try:
            transcription_result = (
                self._stt_provider.transcribe(
                    voice_input
                )
            )

            if not isinstance(
                transcription_result,
                MultimodalInputResult,
            ):
                return self.create_failure_result(
                    voice_input,
                    "STT provider returned an invalid result.",
                )

            if not transcription_result.is_successful():
                error = (
                    transcription_result.error
                    or "STT transcription failed."
                )

                return self.create_failure_result(
                    voice_input,
                    error,
                )

            text = transcription_result.get_data()

            if not isinstance(
                text,
                str,
            ):
                return self.create_failure_result(
                    voice_input,
                    "STT provider returned non-text transcription data.",
                )

            text = text.strip()

            if not text:
                return self.create_failure_result(
                    voice_input,
                    "STT provider returned empty transcription.",
                )

            result.complete(
                data=text,
                confidence=(
                    transcription_result.confidence
                ),
            )

            result.set_metadata(
                "provider",
                self._stt_provider.get_name(),
            )

            result.set_metadata(
                "transcription",
                text,
            )

            return result

        except Exception as exc:
            return self.create_failure_result(
                voice_input,
                str(exc),
            )

    # ========================================================
    # Provider
    # ========================================================

    def get_stt_provider(self) -> STTProvider:
        """
        Return the configured STT provider.
        """

        return self._stt_provider

    def set_stt_provider(
        self,
        stt_provider: STTProvider,
    ) -> None:
        """
        Replace the configured STT provider.
        """

        if not isinstance(
            stt_provider,
            STTProvider,
        ):
            raise TypeError(
                "stt_provider must be an STTProvider instance."
            )

        self._stt_provider = stt_provider


__all__ = [
    "OpenAIVoiceProcessor",
]