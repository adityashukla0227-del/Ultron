"""
Tests for Ultron TTS Provider Abstraction.

v0.61 — Text-to-Speech Provider Abstraction
"""

from __future__ import annotations

from typing import Any

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.tts_provider import (
    TTSProvider,
    TTSProviderError,
)


# ============================================================
# Dummy Provider
# ============================================================


class DummyTTSProvider(TTSProvider):
    """Concrete provider used for testing the abstraction."""

    def __init__(
        self,
        *,
        name: str = "Dummy TTS",
        supported_formats: list[str] | None = None,
        capabilities: list[str] | None = None,
        voices: list[str] | None = None,
        configuration: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        available: bool = True,
    ) -> None:
        super().__init__(
            name=name,
            supported_formats=supported_formats,
            capabilities=capabilities,
            voices=voices,
            configuration=configuration,
            metadata=metadata,
        )

        self.available = available

    def synthesize(
        self,
        text: str,
    ) -> MultimodalInputResult:
        self.validate_availability()
        self.validate_text(text)

        result = MultimodalInputResult(
            input_id="tts-test-001",
        )

        result.start_processing()

        result.complete(
            data={
                "audio": b"dummy-audio",
                "text": text,
                "provider": self.get_name(),
            }
        )

        return result

    def is_available(self) -> bool:
        return self.available


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def provider() -> DummyTTSProvider:
    return DummyTTSProvider(
        name="Dummy TTS",
        supported_formats=[
            "mp3",
            "wav",
            "ogg",
        ],
        capabilities=[
            "text_to_speech",
            "speech_synthesis",
        ],
        voices=[
            "alloy",
            "nova",
            "echo",
        ],
        configuration={
            "model": "dummy-model",
            "speed": 1.0,
        },
        metadata={
            "version": "0.61-test",
        },
    )


# ============================================================
# Abstract Contract
# ============================================================


def test_tts_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        TTSProvider(
            name="Abstract Provider"
        )


def test_synthesize_is_required() -> None:
    assert getattr(
        TTSProvider.synthesize,
        "__isabstractmethod__",
        False,
    )


# ============================================================
# Initialization
# ============================================================


def test_provider_initializes_with_valid_data(
    provider: DummyTTSProvider,
) -> None:
    assert provider.get_name() == "Dummy TTS"

    assert provider.get_supported_formats() == {
        "mp3",
        "wav",
        "ogg",
    }

    assert provider.get_capabilities() == {
        "text_to_speech",
        "speech_synthesis",
    }

    assert provider.get_voices() == {
        "alloy",
        "nova",
        "echo",
    }


def test_provider_name_is_trimmed() -> None:
    provider = DummyTTSProvider(
        name="  Dummy TTS  "
    )

    assert provider.get_name() == "Dummy TTS"


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_provider_name_raises(
    name,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            name=name
        )


# ============================================================
# Supported Formats
# ============================================================


def test_supported_formats_are_normalized() -> None:
    provider = DummyTTSProvider(
        supported_formats=[
            " MP3 ",
            "Wav",
            "OGG",
        ]
    )

    assert provider.get_supported_formats() == {
        "mp3",
        "wav",
        "ogg",
    }


def test_duplicate_formats_are_removed() -> None:
    provider = DummyTTSProvider(
        supported_formats=[
            "mp3",
            "mp3",
            "MP3",
        ]
    )

    assert provider.get_supported_formats() == {
        "mp3"
    }


def test_empty_supported_formats_are_allowed() -> None:
    provider = DummyTTSProvider(
        supported_formats=[]
    )

    assert provider.get_supported_formats() == set()


def test_none_supported_formats_are_allowed() -> None:
    provider = DummyTTSProvider(
        supported_formats=None
    )

    assert provider.get_supported_formats() == set()


def test_supported_formats_reject_string() -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            supported_formats="mp3"
        )


def test_supported_formats_reject_non_strings() -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            supported_formats=[
                "mp3",
                123,
            ]
        )


def test_supported_formats_reject_empty_values() -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            supported_formats=[
                "mp3",
                "",
            ]
        )


def test_supports_format_returns_true(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_format(
        "mp3"
    ) is True


def test_supports_format_is_case_insensitive(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_format(
        " MP3 "
    ) is True


def test_supports_format_returns_false(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_format(
        "flac"
    ) is False


@pytest.mark.parametrize(
    "audio_format",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_supports_format_invalid_value_raises(
    provider: DummyTTSProvider,
    audio_format,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.supports_format(
            audio_format
        )


def test_supported_formats_are_defensive_copy(
    provider: DummyTTSProvider,
) -> None:
    formats = provider.get_supported_formats()

    formats.add("flac")

    assert "flac" not in provider.get_supported_formats()


# ============================================================
# Capabilities
# ============================================================


def test_capabilities_are_normalized() -> None:
    provider = DummyTTSProvider(
        capabilities=[
            " Text_To_Speech ",
            "SPEECH_SYNTHESIS",
        ]
    )

    assert provider.get_capabilities() == {
        "text_to_speech",
        "speech_synthesis",
    }


def test_duplicate_capabilities_are_removed() -> None:
    provider = DummyTTSProvider(
        capabilities=[
            "text_to_speech",
            "text_to_speech",
        ]
    )

    assert provider.get_capabilities() == {
        "text_to_speech"
    }


def test_none_capabilities_are_allowed() -> None:
    provider = DummyTTSProvider(
        capabilities=None
    )

    assert provider.get_capabilities() == set()


def test_supports_capability_returns_true(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_capability(
        "text_to_speech"
    ) is True


def test_supports_capability_is_case_insensitive(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_capability(
        " TEXT_TO_SPEECH "
    ) is True


def test_supports_capability_returns_false(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_capability(
        "transcription"
    ) is False


@pytest.mark.parametrize(
    "capability",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_supports_capability_invalid_value_raises(
    provider: DummyTTSProvider,
    capability,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.supports_capability(
            capability
        )


def test_capabilities_are_defensive_copy(
    provider: DummyTTSProvider,
) -> None:
    capabilities = provider.get_capabilities()

    capabilities.add("transcription")

    assert (
        "transcription"
        not in provider.get_capabilities()
    )


# ============================================================
# Voices
# ============================================================


def test_voices_are_normalized() -> None:
    provider = DummyTTSProvider(
        voices=[
            " Alloy ",
            "NOVA",
            "Echo",
        ]
    )

    assert provider.get_voices() == {
        "alloy",
        "nova",
        "echo",
    }


def test_duplicate_voices_are_removed() -> None:
    provider = DummyTTSProvider(
        voices=[
            "alloy",
            "alloy",
            "ALLOY",
        ]
    )

    assert provider.get_voices() == {
        "alloy"
    }


def test_none_voices_are_allowed() -> None:
    provider = DummyTTSProvider(
        voices=None
    )

    assert provider.get_voices() == set()


def test_supports_voice_returns_true(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_voice(
        "alloy"
    ) is True


def test_supports_voice_is_case_insensitive(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_voice(
        " ALLOY "
    ) is True


def test_supports_voice_returns_false(
    provider: DummyTTSProvider,
) -> None:
    assert provider.supports_voice(
        "shimmer"
    ) is False


@pytest.mark.parametrize(
    "voice",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_supports_voice_invalid_value_raises(
    provider: DummyTTSProvider,
    voice,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.supports_voice(
            voice
        )


def test_voices_are_defensive_copy(
    provider: DummyTTSProvider,
) -> None:
    voices = provider.get_voices()

    voices.add("shimmer")

    assert (
        "shimmer"
        not in provider.get_voices()
    )


# ============================================================
# Configuration
# ============================================================


def test_configuration_is_initialized(
    provider: DummyTTSProvider,
) -> None:
    assert provider.get_configuration(
        "model"
    ) == "dummy-model"


def test_configuration_default_is_returned(
    provider: DummyTTSProvider,
) -> None:
    assert provider.get_configuration(
        "missing",
        "fallback",
    ) == "fallback"


def test_configuration_can_be_set(
    provider: DummyTTSProvider,
) -> None:
    provider.set_configuration(
        "model",
        "new-model",
    )

    assert provider.get_configuration(
        "model"
    ) == "new-model"


def test_configuration_can_be_updated(
    provider: DummyTTSProvider,
) -> None:
    provider.set_configuration(
        "speed",
        1.25,
    )

    assert provider.get_configuration(
        "speed"
    ) == 1.25


def test_configuration_is_defensive_copy(
    provider: DummyTTSProvider,
) -> None:
    configuration = (
        provider.get_all_configuration()
    )

    configuration["model"] = "changed"

    assert provider.get_configuration(
        "model"
    ) == "dummy-model"


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_configuration_key_raises(
    provider: DummyTTSProvider,
    key,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.get_configuration(
            key
        )


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_configuration_set_key_raises(
    provider: DummyTTSProvider,
    key,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.set_configuration(
            key,
            "value",
        )


def test_invalid_configuration_type_raises() -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            configuration=[]
        )


# ============================================================
# Metadata
# ============================================================


def test_metadata_is_initialized(
    provider: DummyTTSProvider,
) -> None:
    assert provider.get_metadata(
        "version"
    ) == "0.61-test"


def test_metadata_default_is_returned(
    provider: DummyTTSProvider,
) -> None:
    assert provider.get_metadata(
        "missing",
        "fallback",
    ) == "fallback"


def test_metadata_can_be_set(
    provider: DummyTTSProvider,
) -> None:
    provider.set_metadata(
        "region",
        "local",
    )

    assert provider.get_metadata(
        "region"
    ) == "local"


def test_metadata_is_defensive_copy(
    provider: DummyTTSProvider,
) -> None:
    metadata = provider.get_all_metadata()

    metadata["version"] = "changed"

    assert provider.get_metadata(
        "version"
    ) == "0.61-test"


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_metadata_key_raises(
    provider: DummyTTSProvider,
    key,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.get_metadata(
            key
        )


def test_invalid_metadata_type_raises() -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        DummyTTSProvider(
            metadata=[]
        )


# ============================================================
# Availability
# ============================================================


def test_provider_is_available_by_default() -> None:
    provider = DummyTTSProvider()

    assert provider.is_available() is True


def test_available_provider_passes_validation() -> None:
    provider = DummyTTSProvider(
        available=True
    )

    provider.validate_availability()


def test_unavailable_provider_fails_validation() -> None:
    provider = DummyTTSProvider(
        available=False
    )

    with pytest.raises(TTSProviderError):
        provider.validate_availability()


# ============================================================
# Text Validation
# ============================================================


@pytest.mark.parametrize(
    "text",
    [
        "Hello world",
        "Hello",
        "Namaste Ultron",
        "12345",
    ],
)
def test_valid_text_passes_validation(
    provider: DummyTTSProvider,
    text: str,
) -> None:
    provider.validate_text(text)


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "\t",
        "\n",
        None,
        123,
    ],
)
def test_invalid_text_is_rejected(
    provider: DummyTTSProvider,
    text,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.validate_text(text)


# ============================================================
# Synthesis Contract
# ============================================================


def test_synthesize_returns_multimodal_result(
    provider: DummyTTSProvider,
) -> None:
    result = provider.synthesize(
        "Hello Ultron"
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )


def test_synthesis_result_is_completed(
    provider: DummyTTSProvider,
) -> None:
    result = provider.synthesize(
        "Hello Ultron"
    )

    assert result.is_completed()
    assert result.is_successful()


def test_synthesis_result_contains_audio(
    provider: DummyTTSProvider,
) -> None:
    result = provider.synthesize(
        "Hello Ultron"
    )

    data = result.get_data()

    assert data["audio"] == b"dummy-audio"


def test_synthesis_result_contains_text(
    provider: DummyTTSProvider,
) -> None:
    result = provider.synthesize(
        "Hello Ultron"
    )

    data = result.get_data()

    assert data["text"] == "Hello Ultron"


def test_synthesis_result_contains_provider_metadata(
    provider: DummyTTSProvider,
) -> None:
    result = provider.synthesize(
        "Hello Ultron"
    )

    data = result.get_data()

    assert data["provider"] == "Dummy TTS"


def test_unavailable_provider_blocks_synthesis() -> None:
    provider = DummyTTSProvider(
        available=False
    )

    with pytest.raises(TTSProviderError):
        provider.synthesize(
            "Hello Ultron"
        )


def test_empty_text_blocks_synthesis(
    provider: DummyTTSProvider,
) -> None:
    with pytest.raises(
        (TTSProviderError, TypeError, ValueError)
    ):
        provider.synthesize(
            ""
        )


# ============================================================
# Representation
# ============================================================


def test_repr_contains_provider_information(
    provider: DummyTTSProvider,
) -> None:
    representation = repr(provider)

    assert "DummyTTSProvider" in representation
    assert "Dummy TTS" in representation
    assert "mp3" in representation
    assert "text_to_speech" in representation
    assert "alloy" in representation