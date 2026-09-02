"""
Integration tests for Ultron Voice Processing Pipeline.

v0.54 — Voice Processing Pipeline Foundation
"""

from __future__ import annotations

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processor import VoiceProcessor
from modules.multimodal.voice_processing_pipeline import (
    VoiceProcessingPipeline,
)


# ---------------------------------------------------------------------------
# Integration Test Processor
# ---------------------------------------------------------------------------


class IntegrationVoiceProcessor(VoiceProcessor):
    """Processor used to validate the complete voice pipeline flow."""

    def __init__(
        self,
        *,
        result_data=None,
        should_fail: bool = False,
    ) -> None:
        super().__init__(
            name="integration-processor",
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
            raise RuntimeError(
                "integration processor failed"
            )

        return self.create_success_result(
            voice_input,
            self.result_data,
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_voice_input(
    *,
    audio_data: bytes = b"integration-audio",
) -> VoiceInput:
    """Create a valid voice input for integration tests."""

    return VoiceInput(
        audio_data=audio_data,
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=1.5,
        metadata={
            "source": "integration-test",
        },
    )


# ---------------------------------------------------------------------------
# End-to-End Pipeline Tests
# ---------------------------------------------------------------------------


def test_voice_input_flows_through_complete_pipeline():
    processor = IntegrationVoiceProcessor(
        result_data={
            "text": "hello ultron",
        },
    )

    pipeline = VoiceProcessingPipeline(
        processor,
        name="integration-pipeline",
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_id == voice_input.get_id()
    assert result.input_type == InputType.VOICE
    assert result.status == "completed"
    assert result.success is True

    assert result.get_data() == {
        "text": "hello ultron",
    }

    assert processor.process_calls == 1


def test_pipeline_preserves_voice_input_identity():
    processor = IntegrationVoiceProcessor(
        result_data="processed",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    voice_input = make_voice_input()

    result = pipeline.process(
        voice_input,
    )

    assert result.input_id == voice_input.get_id()


def test_pipeline_produces_standardized_result():
    processor = IntegrationVoiceProcessor(
        result_data={
            "text": "ultron response",
            "language": "en",
        },
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    result = pipeline.process(
        make_voice_input(),
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.input_type is InputType.VOICE
    assert result.status == "completed"
    assert result.get_data()["text"] == "ultron response"
    assert result.get_data()["language"] == "en"


def test_pipeline_handles_processor_exception_without_leaking():
    processor = IntegrationVoiceProcessor(
        should_fail=True,
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    result = pipeline.process(
        make_voice_input(),
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )

    assert result.status == "failed"
    assert result.success is False
    assert result.has_error()
    assert (
        result.get_error()
        == "integration processor failed"
    )


def test_pipeline_can_process_multiple_voice_inputs():
    processor = IntegrationVoiceProcessor(
        result_data="processed",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    first_input = make_voice_input(
        audio_data=b"audio-one",
    )

    second_input = make_voice_input(
        audio_data=b"audio-two",
    )

    first_result = pipeline.process(
        first_input,
    )

    second_result = pipeline.process(
        second_input,
    )

    assert first_result.status == "completed"
    assert second_result.status == "completed"

    assert first_result.input_id == first_input.get_id()
    assert second_result.input_id == second_input.get_id()

    assert first_result.get_data() == "processed"
    assert second_result.get_data() == "processed"

    assert processor.process_calls == 2


def test_pipeline_processor_can_be_replaced_during_integration_flow():
    first_processor = IntegrationVoiceProcessor(
        result_data="first-result",
    )

    second_processor = IntegrationVoiceProcessor(
        result_data="second-result",
    )

    pipeline = VoiceProcessingPipeline(
        first_processor,
    )

    first_result = pipeline.process(
        make_voice_input(
            audio_data=b"first-audio",
        ),
    )

    pipeline.set_processor(
        second_processor,
    )

    second_result = pipeline.process(
        make_voice_input(
            audio_data=b"second-audio",
        ),
    )

    assert first_result.get_data() == "first-result"
    assert second_result.get_data() == "second-result"

    assert first_processor.process_calls == 1
    assert second_processor.process_calls == 1


def test_pipeline_metadata_remains_available_during_processing():
    processor = IntegrationVoiceProcessor(
        result_data="processed",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
        metadata={
            "pipeline_version": "v0.54",
            "environment": "integration",
        },
    )

    result = pipeline.process(
        make_voice_input(),
    )

    assert result.status == "completed"

    assert pipeline.get_metadata(
        "pipeline_version",
    ) == "v0.54"

    assert pipeline.get_metadata(
        "environment",
    ) == "integration"


def test_pipeline_result_data_isolated_from_processor_configuration():
    processor = IntegrationVoiceProcessor(
        result_data={
            "text": "original",
        },
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    result = pipeline.process(
        make_voice_input(),
    )

    data = result.get_data()

    data["text"] = "modified"

    assert result.get_data() == {
        "text": "original",
    }


def test_pipeline_preserves_result_lifecycle():
    processor = IntegrationVoiceProcessor(
        result_data="completed-data",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    result = pipeline.process(
        make_voice_input(),
    )

    assert result.is_completed()
    assert result.is_terminal()
    assert result.is_successful()
    assert not result.is_failed()


def test_pipeline_keeps_processor_isolated():
    processor = IntegrationVoiceProcessor(
        result_data="isolated",
    )

    pipeline = VoiceProcessingPipeline(
        processor,
    )

    pipeline.process(
        make_voice_input(),
    )

    assert pipeline.get_processor() is processor
    assert processor.process_calls == 1