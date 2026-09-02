"""
Tests for Ultron Voice Processing Pipeline.

v0.54 — Voice Processing Pipeline Foundation
"""

from __future__ import annotations

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processor import VoiceProcessor
from modules.multimodal.voice_processing_pipeline import (
    VoiceProcessingPipeline,
    VoiceProcessingPipelineError,
)


# ---------------------------------------------------------------------------
# Test Processor
# ---------------------------------------------------------------------------


class DummyVoiceProcessor(VoiceProcessor):
    """Simple processor used for pipeline tests."""

    def __init__(
        self,
        *,
        result_data=None,
        should_fail: bool = False,
        name: str | None = "dummy",
        metadata=None,
    ) -> None:
        super().__init__(
            name=name,
            metadata=metadata,
        )
        self.result_data = result_data
        self.should_fail = should_fail
        self.process_calls = 0

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.process_calls += 1

        if self.should_fail:
            raise RuntimeError("processor failed")

        return self.create_success_result(
            voice_input,
            self.result_data,
        )


class InvalidResultProcessor(VoiceProcessor):
    """Processor returning an invalid result."""

    def process(
        self,
        voice_input: VoiceInput,
    ):
        return "invalid-result"


class NonVoiceProcessor:
    """Object that is not a VoiceProcessor."""

    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_voice_input() -> VoiceInput:
    """Create a valid VoiceInput for tests."""

    return VoiceInput(
        audio_data=b"test-audio",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=1.0,
    )


# ---------------------------------------------------------------------------
# Initialization Tests
# ---------------------------------------------------------------------------


def test_pipeline_initializes_with_valid_processor():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    assert pipeline.get_processor() is processor
    assert pipeline.get_name() is None
    assert pipeline.get_all_metadata() == {}


def test_pipeline_accepts_name():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
        name="voice-pipeline",
    )

    assert pipeline.get_name() == "voice-pipeline"


def test_pipeline_accepts_metadata():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
        metadata={
            "environment": "test",
            "version": "v0.54",
        },
    )

    assert pipeline.get_metadata("environment") == "test"
    assert pipeline.get_metadata("version") == "v0.54"


def test_pipeline_rejects_invalid_processor():
    with pytest.raises(VoiceProcessingPipelineError):
        VoiceProcessingPipeline(
            NonVoiceProcessor(),
        )


def test_pipeline_rejects_none_processor():
    with pytest.raises(VoiceProcessingPipelineError):
        VoiceProcessingPipeline(
            None,
        )


def test_pipeline_rejects_invalid_name_type():
    processor = DummyVoiceProcessor()

    with pytest.raises(VoiceProcessingPipelineError):
        VoiceProcessingPipeline(
            processor,
            name=123,
        )


def test_pipeline_rejects_empty_name():
    processor = DummyVoiceProcessor()

    with pytest.raises(VoiceProcessingPipelineError):
        VoiceProcessingPipeline(
            processor,
            name="   ",
        )


def test_pipeline_rejects_invalid_metadata():
    processor = DummyVoiceProcessor()

    with pytest.raises(VoiceProcessingPipelineError):
        VoiceProcessingPipeline(
            processor,
            metadata="invalid",
        )


# ---------------------------------------------------------------------------
# Voice Input Validation
# ---------------------------------------------------------------------------


def test_pipeline_rejects_invalid_voice_input_type():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.process("invalid")


def test_pipeline_rejects_none_voice_input():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.process(None)


# ---------------------------------------------------------------------------
# Processing Tests
# ---------------------------------------------------------------------------


def test_pipeline_processes_valid_voice_input():
    processor = DummyVoiceProcessor(
        result_data={
            "text": "hello ultron",
        }
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.status == "completed"
    assert result.input_id == voice_input.get_id()
    assert result.input_type == InputType.VOICE
    assert result.get_data() == {
        "text": "hello ultron",
    }


def test_pipeline_calls_processor_once():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    pipeline.process(
        voice_input,
    )

    assert processor.process_calls == 1


def test_pipeline_returns_processor_result():
    processor = DummyVoiceProcessor(
        result_data="processed",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert result.get_data() == "processed"


def test_pipeline_handles_processor_failure():
    processor = DummyVoiceProcessor(
        should_fail=True,
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.status == "failed"
    assert "processor failed" in result.error


def test_pipeline_isolates_processor_exception():
    processor = DummyVoiceProcessor(
        should_fail=True,
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert result.status == "failed"


def test_pipeline_rejects_invalid_processor_result():
    processor = InvalidResultProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.status == "failed"
    assert "invalid result" in result.error.lower()


# ---------------------------------------------------------------------------
# Processor Management
# ---------------------------------------------------------------------------


def test_get_processor_returns_active_processor():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    assert pipeline.get_processor() is processor


def test_set_processor_replaces_processor():
    first_processor = DummyVoiceProcessor(
        name="first",
    )

    second_processor = DummyVoiceProcessor(
        name="second",
    )

    pipeline = VoiceProcessingPipeline(
        first_processor,
    )

    pipeline.set_processor(
        second_processor,
    )

    assert pipeline.get_processor() is second_processor
    assert pipeline.get_processor_name() == "second"


def test_set_processor_rejects_invalid_processor():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.set_processor(
            NonVoiceProcessor(),
        )


# ---------------------------------------------------------------------------
# Processor Identity
# ---------------------------------------------------------------------------


def test_get_processor_name():
    processor = DummyVoiceProcessor(
        name="test-processor",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    assert pipeline.get_processor_name() == "test-processor"


# ---------------------------------------------------------------------------
# Metadata Tests
# ---------------------------------------------------------------------------


def test_set_metadata():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    pipeline.set_metadata(
        "provider",
        "future-stt",
    )

    assert pipeline.get_metadata(
        "provider",
    ) == "future-stt"


def test_get_metadata_default():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    assert pipeline.get_metadata(
        "missing",
    ) is None

    assert pipeline.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_get_all_metadata_returns_copy():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
        metadata={
            "provider": "test",
        },
    )

    metadata = pipeline.get_all_metadata()

    metadata["provider"] = "changed"

    assert pipeline.get_metadata(
        "provider",
    ) == "test"


def test_set_metadata_rejects_non_string_key():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.set_metadata(
            123,
            "value",
        )


def test_set_metadata_rejects_empty_key():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.set_metadata(
            "   ",
            "value",
        )


def test_get_metadata_rejects_non_string_key():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.get_metadata(
            123,
        )


def test_get_metadata_rejects_empty_key():
    processor = DummyVoiceProcessor()
    pipeline = VoiceProcessingPipeline(processor)

    with pytest.raises(VoiceProcessingPipelineError):
        pipeline.get_metadata(
            "   ",
        )


# ---------------------------------------------------------------------------
# Representation
# ---------------------------------------------------------------------------


def test_pipeline_repr():
    processor = DummyVoiceProcessor(
        name="dummy",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
        name="voice-pipeline",
    )

    representation = repr(pipeline)

    assert "VoiceProcessingPipeline" in representation
    assert "voice-pipeline" in representation
    assert "dummy" in representation


# ---------------------------------------------------------------------------
# Multiple Processing Calls
# ---------------------------------------------------------------------------


def test_pipeline_can_process_multiple_inputs():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    first_input = make_voice_input()
    second_input = make_voice_input()

    first_result = pipeline.process(
        first_input,
    )

    second_result = pipeline.process(
        second_input,
    )

    assert first_result.status == "completed"
    assert second_result.status == "completed"

    assert processor.process_calls == 2


# ---------------------------------------------------------------------------
# Result Isolation
# ---------------------------------------------------------------------------


def test_pipeline_does_not_replace_processor():
    processor = DummyVoiceProcessor()

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    pipeline.process(
        voice_input,
    )

    assert pipeline.get_processor() is processor