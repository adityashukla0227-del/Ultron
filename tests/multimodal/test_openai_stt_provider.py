"""
Tests for OpenAI STT Provider.

Ultron v0.57 — First STT Provider
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.stt_provider import STTProviderError
from modules.multimodal.providers.openai_stt_provider import (
    OpenAISTTProvider,
)
from modules.multimodal.voice_input import VoiceInput


class TestOpenAISTTProviderInitialization:
    """Test provider initialization and configuration."""

    def test_provider_requires_client(self):
        with pytest.raises(STTProviderError):
            OpenAISTTProvider(client=None)

    def test_provider_requires_valid_model(self):
        client = MagicMock()

        with pytest.raises(STTProviderError):
            OpenAISTTProvider(
                client=client,
                model="",
            )

    def test_provider_initializes_successfully(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.get_name() == "openai-stt"

    def test_provider_uses_default_model(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert (
            provider.get_configuration("model")
            == OpenAISTTProvider.DEFAULT_MODEL
        )

    def test_provider_accepts_custom_model(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client,
            model="custom-transcribe-model",
        )

        assert (
            provider.get_configuration("model")
            == "custom-transcribe-model"
        )

    def test_provider_is_available_with_client(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.is_available() is True

    def test_provider_has_transcription_capability(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.supports_capability(
            "transcription"
        )

    def test_provider_has_speech_to_text_capability(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.supports_capability(
            "speech_to_text"
        )


class TestOpenAISTTProviderFormats:
    """Test supported audio formats."""

    @pytest.mark.parametrize(
        "audio_format",
        [
            "wav",
            "mp3",
            "m4a",
            "ogg",
            "flac",
            "webm",
        ],
    )
    def test_supported_format(
        self,
        audio_format,
    ):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.supports_format(
            audio_format
        )

    def test_format_matching_is_case_insensitive(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.supports_format(
            "WAV"
        )

    def test_format_matching_strips_whitespace(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert provider.supports_format(
            " wav "
        )

    def test_unsupported_format(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        assert not provider.supports_format(
            "pcm"
        )

    def test_supported_formats_are_returned_as_copy(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        formats = provider.get_supported_formats()

        formats.add("fake")

        assert "fake" not in provider.get_supported_formats()


class TestOpenAISTTProviderInputValidation:
    """Test VoiceInput validation."""

    def test_valid_voice_input_is_accepted(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = VoiceInput(
            b"audio-data",
            audio_format="wav",
        )

        provider.validate_input(
            voice_input
        )

    def test_invalid_object_is_rejected(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        with pytest.raises(STTProviderError):
            provider.validate_input(
                "not-a-voice-input"
            )

    def test_unsupported_audio_format_is_rejected(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = VoiceInput(
            b"audio-data",
            audio_format="pcm",
        )

        with pytest.raises(STTProviderError):
            provider.validate_input(
                voice_input
            )

    def test_voice_input_without_format_can_pass_base_validation(
        self,
    ):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = VoiceInput(
            b"audio-data"
        )

        provider.validate_input(
            voice_input
        )


class TestOpenAISTTProviderAvailability:
    """Test provider availability behavior."""

    def test_validate_availability_succeeds_with_client(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        provider.validate_availability()

    def test_missing_client_cannot_create_provider(self):
        with pytest.raises(STTProviderError):
            OpenAISTTProvider(
                client=None
            )


class TestOpenAISTTProviderTranscription:
    """Test transcription behavior."""

    @staticmethod
    def create_provider():
        client = MagicMock()

        response = SimpleNamespace(
            text="Hello from Ultron"
        )

        client.audio.transcriptions.create.return_value = (
            response
        )

        provider = OpenAISTTProvider(
            client=client
        )

        return provider, client

    @staticmethod
    def create_voice_input():
        return VoiceInput(
            b"fake-audio-data",
            input_id="voice-test-001",
            audio_format="wav",
        )

    def test_successful_transcription_returns_result(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

    def test_successful_transcription_is_completed(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.is_completed()

    def test_successful_transcription_is_successful(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.is_successful()

    def test_transcription_returns_expected_text(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.get_data() == (
            "Hello from Ultron"
        )

    def test_transcription_preserves_input_id(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.input_id == (
            "voice-test-001"
        )

    def test_transcription_preserves_voice_input_type(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.input_type == (
            voice_input.input_type
        )

    def test_provider_calls_openai_transcription_api(
        self,
    ):
        provider, client = self.create_provider()

        voice_input = self.create_voice_input()

        provider.transcribe(
            voice_input
        )

        client.audio.transcriptions.create.assert_called_once()

    def test_provider_uses_configured_model(
        self,
    ):
        provider, client = self.create_provider()

        provider.set_configuration(
            "model",
            "custom-model",
        )

        voice_input = self.create_voice_input()

        provider.transcribe(
            voice_input
        )

        call_kwargs = (
            client.audio.transcriptions.create
            .call_args.kwargs
        )

        assert call_kwargs["model"] == (
            "custom-model"
        )

    def test_provider_sends_audio_file(
        self,
    ):
        provider, client = self.create_provider()

        voice_input = self.create_voice_input()

        provider.transcribe(
            voice_input
        )

        call_kwargs = (
            client.audio.transcriptions.create
            .call_args.kwargs
        )

        audio_file = call_kwargs["file"]

        assert audio_file is not None
        assert audio_file.name == "ultron_audio.wav"

    def test_empty_transcription_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.transcriptions.create.return_value = (
            SimpleNamespace(text="")
        )

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.status == "failed"
        assert result.success is False

    def test_none_response_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.transcriptions.create.return_value = (
            None
        )

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.status == "failed"
        assert result.success is False

    def test_provider_exception_fails_result(
        self,
    ):
        client = MagicMock()

        client.audio.transcriptions.create.side_effect = (
            RuntimeError("provider failure")
        )

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert result.status == "failed"
        assert result.success is False

    def test_provider_exception_message_is_preserved(
        self,
    ):
        client = MagicMock()

        client.audio.transcriptions.create.side_effect = (
            RuntimeError("provider failure")
        )

        provider = OpenAISTTProvider(
            client=client
        )

        voice_input = self.create_voice_input()

        result = provider.transcribe(
            voice_input
        )

        assert "provider failure" in str(
            result.error
        )

    def test_invalid_voice_input_does_not_call_provider(
        self,
    ):
        provider, client = self.create_provider()

        with pytest.raises(STTProviderError):
            provider.transcribe(
                "invalid-input"
            )

        client.audio.transcriptions.create.assert_not_called()

    def test_unsupported_format_does_not_call_provider(
        self,
    ):
        provider, client = self.create_provider()

        voice_input = VoiceInput(
            b"audio-data",
            input_id="unsupported-format",
            audio_format="pcm",
        )

        with pytest.raises(STTProviderError):
            provider.transcribe(
                voice_input
            )

        client.audio.transcriptions.create.assert_not_called()

    def test_transcription_uses_voice_input_id(
        self,
    ):
        provider, _ = self.create_provider()

        voice_input = VoiceInput(
            b"audio-data",
            input_id="custom-id",
            audio_format="wav",
        )

        result = provider.transcribe(
            voice_input
        )

        assert result.input_id == "custom-id"


class TestOpenAISTTProviderResponseExtraction:
    """Test response text extraction."""

    def test_extract_text_from_object(self):
        response = SimpleNamespace(
            text="Hello"
        )

        assert (
            OpenAISTTProvider._extract_text(
                response
            )
            == "Hello"
        )

    def test_extract_text_from_dictionary(self):
        response = {
            "text": "Hello"
        }

        assert (
            OpenAISTTProvider._extract_text(
                response
            )
            == "Hello"
        )

    def test_extract_text_strips_whitespace(self):
        response = SimpleNamespace(
            text="  Hello  "
        )

        assert (
            OpenAISTTProvider._extract_text(
                response
            )
            == "Hello"
        )

    def test_extract_text_returns_empty_for_none(self):
        assert (
            OpenAISTTProvider._extract_text(
                None
            )
            == ""
        )

    def test_extract_text_returns_empty_when_missing(self):
        response = SimpleNamespace(
            other="value"
        )

        assert (
            OpenAISTTProvider._extract_text(
                response
            )
            == ""
        )

    def test_extract_text_handles_non_string_text(self):
        response = SimpleNamespace(
            text=123
        )

        assert (
            OpenAISTTProvider._extract_text(
                response
            )
            == "123"
        )


class TestOpenAISTTProviderConfiguration:
    """Test provider configuration behavior."""

    def test_configuration_is_preserved(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client,
            configuration={
                "timeout": 30,
            },
        )

        assert (
            provider.get_configuration("timeout")
            == 30
        )

    def test_model_is_added_to_configuration(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client,
            model="test-model",
        )

        config = (
            provider.get_all_configuration()
        )

        assert config["model"] == "test-model"

    def test_configuration_can_be_updated(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        provider.set_configuration(
            "timeout",
            60,
        )

        assert (
            provider.get_configuration("timeout")
            == 60
        )

    def test_configuration_returns_defensive_copy(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
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


class TestOpenAISTTProviderMetadata:
    """Test provider metadata."""

    def test_metadata_is_preserved(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client,
            metadata={
                "version": "v0.57",
            },
        )

        assert (
            provider.get_metadata("version")
            == "v0.57"
        )

    def test_metadata_can_be_updated(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
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

        provider = OpenAISTTProvider(
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


class TestOpenAISTTProviderRepresentation:
    """Test provider representation."""

    def test_repr_contains_provider_name(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "openai-stt" in representation

    def test_repr_contains_supported_formats(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "wav" in representation
        assert "mp3" in representation

    def test_repr_contains_capabilities(self):
        client = MagicMock()

        provider = OpenAISTTProvider(
            client=client
        )

        representation = repr(
            provider
        )

        assert "transcription" in representation