"""
OpenAI TTS Provider.

Ultron v0.62 — First TTS Provider

Concrete text-to-speech provider implementation built on top
of the provider-agnostic TTSProvider abstraction.

This module keeps provider-specific logic isolated from the
Ultron voice processing and runtime layers.
"""

from __future__ import annotations

from typing import Any, Dict

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.tts_provider import (
    TTSProvider,
    TTSProviderError,
)


class OpenAITTSProvider(TTSProvider):
    """
    OpenAI-backed Text-to-Speech provider.

    Responsibilities:
    - Validate provider configuration
    - Call OpenAI speech synthesis API
    - Extract generated audio
    - Return MultimodalInputResult
    - Preserve provider metadata
    """

    DEFAULT_MODEL = "gpt-4o-mini-tts"

    DEFAULT_VOICE = "alloy"

    DEFAULT_AUDIO_FORMAT = "mp3"

    DEFAULT_SUPPORTED_FORMATS = {
        "mp3",
        "wav",
        "opus",
        "aac",
        "flac",
        "pcm",
    }

    DEFAULT_CAPABILITIES = {
        "text_to_speech",
        "speech_synthesis",
    }

    DEFAULT_VOICES = {
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer",
    }

    def __init__(
        self,
        *,
        client: Any,
        name: str = "openai-tts",
        model: str = DEFAULT_MODEL,
        voice: str = DEFAULT_VOICE,
        audio_format: str = DEFAULT_AUDIO_FORMAT,
        supported_formats: set[str] | None = None,
        capabilities: set[str] | None = None,
        voices: set[str] | None = None,
        configuration: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        if client is None:
            raise TTSProviderError(
                "client cannot be None."
            )

        if (
            not isinstance(model, str)
            or not model.strip()
        ):
            raise TTSProviderError(
                "model must be a non-empty string."
            )

        if (
            not isinstance(voice, str)
            or not voice.strip()
        ):
            raise TTSProviderError(
                "voice must be a non-empty string."
            )

        if (
            not isinstance(audio_format, str)
            or not audio_format.strip()
        ):
            raise TTSProviderError(
                "audio_format must be a non-empty string."
            )

        normalized_voice = voice.strip().lower()
        normalized_format = (
            audio_format.strip().lower()
        )

        provider_configuration = dict(
            configuration or {}
        )

        provider_configuration.setdefault(
            "model",
            model.strip(),
        )

        provider_configuration.setdefault(
            "voice",
            normalized_voice,
        )

        provider_configuration.setdefault(
            "audio_format",
            normalized_format,
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
            voices=(
                voices
                if voices is not None
                else self.DEFAULT_VOICES
            ),
            configuration=provider_configuration,
            metadata=metadata,
        )

        self._client = client

    def is_available(self) -> bool:
        return self._client is not None

    def synthesize(
        self,
        text: str,
    ) -> MultimodalInputResult:
        """
        Convert text into synthesized audio.
        """

        self.validate_availability()
        self.validate_text(text)

        result = MultimodalInputResult(
            input_id="tts-input",
            input_type="text",
        )

        try:
            model = self.get_configuration(
                "model",
                self.DEFAULT_MODEL,
            )

            voice = self.get_configuration(
                "voice",
                self.DEFAULT_VOICE,
            )

            audio_format = self.get_configuration(
                "audio_format",
                self.DEFAULT_AUDIO_FORMAT,
            )

            if not self.supports_voice(voice):
                raise TTSProviderError(
                    f"Unsupported voice: {voice}"
                )

            if not self.supports_format(
                audio_format
            ):
                raise TTSProviderError(
                    f"Unsupported audio format: "
                    f"{audio_format}"
                )

            response = (
                self._client.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=text,
                    response_format=audio_format,
                )
            )

            audio = self._extract_audio(
                response
            )

            if not audio:
                result.fail(
                    error=(
                        "TTS provider returned "
                        "empty audio."
                    )
                )
                return result

            result.complete(
                data=audio
            )

            result.set_metadata(
                "provider",
                self.get_name(),
            )

            result.set_metadata(
                "model",
                model,
            )

            result.set_metadata(
                "voice",
                voice,
            )

            result.set_metadata(
                "audio_format",
                audio_format,
            )

            return result

        except TTSProviderError:
            raise

        except Exception as exc:
            result.fail(
                error=str(exc)
            )
            return result

    @staticmethod
    def _extract_audio(
        response: Any,
    ) -> bytes | None:
        """
        Extract synthesized audio from provider response.
        """

        if response is None:
            return None

        audio = getattr(
            response,
            "audio",
            None,
        )

        if audio is None and isinstance(
            response,
            dict,
        ):
            audio = response.get(
                "audio"
            )

        if audio is None:
            return None

        if isinstance(
            audio,
            bytes,
        ):
            return audio

        if isinstance(
            audio,
            bytearray,
        ):
            return bytes(audio)

        try:
            return bytes(audio)
        except (TypeError, ValueError):
            return None


__all__ = [
    "OpenAITTSProvider",
]