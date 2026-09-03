"""
OpenAI STT Provider.

Ultron v0.57 — First STT Provider

Concrete speech-to-text provider implementation built on top
of the provider-agnostic STTProvider abstraction.

This module keeps provider-specific logic isolated from the
Ultron voice processing and runtime layers.
"""

from __future__ import annotations

from io import BytesIO
from typing import Any, Dict

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.stt_provider import (
    STTProvider,
    STTProviderError,
)
from modules.multimodal.voice_input import VoiceInput


class OpenAISTTProvider(STTProvider):
    """
    OpenAI-backed speech-to-text provider.

    The provider is intentionally isolated behind the STTProvider
    abstraction so that the rest of Ultron does not depend directly
    on the OpenAI SDK.
    """

    DEFAULT_MODEL = "gpt-4o-mini-transcribe"

    DEFAULT_SUPPORTED_FORMATS = {
        "wav",
        "mp3",
        "m4a",
        "ogg",
        "flac",
        "webm",
    }

    DEFAULT_CAPABILITIES = {
        "transcription",
        "speech_to_text",
    }

    def __init__(
        self,
        *,
        client: Any,
        name: str = "openai-stt",
        model: str = DEFAULT_MODEL,
        supported_formats: set[str] | None = None,
        capabilities: set[str] | None = None,
        configuration: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if client is None:
            raise STTProviderError(
                "client cannot be None."
            )

        if not isinstance(model, str) or not model.strip():
            raise STTProviderError(
                "model must be a non-empty string."
            )

        provider_configuration = dict(
            configuration or {}
        )

        provider_configuration.setdefault(
            "model",
            model.strip(),
        )

        super().__init__(
            name=name,
            supported_formats=(
                supported_formats
                if supported_formats is not None
                else self.DEFAULT_SUPPORTED_FORMATS
            ),
            capabilities=(
                capabilities
                if capabilities is not None
                else self.DEFAULT_CAPABILITIES
            ),
            configuration=provider_configuration,
            metadata=metadata,
        )

        self._client = client

    def is_available(self) -> bool:
        """
        Return whether the OpenAI client is available.

        Client creation/authentication remains outside this provider.
        The provider only verifies that a client was supplied.
        """
        return self._client is not None

    def transcribe(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        """
        Transcribe a VoiceInput using the configured OpenAI client.
        """
        self.validate_availability()
        self.validate_input(voice_input)

        input_id = voice_input.get_id()

        result = MultimodalInputResult(
            input_id=input_id,
            input_type=voice_input.input_type,
        )

        try:
            audio_format = voice_input.get_format()

            if audio_format is None:
                raise STTProviderError(
                    "VoiceInput must specify an audio format."
                )

            audio_data = voice_input.get_audio_data()

            if audio_data is None:
                raise STTProviderError(
                    "VoiceInput contains no audio data."
                )

            filename = (
                f"ultron_audio.{audio_format}"
            )

            if isinstance(audio_data, bytes):
                audio_bytes = audio_data
            else:
                audio_bytes = bytes(audio_data)

            audio_file = BytesIO(audio_bytes)
            audio_file.name = filename

            model = self.get_configuration(
                "model",
                self.DEFAULT_MODEL,
            )

            response = (
                self._client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                )
            )

            text = self._extract_text(
                response
            )

            if not text:
                result.fail(
                    error="STT provider returned empty transcription."
                )
                return result

            # InputResult.complete() only accepts the result data
            # and confidence. Metadata must be attached separately.
            result.complete(
                data=text
            )

            result.set_metadata(
                "provider",
                self.get_name(),
            )

            result.set_metadata(
                "model",
                model,
            )

            return result

        except STTProviderError:
            raise

        except Exception as exc:
            result.fail(
                error=str(exc)
            )
            return result

    @staticmethod
    def _extract_text(
        response: Any,
    ) -> str:
        """
        Extract transcription text from an OpenAI response.

        Supports both object-style and dictionary-style responses.
        """
        if response is None:
            return ""

        text = getattr(
            response,
            "text",
            None,
        )

        if text is None and isinstance(
            response,
            dict,
        ):
            text = response.get(
                "text"
            )

        if text is None:
            return ""

        if not isinstance(text, str):
            return str(text)

        return text.strip()


__all__ = [
    "OpenAISTTProvider",
]