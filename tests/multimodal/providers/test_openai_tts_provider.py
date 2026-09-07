"""
Tests for OpenAI TTS Provider.

Ultron v0.62 — First TTS Provider
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.tts_provider import TTSProviderError
from modules.multimodal.providers.openai_tts_provider import (
    OpenAITTSProvider,
)


class TestOpenAITTSProviderInitialization:
    """Test provider initialization and configuration."""

    def test_provider_requires_client(self):
        with pytest.raises(TTSProviderError):
            OpenAITTSProvider(client=None)

    def test_provider_requires_valid_model(self):
        client = MagicMock()

        with pytest.raises(TTSProviderError):
            OpenAITTSProvider(
                client=client,
                model="",
            )

    def test_provider_initializes_successfully(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.get_name() == "openai-tts"

    def test_provider_uses_default_model(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert (
            provider.get_configuration("model")
            == OpenAITTSProvider.DEFAULT_MODEL
        )

    def test_provider_accepts_custom_model(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            model="custom-tts-model",
        )

        assert (
            provider.get_configuration("model")
            == "custom-tts-model"
        )

    def test_provider_is_available_with_client(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.is_available() is True

    def test_provider_has_text_to_speech_capability(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_capability(
            "text_to_speech"
        )

    def test_provider_has_speech_synthesis_capability(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_capability(
            "speech_synthesis"
        )


class TestOpenAITTSProviderFormats:
    """Test supported audio formats."""

    @pytest.mark.parametrize(
        "audio_format",
        [
            "mp3",
            "wav",
            "opus",
            "aac",
            "flac",
            "pcm",
        ],
    )
    def test_supported_format(
        self,
        audio_format,
    ):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_format(
            audio_format
        )

    def test_format_matching_is_case_insensitive(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_format(
            "MP3"
        )

    def test_format_matching_strips_whitespace(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_format(
            " mp3 "
        )

    def test_unsupported_format(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert not provider.supports_format(
            "m4a"
        )

    def test_supported_formats_are_returned_as_copy(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        formats = provider.get_supported_formats()

        formats.add("fake")

        assert "fake" not in provider.get_supported_formats()


class TestOpenAITTSProviderVoices:
    """Test supported voices."""

    @pytest.mark.parametrize(
        "voice",
        [
            "alloy",
            "echo",
            "fable",
            "onyx",
            "nova",
            "shimmer",
        ],
    )
    def test_supported_voice(
        self,
        voice,
    ):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_voice(
            voice
        )

    def test_voice_matching_is_case_insensitive(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_voice(
            "NOVA"
        )

    def test_voice_matching_strips_whitespace(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert provider.supports_voice(
            " nova "
        )

    def test_unsupported_voice(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        assert not provider.supports_voice(
            "fake-voice"
        )

    def test_supported_voices_are_returned_as_copy(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        voices = provider.get_voices()

        voices.add("fake")

        assert "fake" not in provider.get_voices()


class TestOpenAITTSProviderAvailability:
    """Test provider availability behavior."""

    def test_validate_availability_succeeds_with_client(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        provider.validate_availability()

    def test_missing_client_cannot_create_provider(self):
        with pytest.raises(TTSProviderError):
            OpenAITTSProvider(
                client=None
            )


class TestOpenAITTSProviderSynthesis:
    """Test text-to-speech synthesis behavior."""

    @staticmethod
    def create_provider():
        client = MagicMock()

        response = SimpleNamespace(
            audio=b"generated-audio"
        )

        client.audio.speech.create.return_value = (
            response
        )

        provider = OpenAITTSProvider(
            client=client
        )

        return provider, client

    def test_successful_synthesis_returns_result(
        self,
    ):
        provider, _ = self.create_provider()

        result = provider.synthesize(
            "Hello from Ultron"
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

    def test_successful_synthesis_is_completed(
        self,
    ):
        provider, _ = self.create_provider()

        result = provider.synthesize(
            "Hello from Ultron"
        )

        assert result.is_completed()

    def test_successful_synthesis_is_successful(
        self,
    ):
        provider, _ = self.create_provider()

        result = provider.synthesize(
            "Hello from Ultron"
        )

        assert result.is_successful()

    def test_synthesis_returns_expected_audio(
        self,
    ):
        provider, _ = self.create_provider()

        result = provider.synthesize(
            "Hello from Ultron"
        )

        assert result.get_data() == (
            b"generated-audio"
        )

    def test_provider_calls_openai_speech_api(
        self,
    ):
        provider, client = self.create_provider()

        provider.synthesize(
            "Hello from Ultron"
        )

        client.audio.speech.create.assert_called_once()

    def test_provider_uses_configured_model(
        self,
    ):
        provider, client = self.create_provider()

        provider.set_configuration(
            "model",
            "custom-model",
        )

        provider.synthesize(
            "Hello from Ultron"
        )

        call_kwargs = (
            client.audio.speech.create
            .call_args.kwargs
        )

        assert call_kwargs["model"] == (
            "custom-model"
        )

    def test_provider_sends_input_text(
        self,
    ):
        provider, client = self.create_provider()

        text = "Hello from Ultron"

        provider.synthesize(text)

        call_kwargs = (
            client.audio.speech.create
            .call_args.kwargs
        )

        assert call_kwargs["input"] == text

    def test_provider_uses_default_voice(
        self,
    ):
        provider, client = self.create_provider()

        provider.synthesize(
            "Hello from Ultron"
        )

        call_kwargs = (
            client.audio.speech.create
            .call_args.kwargs
        )

        assert call_kwargs["voice"] == (
            OpenAITTSProvider.DEFAULT_VOICE
        )

    def test_provider_uses_configured_voice(
        self,
    ):
        provider, client = self.create_provider()

        provider.set_configuration(
            "voice",
            "nova",
        )

        provider.synthesize(
            "Hello from Ultron"
        )

        call_kwargs = (
            client.audio.speech.create
            .call_args.kwargs
        )

        assert call_kwargs["voice"] == "nova"

    def test_provider_uses_default_format(
        self,
    ):
        provider, client = self.create_provider()

        provider.synthesize(
            "Hello from Ultron"
        )

        call_kwargs = (
            client.audio.speech.create
            .call_args.kwargs
        )

        assert call_kwargs["response_format"] == (
            OpenAITTSProvider.DEFAULT_AUDIO_FORMAT
        )

    def test_empty_text_fails_before_api_call(
        self,
    ):
        provider, client = self.create_provider()

        with pytest.raises(
            (TTSProviderError, ValueError, TypeError)
        ):
            provider.synthesize("")

        client.audio.speech.create.assert_not_called()

    def test_whitespace_text_fails_before_api_call(
        self,
    ):
        provider, client = self.create_provider()

        with pytest.raises(
            (TTSProviderError, ValueError, TypeError)
        ):
            provider.synthesize("   ")

        client.audio.speech.create.assert_not_called()

    def test_none_text_fails_before_api_call(
        self,
    ):
        provider, client = self.create_provider()

        with pytest.raises(
            (TTSProviderError, ValueError, TypeError)
        ):
            provider.synthesize(None)

        client.audio.speech.create.assert_not_called()

    def test_empty_audio_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.speech.create.return_value = (
            SimpleNamespace(
                audio=b""
            )
        )

        provider = OpenAITTSProvider(
            client=client
        )

        result = provider.synthesize(
            "Hello"
        )

        assert result.status == "failed"
        assert result.success is False

    def test_none_audio_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.speech.create.return_value = (
            SimpleNamespace(
                audio=None
            )
        )

        provider = OpenAITTSProvider(
            client=client
        )

        result = provider.synthesize(
            "Hello"
        )

        assert result.status == "failed"
        assert result.success is False

    def test_none_response_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.speech.create.return_value = (
            None
        )

        provider = OpenAITTSProvider(
            client=client
        )

        result = provider.synthesize(
            "Hello"
        )

        assert result.status == "failed"
        assert result.success is False

    def test_provider_exception_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.speech.create.side_effect = (
            RuntimeError("provider failure")
        )

        provider = OpenAITTSProvider(
            client=client
        )

        result = provider.synthesize(
            "Hello"
        )

        assert result.status == "failed"
        assert result.success is False

    def test_provider_exception_message_is_preserved(
        self,
    ):
        client = MagicMock()

        client.audio.speech.create.side_effect = (
            RuntimeError("provider failure")
        )

        provider = OpenAITTSProvider(
            client=client
        )

        result = provider.synthesize(
            "Hello"
        )

        assert "provider failure" in str(
            result.error
        )


class TestOpenAITTSProviderResponseExtraction:
    """Test response audio extraction."""

    def test_extract_audio_from_object(self):
        response = SimpleNamespace(
            audio=b"audio-data"
        )

        assert (
            OpenAITTSProvider._extract_audio(
                response
            )
            == b"audio-data"
        )

    def test_extract_audio_from_dictionary(self):
        response = {
            "audio": b"audio-data"
        }

        assert (
            OpenAITTSProvider._extract_audio(
                response
            )
            == b"audio-data"
        )

    def test_extract_audio_returns_none_for_none(self):
        assert (
            OpenAITTSProvider._extract_audio(
                None
            )
            is None
        )

    def test_extract_audio_returns_none_when_missing(self):
        response = SimpleNamespace(
            other="value"
        )

        assert (
            OpenAITTSProvider._extract_audio(
                response
            )
            is None
        )


class TestOpenAITTSProviderConfiguration:
    """Test provider configuration behavior."""

    def test_configuration_is_preserved(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            configuration={
                "speed": 1.0,
            },
        )

        assert (
            provider.get_configuration("speed")
            == 1.0
        )

    def test_model_is_added_to_configuration(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            model="test-model",
        )

        config = (
            provider.get_all_configuration()
        )

        assert config["model"] == "test-model"

    def test_configuration_can_be_updated(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        provider.set_configuration(
            "speed",
            1.2,
        )

        assert (
            provider.get_configuration("speed")
            == 1.2
        )

    def test_configuration_returns_defensive_copy(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            configuration={
                "nested": {
                    "value": 1,
                }
            },
        )

        config = (
            provider.get_all_configuration()
        )

        config["nested"]["value"] = 999

        assert (
            provider.get_configuration(
                "nested"
            )["value"]
            == 1
        )


class TestOpenAITTSProviderMetadata:
    """Test provider metadata."""

    def test_metadata_is_preserved(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            metadata={
                "version": "v0.62",
            },
        )

        assert (
            provider.get_metadata("version")
            == "v0.62"
        )

    def test_metadata_can_be_updated(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        provider.set_metadata(
            "environment",
            "test",
        )

        assert (
            provider.get_metadata(
                "environment"
            )
            == "test"
        )

    def test_metadata_returns_defensive_copy(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client,
            metadata={
                "nested": {
                    "value": 1,
                }
            },
        )

        metadata = (
            provider.get_all_metadata()
        )

        metadata["nested"]["value"] = 999

        assert (
            provider.get_metadata(
                "nested"
            )["value"]
            == 1
        )


class TestOpenAITTSProviderRepresentation:
    """Test provider representation."""

    def test_repr_contains_provider_name(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "openai-tts" in representation

    def test_repr_contains_supported_formats(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "mp3" in representation
        assert "wav" in representation

    def test_repr_contains_capabilities(self):
        client = MagicMock()

        provider = OpenAITTSProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "text_to_speech" in representation