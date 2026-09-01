"""
Tests for Ultron Voice Processor.

v0.53 — Voice Processing Foundation
"""

from __future__ import annotations

from abc import ABC

import pytest

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processor import (
    VoiceProcessor,
    VoiceProcessorError,
)


# ============================================================
# Test Processor Implementations
# ============================================================


class ConcreteVoiceProcessor(VoiceProcessor):
    """Concrete processor used for testing the abstract contract."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        return self.create_success_result(
            voice_input,
            data="processed",
        )


class EchoVoiceProcessor(VoiceProcessor):
    """Processor that returns the supplied audio data."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        return self.create_success_result(
            voice_input,
            data=voice_input.get_audio_data(),
        )


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def voice_input() -> VoiceInput:
    """Return a valid VoiceInput instance."""

    return VoiceInput(
        b"test-audio",
        input_id="voice-test-001",
        source="test",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=2.5,
        metadata={
            "language": "en",
        },
    )


@pytest.fixture
def processor() -> ConcreteVoiceProcessor:
    """Return a concrete VoiceProcessor implementation."""

    return ConcreteVoiceProcessor(
        name="test-processor",
        metadata={
            "provider": "test",
        },
    )


# ============================================================
# Abstract Contract
# ============================================================


def test_voice_processor_is_abstract() -> None:
    """VoiceProcessor must remain an abstract base class."""

    assert issubclass(
        VoiceProcessor,
        ABC,
    )

    assert VoiceProcessor.__abstractmethods__ == {
        "process",
    }


def test_voice_processor_cannot_be_instantiated_directly() -> None:
    """Direct VoiceProcessor instantiation must fail."""

    with pytest.raises(
        TypeError,
    ):
        VoiceProcessor()


# ============================================================
# Initialization
# ============================================================


def test_processor_initialization(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Processor initializes with name and metadata."""

    assert processor.name == "test-processor"
    assert processor.get_name() == "test-processor"

    assert processor.metadata == {
        "provider": "test",
    }


def test_processor_initialization_without_name() -> None:
    """Processor name may be omitted."""

    processor = ConcreteVoiceProcessor()

    assert processor.name is None
    assert processor.get_name() is None


def test_processor_initialization_without_metadata() -> None:
    """Processor metadata defaults to an empty dictionary."""

    processor = ConcreteVoiceProcessor()

    assert processor.metadata == {}


def test_processor_rejects_non_string_name() -> None:
    """Processor must reject non-string names."""

    with pytest.raises(
        VoiceProcessorError,
        match="name must be a string or None",
    ):
        ConcreteVoiceProcessor(
            name=123,
        )


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "   ",
    ],
)
def test_processor_rejects_empty_name(
    name: str,
) -> None:
    """Processor must reject empty names."""

    with pytest.raises(
        VoiceProcessorError,
        match="name cannot be empty",
    ):
        ConcreteVoiceProcessor(
            name=name,
        )


def test_processor_rejects_non_dict_metadata() -> None:
    """Processor must reject non-dictionary metadata."""

    with pytest.raises(
        VoiceProcessorError,
        match="metadata must be a dictionary or None",
    ):
        ConcreteVoiceProcessor(
            metadata="invalid",
        )


# ============================================================
# Metadata
# ============================================================


def test_set_metadata(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Processor metadata can be added."""

    processor.set_metadata(
        "language",
        "en",
    )

    assert processor.get_metadata(
        "language",
    ) == "en"


def test_set_metadata_overwrites_existing_value(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Existing metadata values can be replaced."""

    processor.set_metadata(
        "provider",
        "new-provider",
    )

    assert processor.get_metadata(
        "provider",
    ) == "new-provider"


def test_set_metadata_accepts_any_value(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Metadata values may contain arbitrary objects."""

    value = {
        "nested": True,
    }

    processor.set_metadata(
        "config",
        value,
    )

    assert processor.get_metadata(
        "config",
    ) == value


def test_set_metadata_rejects_non_string_key(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Metadata keys must be strings."""

    with pytest.raises(
        VoiceProcessorError,
        match="Metadata key must be a string",
    ):
        processor.set_metadata(
            123,
            "value",
        )


@pytest.mark.parametrize(
    "key",
    [
        "",
        " ",
        "   ",
    ],
)
def test_set_metadata_rejects_empty_key(
    processor: ConcreteVoiceProcessor,
    key: str,
) -> None:
    """Metadata keys cannot be empty."""

    with pytest.raises(
        VoiceProcessorError,
        match="Metadata key cannot be empty",
    ):
        processor.set_metadata(
            key,
            "value",
        )


def test_get_metadata_returns_default(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Missing metadata returns the supplied default."""

    assert processor.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_get_metadata_defaults_to_none(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Missing metadata defaults to None."""

    assert processor.get_metadata(
        "missing",
    ) is None


def test_get_metadata_rejects_non_string_key(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Metadata lookup keys must be strings."""

    with pytest.raises(
        VoiceProcessorError,
        match="Metadata key must be a string",
    ):
        processor.get_metadata(
            123,
        )


@pytest.mark.parametrize(
    "key",
    [
        "",
        " ",
        "   ",
    ],
)
def test_get_metadata_rejects_empty_key(
    processor: ConcreteVoiceProcessor,
    key: str,
) -> None:
    """Metadata lookup keys cannot be empty."""

    with pytest.raises(
        VoiceProcessorError,
        match="Metadata key cannot be empty",
    ):
        processor.get_metadata(
            key,
        )


def test_get_all_metadata_returns_copy(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Metadata retrieval must be defensive."""

    metadata = processor.get_all_metadata()

    metadata["provider"] = "modified"
    metadata["new"] = True

    assert processor.get_metadata(
        "provider",
    ) == "test"

    assert processor.get_metadata(
        "new",
    ) is None


def test_nested_metadata_is_defensive_copy(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Nested metadata should also be protected."""

    processor.set_metadata(
        "config",
        {
            "enabled": True,
        },
    )

    metadata = processor.get_all_metadata()

    metadata["config"]["enabled"] = False

    assert processor.get_metadata(
        "config",
    ) == {
        "enabled": True,
    }


def test_initial_metadata_is_defensively_copied() -> None:
    """Constructor must defensively copy metadata."""

    metadata = {
        "provider": "test",
        "config": {
            "enabled": True,
        },
    }

    processor = ConcreteVoiceProcessor(
        metadata=metadata,
    )

    metadata["provider"] = "changed"
    metadata["config"]["enabled"] = False

    assert processor.get_metadata(
        "provider",
    ) == "test"

    assert processor.get_metadata(
        "config",
    ) == {
        "enabled": True,
    }


# ============================================================
# Input Validation
# ============================================================


def test_validate_input_accepts_valid_voice_input(
    voice_input: VoiceInput,
) -> None:
    """Valid VoiceInput must pass validation."""

    VoiceProcessor.validate_input(
        voice_input,
    )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "voice",
        b"audio",
        123,
        {},
        [],
    ],
)
def test_validate_input_rejects_invalid_object(
    value: object,
) -> None:
    """Non-VoiceInput objects must be rejected."""

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input must be a VoiceInput instance",
    ):
        VoiceProcessor.validate_input(
            value,
        )


def test_validate_input_rejects_invalid_voice_input() -> None:
    """Invalid VoiceInput state must be rejected."""

    voice = VoiceInput(
        b"audio",
    )

    voice.audio_data = None

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input is invalid",
    ):
        VoiceProcessor.validate_input(
            voice,
        )


# ============================================================
# Processing Result
# ============================================================


def test_create_processing_result(
    voice_input: VoiceInput,
) -> None:
    """Processing result must contain voice identity and type."""

    result = VoiceProcessor.create_processing_result(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "processing"


def test_create_processing_result_rejects_invalid_input() -> None:
    """Processing result creation must validate input."""

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input must be a VoiceInput instance",
    ):
        VoiceProcessor.create_processing_result(
            "invalid",
        )


# ============================================================
# Success Result
# ============================================================


def test_create_success_result(
    voice_input: VoiceInput,
) -> None:
    """Successful result must contain processed data."""

    result = VoiceProcessor.create_success_result(
        voice_input,
        data="hello world",
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "completed"

    assert result.data == "hello world"


def test_create_success_result_supports_none_data(
    voice_input: VoiceInput,
) -> None:
    """Successful processing may return None."""

    result = VoiceProcessor.create_success_result(
        voice_input,
    )

    assert result.status == "completed"
    assert result.data is None


def test_create_success_result_supports_complex_data(
    voice_input: VoiceInput,
) -> None:
    """Successful result may contain structured data."""

    data = {
        "text": "hello",
        "confidence": 0.97,
    }

    result = VoiceProcessor.create_success_result(
        voice_input,
        data=data,
    )

    assert result.status == "completed"
    assert result.data == data


# ============================================================
# Failure Result
# ============================================================


def test_create_failure_result(
    voice_input: VoiceInput,
) -> None:
    """Failed result must contain the supplied error."""

    result = VoiceProcessor.create_failure_result(
        voice_input,
        "Speech processing failed.",
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "failed"
    assert result.error == "Speech processing failed."


def test_create_failure_result_rejects_non_string_error(
    voice_input: VoiceInput,
) -> None:
    """Failure errors must be strings."""

    with pytest.raises(
        VoiceProcessorError,
        match="error must be a string",
    ):
        VoiceProcessor.create_failure_result(
            voice_input,
            123,
        )


@pytest.mark.parametrize(
    "error",
    [
        "",
        " ",
        "   ",
    ],
)
def test_create_failure_result_rejects_empty_error(
    voice_input: VoiceInput,
    error: str,
) -> None:
    """Failure errors cannot be empty."""

    with pytest.raises(
        VoiceProcessorError,
        match="error cannot be empty",
    ):
        VoiceProcessor.create_failure_result(
            voice_input,
            error,
        )


# ============================================================
# Concrete Processing Contract
# ============================================================


def test_process_returns_standardized_result(
    processor: ConcreteVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Concrete processor must return MultimodalInputResult."""

    result = processor.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "completed"
    assert result.data == "processed"


def test_process_validates_input(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Concrete processor should validate its input."""

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input must be a VoiceInput instance",
    ):
        processor.process(
            "invalid",
        )


def test_echo_processor_preserves_audio_data(
    voice_input: VoiceInput,
) -> None:
    """Concrete processors can consume VoiceInput data."""

    processor = EchoVoiceProcessor(
        name="echo",
    )

    result = processor.process(
        voice_input,
    )

    assert result.status == "completed"
    assert result.data == b"test-audio"


# ============================================================
# Input Identity Preservation
# ============================================================


def test_processing_result_preserves_input_id(
    voice_input: VoiceInput,
) -> None:
    """Result must preserve the original input ID."""

    result = VoiceProcessor.create_success_result(
        voice_input,
        "processed",
    )

    assert result.input_id == "voice-test-001"


def test_processing_result_preserves_voice_type(
    voice_input: VoiceInput,
) -> None:
    """Result must preserve VOICE input type."""

    result = VoiceProcessor.create_success_result(
        voice_input,
        "processed",
    )

    assert result.input_type is InputType.VOICE


# ============================================================
# Representation
# ============================================================


def test_processor_repr(
    processor: ConcreteVoiceProcessor,
) -> None:
    """Processor representation should be developer-friendly."""

    representation = repr(
        processor,
    )

    assert representation == (
        "ConcreteVoiceProcessor("
        "name='test-processor'"
        ")" 
    )


def test_processor_repr_without_name() -> None:
    """Representation must support processors without names."""

    processor = ConcreteVoiceProcessor()

    assert repr(
        processor,
    ) == (
        "ConcreteVoiceProcessor("
        "name=None"
        ")"
    )


# ============================================================
# Public Exports
# ============================================================


def test_public_exports() -> None:
    """Public module exports must remain available."""

    import modules.multimodal.voice_processor as module

    assert hasattr(
        module,
        "VoiceProcessor",
    )

    assert hasattr(
        module,
        "VoiceProcessorError",
    )

    assert module.__all__ == [
        "VoiceProcessor",
        "VoiceProcessorError",
    ]
