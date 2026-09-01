"""
Ultron Voice Processor Integration Tests.

v0.53 — Voice Processing Foundation

Integration tests for the VoiceInput -> VoiceProcessor ->
MultimodalInputResult processing boundary.

These tests intentionally do not depend on a concrete STT
provider. They verify the processing architecture and lifecycle.
"""

from __future__ import annotations

from typing import Any

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
# Test Processors
# ============================================================


class SuccessfulVoiceProcessor(VoiceProcessor):
    """Processor that simulates successful voice processing."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        return self.create_success_result(
            voice_input,
            data={
                "text": "hello world",
                "confidence": 0.97,
            },
        )


class FailingVoiceProcessor(VoiceProcessor):
    """Processor that simulates a failed processing operation."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        return self.create_failure_result(
            voice_input,
            "Speech processing failed.",
        )


class AudioEchoProcessor(VoiceProcessor):
    """Processor that returns the original audio payload."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        return self.create_success_result(
            voice_input,
            data=voice_input.get_audio_data(),
        )


class MetadataProcessor(VoiceProcessor):
    """Processor that exposes processor metadata in its result."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        result = self.create_success_result(
            voice_input,
            data="processed",
        )

        result.set_metadata(
            "processor_name",
            self.get_name(),
        )

        result.set_metadata(
            "processor_metadata",
            self.get_all_metadata(),
        )

        return result


class ExceptionVoiceProcessor(VoiceProcessor):
    """Processor used to verify exception boundaries."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.validate_input(voice_input)

        raise RuntimeError(
            "Simulated processor failure."
        )


# ============================================================
# Fixtures
# ============================================================


@pytest.fixture
def voice_input() -> VoiceInput:
    """Return a valid voice input."""

    return VoiceInput(
        b"integration-audio",
        input_id="voice-integration-001",
        source="integration-test",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=3.2,
        metadata={
            "language": "en",
            "test": True,
        },
    )


@pytest.fixture
def successful_processor() -> SuccessfulVoiceProcessor:
    """Return a successful processor."""

    return SuccessfulVoiceProcessor(
        name="successful-processor",
    )


@pytest.fixture
def failing_processor() -> FailingVoiceProcessor:
    """Return a failing processor."""

    return FailingVoiceProcessor(
        name="failing-processor",
    )


# ============================================================
# Successful Processing
# ============================================================


def test_voice_input_to_processor_to_result(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Voice input must successfully pass through the processor."""

    result = successful_processor.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "completed"
    assert result.success is True


def test_successful_processing_contains_processed_data(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Successful processing must expose processed data."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.data == {
        "text": "hello world",
        "confidence": 0.97,
    }


def test_successful_processing_is_terminal(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Completed processing must produce a terminal result."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.is_completed()
    assert result.is_terminal()
    assert result.is_successful()
    assert result.is_unsuccessful() is False


# ============================================================
# Failure Processing
# ============================================================


def test_failed_processing_returns_result(
    failing_processor: FailingVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Processing failures must be represented by a result."""

    result = failing_processor.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type is InputType.VOICE
    assert result.status == "failed"
    assert result.success is False


def test_failed_processing_contains_error(
    failing_processor: FailingVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Failed processing must preserve its error."""

    result = failing_processor.process(
        voice_input,
    )

    assert result.error == (
        "Speech processing failed."
    )

    assert result.has_error()
    assert result.is_failed()
    assert result.is_terminal()


# ============================================================
# Identity Preservation
# ============================================================


def test_input_id_is_preserved_across_processing(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """The original voice input ID must reach the result."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.input_id == (
        voice_input.get_id()
    )


def test_voice_type_is_preserved_across_processing(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """The VOICE input type must reach the result."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.input_type is InputType.VOICE


# ============================================================
# Audio Payload Propagation
# ============================================================


def test_audio_payload_can_be_consumed_by_processor(
    voice_input: VoiceInput,
) -> None:
    """Processors must be able to consume VoiceInput audio data."""

    processor = AudioEchoProcessor(
        name="audio-echo",
    )

    result = processor.process(
        voice_input,
    )

    assert result.status == "completed"
    assert result.data == b"integration-audio"


def test_audio_payload_is_not_modified(
    voice_input: VoiceInput,
) -> None:
    """Processing must not mutate the original audio payload."""

    original_audio = voice_input.get_audio_data()

    processor = AudioEchoProcessor(
        name="audio-echo",
    )

    processor.process(
        voice_input,
    )

    assert voice_input.get_audio_data() == (
        original_audio
    )


# ============================================================
# Voice Metadata
# ============================================================


def test_voice_metadata_remains_available(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Voice metadata must remain available to processing."""

    assert voice_input.get_metadata(
        "language",
    ) == "en"

    assert voice_input.get_metadata(
        "test",
    ) is True

    result = successful_processor.process(
        voice_input,
    )

    assert result.input_id == voice_input.get_id()


def test_processor_metadata_can_be_attached_to_result(
    voice_input: VoiceInput,
) -> None:
    """Processor metadata can be propagated into a result."""

    processor = MetadataProcessor(
        name="metadata-processor",
        metadata={
            "provider": "test",
            "version": "0.53",
        },
    )

    result = processor.process(
        voice_input,
    )

    assert result.status == "completed"

    assert result.get_metadata(
        "processor_name",
    ) == "metadata-processor"

    assert result.get_metadata(
        "processor_metadata",
    ) == {
        "provider": "test",
        "version": "0.53",
    }


# ============================================================
# Validation Boundary
# ============================================================


@pytest.mark.parametrize(
    "invalid_input",
    [
        None,
        "invalid",
        b"audio",
        123,
        {},
        [],
    ],
)
def test_processor_rejects_invalid_input(
    successful_processor: SuccessfulVoiceProcessor,
    invalid_input: Any,
) -> None:
    """Processors must reject non-VoiceInput values."""

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input must be a VoiceInput instance",
    ):
        successful_processor.process(
            invalid_input,
        )


def test_processor_rejects_invalid_voice_state(
    successful_processor: SuccessfulVoiceProcessor,
) -> None:
    """Processors must reject invalid VoiceInput state."""

    voice = VoiceInput(
        b"audio",
    )

    voice.audio_data = None

    with pytest.raises(
        VoiceProcessorError,
        match="voice_input is invalid",
    ):
        successful_processor.process(
            voice,
        )


# ============================================================
# Result Lifecycle
# ============================================================


def test_successful_result_has_completed_timestamp(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Completed results must receive a completion timestamp."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.completed_at is not None


def test_failed_result_has_completed_timestamp(
    failing_processor: FailingVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Failed results must receive a completion timestamp."""

    result = failing_processor.process(
        voice_input,
    )

    assert result.completed_at is not None


def test_successful_result_has_no_error(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Successful results must not contain an error."""

    result = successful_processor.process(
        voice_input,
    )

    assert result.error is None
    assert result.has_error() is False


def test_failed_result_is_unsuccessful(
    failing_processor: FailingVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Failed results must be unsuccessful."""

    result = failing_processor.process(
        voice_input,
    )

    assert result.is_unsuccessful()
    assert result.is_successful() is False


# ============================================================
# Processor Identity
# ============================================================


def test_processor_name_is_available(
    successful_processor: SuccessfulVoiceProcessor,
) -> None:
    """Processor identity must remain accessible."""

    assert successful_processor.get_name() == (
        "successful-processor"
    )


def test_different_processors_can_process_same_input(
    voice_input: VoiceInput,
) -> None:
    """Multiple processors must be independently usable."""

    success_processor = SuccessfulVoiceProcessor(
        name="success",
    )

    echo_processor = AudioEchoProcessor(
        name="echo",
    )

    success_result = success_processor.process(
        voice_input,
    )

    echo_result = echo_processor.process(
        voice_input,
    )

    assert success_result.input_id == (
        voice_input.get_id()
    )

    assert echo_result.input_id == (
        voice_input.get_id()
    )

    assert success_result.data != (
        echo_result.data
    )


# ============================================================
# Exception Boundary
# ============================================================


def test_processor_exception_is_not_silently_converted(
    voice_input: VoiceInput,
) -> None:
    """
    Unexpected processor exceptions must remain visible.

    The foundation does not yet define a global runtime
    exception adapter, so provider/runtime exceptions should
    not be silently swallowed here.
    """

    processor = ExceptionVoiceProcessor(
        name="exception-processor",
    )

    with pytest.raises(
        RuntimeError,
        match="Simulated processor failure",
    ):
        processor.process(
            voice_input,
        )


# ============================================================
# Serialization
# ============================================================


def test_success_result_can_be_serialized(
    successful_processor: SuccessfulVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Processed voice results must remain serializable."""

    result = successful_processor.process(
        voice_input,
    )

    serialized = result.to_dict()

    assert serialized["input_id"] == (
        voice_input.get_id()
    )

    assert serialized["input_type"] == (
        InputType.VOICE.value
    )

    assert serialized["status"] == "completed"

    assert serialized["success"] is True

    assert serialized["data"] == {
        "text": "hello world",
        "confidence": 0.97,
    }


def test_failed_result_can_be_serialized(
    failing_processor: FailingVoiceProcessor,
    voice_input: VoiceInput,
) -> None:
    """Failed voice results must remain serializable."""

    result = failing_processor.process(
        voice_input,
    )

    serialized = result.to_dict()

    assert serialized["input_id"] == (
        voice_input.get_id()
    )

    assert serialized["input_type"] == (
        InputType.VOICE.value
    )

    assert serialized["status"] == "failed"

    assert serialized["success"] is False

    assert serialized["error"] == (
        "Speech processing failed."
    )


# ============================================================
# End-to-End Foundation Flow
# ============================================================


def test_end_to_end_voice_processing_foundation(
    voice_input: VoiceInput,
) -> None:
    """
    Verify the complete v0.53 foundation flow.

    VoiceInput
        -> VoiceProcessor
        -> MultimodalInputResult
    """

    processor = SuccessfulVoiceProcessor(
        name="e2e-processor",
    )

    assert voice_input.is_voice()
    assert voice_input.is_valid()

    result = processor.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == (
        voice_input.get_id()
    )

    assert result.input_type is InputType.VOICE

    assert result.status == "completed"

    assert result.success is True

    assert result.data == {
        "text": "hello world",
        "confidence": 0.97,
    }

    assert result.is_terminal()
