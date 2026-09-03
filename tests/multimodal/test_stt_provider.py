"""
Tests for Ultron STT Provider Abstraction.

v0.56 — STT Provider Abstraction
"""

from __future__ import annotations

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.stt_provider import (
    STTProvider,
    STTProviderError,
)
from modules.multimodal.voice_input import VoiceInput


# ============================================================
# Dummy Provider
# ============================================================


class DummySTTProvider(STTProvider):
    """Concrete provider used for testing the abstraction."""

    def __init__(
        self,
        *,
        name: str = "Dummy STT",
        supported_formats: list[str] | None = None,
        capabilities: list[str] | None = None,
        configuration: dict | None = None,
        metadata: dict | None = None,
        available: bool = True,
    ) -> None:
        super().__init__(
            name=name,
            supported_formats=supported_formats,
            capabilities=capabilities,
            configuration=configuration,
            metadata=metadata,
        )

        self.available = available

    def transcribe(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_availability()
        self.validate_input(voice_input)

        result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=voice_input.input_type,
        )

        result.start_processing()

        result.complete(
            data={
                "text": "dummy transcription",
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
def provider() -> DummySTTProvider:
    return DummySTTProvider(
        name="Dummy STT",
        supported_formats=["wav", "mp3", "flac"],
        capabilities=[
            "transcription",
            "timestamps",
        ],
        configuration={
            "language": "en",
            "temperature": 0.0,
        },
        metadata={
            "version": "0.56-test",
        },
    )


@pytest.fixture
def voice_input() -> VoiceInput:
    return VoiceInput(
        b"test-audio",
        input_id="voice-test-001",
        source="test",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=2.5,
    )


# ============================================================
# Abstract Contract
# ============================================================


def test_stt_provider_is_abstract() -> None:
    with pytest.raises(TypeError):
        STTProvider(name="Abstract Provider")


def test_transcribe_is_required() -> None:
    assert getattr(
        STTProvider.transcribe,
        "__isabstractmethod__",
        False,
    )


# ============================================================
# Initialization
# ============================================================


def test_provider_initializes_with_valid_data(
    provider: DummySTTProvider,
) -> None:
    assert provider.get_name() == "Dummy STT"
    assert provider.get_supported_formats() == {
        "wav",
        "mp3",
        "flac",
    }
    assert provider.get_capabilities() == {
        "transcription",
        "timestamps",
    }


def test_provider_name_is_trimmed() -> None:
    provider = DummySTTProvider(
        name="  Dummy STT  "
    )

    assert provider.get_name() == "Dummy STT"


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
    with pytest.raises(STTProviderError):
        DummySTTProvider(name=name)


# ============================================================
# Supported Formats
# ============================================================


def test_supported_formats_are_normalized() -> None:
    provider = DummySTTProvider(
        supported_formats=[
            " WAV ",
            "Mp3",
            "FLAC",
        ]
    )

    assert provider.get_supported_formats() == {
        "wav",
        "mp3",
        "flac",
    }


def test_duplicate_formats_are_removed() -> None:
    provider = DummySTTProvider(
        supported_formats=[
            "wav",
            "wav",
            "WAV",
        ]
    )

    assert provider.get_supported_formats() == {
        "wav"
    }


def test_empty_supported_formats_are_allowed() -> None:
    provider = DummySTTProvider(
        supported_formats=[]
    )

    assert provider.get_supported_formats() == set()


def test_none_supported_formats_are_allowed() -> None:
    provider = DummySTTProvider(
        supported_formats=None
    )

    assert provider.get_supported_formats() == set()


def test_supported_formats_reject_string() -> None:
    with pytest.raises(STTProviderError):
        DummySTTProvider(
            supported_formats="wav"
        )


def test_supported_formats_reject_non_strings() -> None:
    with pytest.raises(STTProviderError):
        DummySTTProvider(
            supported_formats=["wav", 123]
        )


def test_supported_formats_reject_empty_values() -> None:
    with pytest.raises(STTProviderError):
        DummySTTProvider(
            supported_formats=["wav", ""]
        )


def test_supports_format_returns_true(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_format("wav") is True


def test_supports_format_is_case_insensitive(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_format(" WAV ") is True


def test_supports_format_returns_false(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_format("ogg") is False


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
    provider: DummySTTProvider,
    audio_format,
) -> None:
    with pytest.raises(STTProviderError):
        provider.supports_format(audio_format)


def test_supported_formats_are_defensive_copy(
    provider: DummySTTProvider,
) -> None:
    formats = provider.get_supported_formats()

    formats.add("ogg")

    assert "ogg" not in provider.get_supported_formats()


# ============================================================
# Capabilities
# ============================================================


def test_capabilities_are_normalized() -> None:
    provider = DummySTTProvider(
        capabilities=[
            " Transcription ",
            "TIMESTAMPS",
        ]
    )

    assert provider.get_capabilities() == {
        "transcription",
        "timestamps",
    }


def test_duplicate_capabilities_are_removed() -> None:
    provider = DummySTTProvider(
        capabilities=[
            "transcription",
            "transcription",
        ]
    )

    assert provider.get_capabilities() == {
        "transcription"
    }


def test_none_capabilities_are_allowed() -> None:
    provider = DummySTTProvider(
        capabilities=None
    )

    assert provider.get_capabilities() == set()


def test_supports_capability_returns_true(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_capability(
        "transcription"
    ) is True


def test_supports_capability_is_case_insensitive(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_capability(
        " TRANSCRIPTION "
    ) is True


def test_supports_capability_returns_false(
    provider: DummySTTProvider,
) -> None:
    assert provider.supports_capability(
        "translation"
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
    provider: DummySTTProvider,
    capability,
) -> None:
    with pytest.raises(STTProviderError):
        provider.supports_capability(capability)


def test_capabilities_are_defensive_copy(
    provider: DummySTTProvider,
) -> None:
    capabilities = provider.get_capabilities()

    capabilities.add("translation")

    assert "translation" not in provider.get_capabilities()


# ============================================================
# Configuration
# ============================================================


def test_configuration_is_initialized(
    provider: DummySTTProvider,
) -> None:
    assert provider.get_configuration(
        "language"
    ) == "en"


def test_configuration_default_is_returned(
    provider: DummySTTProvider,
) -> None:
    assert provider.get_configuration(
        "missing",
        "fallback",
    ) == "fallback"


def test_configuration_can_be_set(
    provider: DummySTTProvider,
) -> None:
    provider.set_configuration(
        "language",
        "hi",
    )

    assert provider.get_configuration(
        "language"
    ) == "hi"


def test_configuration_can_be_updated(
    provider: DummySTTProvider,
) -> None:
    provider.set_configuration(
        "temperature",
        0.5,
    )

    assert provider.get_configuration(
        "temperature"
    ) == 0.5


def test_configuration_is_defensive_copy(
    provider: DummySTTProvider,
) -> None:
    configuration = provider.get_all_configuration()

    configuration["language"] = "fr"

    assert provider.get_configuration(
        "language"
    ) == "en"


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
    provider: DummySTTProvider,
    key,
) -> None:
    with pytest.raises(STTProviderError):
        provider.get_configuration(key)


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
    provider: DummySTTProvider,
    key,
) -> None:
    with pytest.raises(STTProviderError):
        provider.set_configuration(
            key,
            "value",
        )


def test_invalid_configuration_type_raises() -> None:
    with pytest.raises(STTProviderError):
        DummySTTProvider(
            configuration=[]
        )


# ============================================================
# Metadata
# ============================================================


def test_metadata_is_initialized(
    provider: DummySTTProvider,
) -> None:
    assert provider.get_metadata(
        "version"
    ) == "0.56-test"


def test_metadata_default_is_returned(
    provider: DummySTTProvider,
) -> None:
    assert provider.get_metadata(
        "missing",
        "fallback",
    ) == "fallback"


def test_metadata_can_be_set(
    provider: DummySTTProvider,
) -> None:
    provider.set_metadata(
        "region",
        "local",
    )

    assert provider.get_metadata(
        "region"
    ) == "local"


def test_metadata_is_defensive_copy(
    provider: DummySTTProvider,
) -> None:
    metadata = provider.get_all_metadata()

    metadata["version"] = "changed"

    assert provider.get_metadata(
        "version"
    ) == "0.56-test"


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
    provider: DummySTTProvider,
    key,
) -> None:
    with pytest.raises(STTProviderError):
        provider.get_metadata(key)


def test_invalid_metadata_type_raises() -> None:
    with pytest.raises(STTProviderError):
        DummySTTProvider(
            metadata=[]
        )


# ============================================================
# Availability
# ============================================================


def test_provider_is_available_by_default() -> None:
    provider = DummySTTProvider()

    assert provider.is_available() is True


def test_available_provider_passes_validation() -> None:
    provider = DummySTTProvider(
        available=True
    )

    provider.validate_availability()


def test_unavailable_provider_fails_validation() -> None:
    provider = DummySTTProvider(
        available=False
    )

    with pytest.raises(STTProviderError):
        provider.validate_availability()


# ============================================================
# Input Validation
# ============================================================


def test_valid_input_passes_validation(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    provider.validate_input(
        voice_input
    )


def test_non_voice_input_is_rejected(
    provider: DummySTTProvider,
) -> None:
    with pytest.raises(STTProviderError):
        provider.validate_input(
            "not-a-voice-input"
        )


def test_unsupported_audio_format_is_rejected(
    provider: DummySTTProvider,
) -> None:
    voice_input = VoiceInput(
        b"audio",
        audio_format="ogg",
    )

    with pytest.raises(STTProviderError):
        provider.validate_input(
            voice_input
        )


def test_unknown_audio_format_can_pass_when_provider_has_no_restriction() -> None:
    provider = DummySTTProvider(
        supported_formats=[]
    )

    voice_input = VoiceInput(
        b"audio",
        audio_format="wav",
    )

    provider.validate_input(
        voice_input
    )


def test_missing_audio_format_can_pass(
    provider: DummySTTProvider,
) -> None:
    voice_input = VoiceInput(
        b"audio"
    )

    provider.validate_input(
        voice_input
    )


# ============================================================
# Transcription Contract
# ============================================================


def test_transcribe_returns_multimodal_result(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    result = provider.transcribe(
        voice_input
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )


def test_transcription_result_is_completed(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    result = provider.transcribe(
        voice_input
    )

    assert result.is_completed()
    assert result.is_successful()


def test_transcription_result_contains_text(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    result = provider.transcribe(
        voice_input
    )

    data = result.get_data()

    assert data["text"] == "dummy transcription"


def test_transcription_result_contains_provider_metadata(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    result = provider.transcribe(
        voice_input
    )

    data = result.get_data()

    assert data["provider"] == "Dummy STT"


def test_transcription_preserves_input_id(
    provider: DummySTTProvider,
    voice_input: VoiceInput,
) -> None:
    result = provider.transcribe(
        voice_input
    )

    assert result.input_id == voice_input.get_id()


def test_unavailable_provider_blocks_transcription(
    voice_input: VoiceInput,
) -> None:
    provider = DummySTTProvider(
        available=False
    )

    with pytest.raises(STTProviderError):
        provider.transcribe(
            voice_input
        )


def test_unsupported_input_blocks_transcription(
    provider: DummySTTProvider,
) -> None:
    voice_input = VoiceInput(
        b"audio",
        audio_format="ogg",
    )

    with pytest.raises(STTProviderError):
        provider.transcribe(
            voice_input
        )


# ============================================================
# Representation
# ============================================================


def test_repr_contains_provider_information(
    provider: DummySTTProvider,
) -> None:
    representation = repr(provider)

    assert "DummySTTProvider" in representation
    assert "Dummy STT" in representation
    assert "wav" in representation
    assert "transcription" in representation