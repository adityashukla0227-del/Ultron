"""
Voice → Runtime Integration Tests.

Ultron v0.58 — Voice → Text Runtime Integration
"""

from unittest.mock import Mock

import pytest

from modules.agent.agent import Agent
from modules.agent.agent_runtime_context import (
    AgentRuntimeContext,
)
from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.providers.openai_voice_processor import (
    OpenAIVoiceProcessor,
)
from modules.multimodal.stt_provider import (
    STTProvider,
)
from modules.multimodal.voice_input import (
    VoiceInput,
)
from modules.multimodal.voice_processing_pipeline import (
    VoiceProcessingPipeline,
)
from modules.multimodal.voice_runtime_integration import (
    VoiceRuntimeIntegration,
    VoiceRuntimeIntegrationError,
)


# ============================================================
# Test Helpers
# ============================================================


class MockSTTProvider(STTProvider):
    """Mock STT provider for integration tests."""

    def __init__(
        self,
        *,
        text: str = "open Chrome",
        should_fail: bool = False,
    ) -> None:
        super().__init__(
            name="mock-stt",
            supported_formats={
                "wav",
                "mp3",
                "m4a",
                "ogg",
                "flac",
                "webm",
            },
            capabilities={
                "transcription",
                "speech_to_text",
            },
        )

        self.text = text
        self.should_fail = should_fail
        self.transcribe_calls = 0

    def is_available(self) -> bool:
        return True

    def transcribe(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self.transcribe_calls += 1

        result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=voice_input.input_type,
        )

        if self.should_fail:
            result.fail(
                error="Mock STT failure."
            )
            return result

        result.complete(
            data=self.text,
            confidence=0.95,
        )

        result.set_metadata(
            "provider",
            self.get_name(),
        )

        return result


def create_agent() -> Agent:
    """Create a minimal valid Agent instance."""

    return Agent(
        name="TestAgent",
    )


def create_voice_input() -> VoiceInput:
    """Create a valid test VoiceInput."""

    return VoiceInput(
        audio_data=b"fake-audio-data",
        input_id="voice-test-001",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=1.5,
    )


def create_integration(
    *,
    text: str = "open Chrome",
    should_fail: bool = False,
):
    """Create a complete test integration stack."""

    provider = MockSTTProvider(
        text=text,
        should_fail=should_fail,
    )

    processor = OpenAIVoiceProcessor(
        stt_provider=provider,
    )

    pipeline = VoiceProcessingPipeline(
        processor=processor,
    )

    context = AgentRuntimeContext(
        agent=create_agent(),
    )

    integration = VoiceRuntimeIntegration(
        pipeline=pipeline,
        context=context,
    )

    return (
        integration,
        context,
        provider,
    )


# ============================================================
# Initialization
# ============================================================


def test_initialization() -> None:
    """Integration should initialize with valid dependencies."""

    integration, context, provider = create_integration()

    assert isinstance(
        integration,
        VoiceRuntimeIntegration,
    )

    assert integration.get_context() is context

    assert integration.get_pipeline() is not None

    assert (
        integration.get_name()
        == "voice-runtime-integration"
    )

    assert (
        integration.get_pipeline()
        .get_processor()
        .get_stt_provider()
        is provider
    )


def test_invalid_pipeline_rejected() -> None:
    """Invalid pipeline should be rejected."""

    context = AgentRuntimeContext(
        agent=create_agent(),
    )

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        VoiceRuntimeIntegration(
            pipeline=Mock(),
            context=context,
        )


def test_invalid_context_rejected() -> None:
    """Invalid runtime context should be rejected."""

    provider = MockSTTProvider()

    processor = OpenAIVoiceProcessor(
        stt_provider=provider,
    )

    pipeline = VoiceProcessingPipeline(
        processor=processor,
    )

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        VoiceRuntimeIntegration(
            pipeline=pipeline,
            context=Mock(),
        )


# ============================================================
# Successful Voice → Text → Runtime Flow
# ============================================================


def test_process_voice_updates_runtime_query() -> None:
    """Successful transcription should become runtime query."""

    integration, context, provider = create_integration(
        text="open Chrome",
    )

    voice_input = create_voice_input()

    result = integration.process_voice(
        voice_input
    )

    assert result.is_successful()

    assert result.get_data() == "open Chrome"

    assert context.get_query() == "open Chrome"

    assert context.status == "ready"

    assert provider.transcribe_calls == 1


def test_process_voice_preserves_confidence() -> None:
    """Transcription confidence should be preserved."""

    integration, context, _ = create_integration()

    result = integration.process_voice(
        create_voice_input()
    )

    assert result.is_successful()

    assert result.confidence == 0.95

    assert context.get_query() == "open Chrome"


def test_process_voice_adds_runtime_metadata() -> None:
    """Runtime integration metadata should be attached."""

    integration, context, _ = create_integration()

    result = integration.process_voice(
        create_voice_input()
    )

    assert result.is_successful()

    assert (
        result.get_metadata(
            "runtime_context_id"
        )
        == context.id
    )

    assert (
        result.get_metadata(
            "runtime_query"
        )
        == "open Chrome"
    )

    assert (
        result.get_metadata(
            "integration"
        )
        == "voice-runtime-integration"
    )


def test_process_voice_adds_provider_metadata() -> None:
    """Provider metadata should survive the processing chain."""

    integration, _, _ = create_integration()

    result = integration.process_voice(
        create_voice_input()
    )

    assert result.is_successful()

    assert (
        result.get_metadata(
            "provider"
        )
        == "mock-stt"
    )


# ============================================================
# Failure Handling
# ============================================================


def test_failed_stt_does_not_update_runtime_query() -> None:
    """Failed STT should not update the runtime query."""

    integration, context, _ = create_integration(
        text="open Chrome",
        should_fail=True,
    )

    original_query = context.get_query()

    result = integration.process_voice(
        create_voice_input()
    )

    assert not result.is_successful()

    assert result.status == "failed"

    assert context.get_query() == original_query

    assert context.status == "created"


def test_empty_transcription_does_not_update_query() -> None:
    """Empty transcription should fail safely."""

    integration, context, _ = create_integration(
        text="   ",
    )

    result = integration.process_voice(
        create_voice_input()
    )

    assert not result.is_successful()

    assert result.status == "failed"

    assert (
        context.get_query()
        == ""
    )

    assert context.status == "created"


def test_invalid_voice_input_rejected() -> None:
    """Invalid voice input should be rejected."""

    integration, _, _ = create_integration()

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        integration.process_voice(
            Mock()
        )


# ============================================================
# Runtime Context
# ============================================================


def test_context_can_be_replaced() -> None:
    """Integration should support replacing runtime context."""

    integration, _, _ = create_integration()

    new_context = AgentRuntimeContext(
        agent=create_agent(),
    )

    integration.set_context(
        new_context
    )

    assert (
        integration.get_context()
        is new_context
    )


def test_invalid_context_replacement_rejected() -> None:
    """Invalid context replacement should fail."""

    integration, _, _ = create_integration()

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        integration.set_context(
            Mock()
        )


# ============================================================
# Pipeline
# ============================================================


def test_pipeline_can_be_replaced() -> None:
    """Integration should support replacing its pipeline."""

    integration, _, _ = create_integration()

    provider = MockSTTProvider(
        text="launch calculator",
    )

    processor = OpenAIVoiceProcessor(
        stt_provider=provider,
    )

    new_pipeline = VoiceProcessingPipeline(
        processor=processor,
    )

    integration.set_pipeline(
        new_pipeline
    )

    assert (
        integration.get_pipeline()
        is new_pipeline
    )


def test_invalid_pipeline_replacement_rejected() -> None:
    """Invalid pipeline replacement should fail."""

    integration, _, _ = create_integration()

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        integration.set_pipeline(
            Mock()
        )


# ============================================================
# Metadata
# ============================================================


def test_metadata_management() -> None:
    """Integration metadata should be manageable."""

    integration, _, _ = create_integration()

    integration.set_metadata(
        "version",
        "v0.58",
    )

    assert (
        integration.get_metadata(
            "version"
        )
        == "v0.58"
    )

    metadata = integration.get_all_metadata()

    assert metadata["version"] == "v0.58"


def test_custom_metadata_is_attached_to_result() -> None:
    """Configured integration metadata should reach the result."""

    integration, _, _ = create_integration()

    integration.set_metadata(
        "source",
        "microphone",
    )

    result = integration.process_voice(
        create_voice_input()
    )

    assert result.is_successful()

    assert (
        result.get_metadata(
            "source"
        )
        == "microphone"
    )


def test_invalid_metadata_key_rejected() -> None:
    """Invalid metadata keys should be rejected."""

    integration, _, _ = create_integration()

    with pytest.raises(
        VoiceRuntimeIntegrationError,
    ):
        integration.set_metadata(
            "",
            "value",
        )


# ============================================================
# Multiple Voice Inputs
# ============================================================


def test_multiple_voice_inputs_update_query() -> None:
    """Each successful voice input should update the current query."""

    integration, context, provider = create_integration(
        text="first query",
    )

    first_result = integration.process_voice(
        create_voice_input()
    )

    assert first_result.is_successful()

    assert context.get_query() == "first query"

    provider.text = "second query"

    second_result = integration.process_voice(
        create_voice_input()
    )

    assert second_result.is_successful()

    assert context.get_query() == "second query"

    assert provider.transcribe_calls == 2