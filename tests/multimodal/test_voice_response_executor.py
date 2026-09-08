"""
Tests for Voice Response Executor.

Ultron v0.64 — Voice Response Execution
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.tts_runtime_integration import (
    TTSRuntimeIntegration,
)
from modules.multimodal.voice_response_executor import (
    VoiceResponseExecutionError,
    VoiceResponseExecutor,
)


class TestVoiceResponseExecutorInitialization:
    """Test voice response executor initialization."""

    def test_requires_tts_integration(self):
        with pytest.raises(
            VoiceResponseExecutionError
        ):
            VoiceResponseExecutor(
                tts_integration=None
            )

    def test_requires_tts_runtime_integration_instance(
        self,
    ):
        with pytest.raises(
            VoiceResponseExecutionError
        ):
            VoiceResponseExecutor(
                tts_integration=MagicMock()
            )

    def test_initializes_successfully(self):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        assert (
            executor.get_tts_integration()
            is integration
        )

    def test_repr_contains_executor_name(self):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        assert "voice-response-executor" in repr(
            executor
        )


class TestVoiceResponseExecutorAvailability:
    """Test TTS availability delegation."""

    def test_is_available_delegates_to_integration(
        self,
    ):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.is_available.return_value = (
            True
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        assert executor.is_available() is True

        integration.is_available.assert_called_once()


class TestVoiceResponseExecutorValidation:
    """Test runtime response validation."""

    @staticmethod
    def create_executor():
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        return VoiceResponseExecutor(
            tts_integration=integration
        )

    def test_accepts_valid_response_text(self):
        executor = self.create_executor()

        executor.validate_response_text(
            "Hello from Ultron"
        )

    def test_rejects_empty_response_text(self):
        executor = self.create_executor()

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.validate_response_text("")

    def test_rejects_whitespace_response_text(
        self,
    ):
        executor = self.create_executor()

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.validate_response_text("   ")

    def test_rejects_none_response_text(self):
        executor = self.create_executor()

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.validate_response_text(None)

    def test_rejects_non_string_response_text(
        self,
    ):
        executor = self.create_executor()

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.validate_response_text(123)


class TestVoiceResponseExecutorExecution:
    """Test voice response execution."""

    @staticmethod
    def create_executor():
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        result = MultimodalInputResult(
            input_id="tts-input",
            input_type="text",
        )

        result.complete(
            data=b"generated-audio"
        )

        integration.synthesize.return_value = (
            result
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        return executor, integration

    def test_execute_returns_result(self):
        executor, _ = (
            self.create_executor()
        )

        result = executor.execute(
            "Hello from Ultron"
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

    def test_execute_returns_integration_result(
        self,
    ):
        executor, integration = (
            self.create_executor()
        )

        result = executor.execute(
            "Hello from Ultron"
        )

        assert result is (
            integration.synthesize.return_value
        )

    def test_execute_delegates_response_text(
        self,
    ):
        executor, integration = (
            self.create_executor()
        )

        text = "Hello from Ultron"

        executor.execute(text)

        integration.synthesize.assert_called_once_with(
            text,
            runtime_context_id=None,
            execution_id=None,
            metadata=None,
        )

    def test_execute_preserves_audio(self):
        executor, _ = (
            self.create_executor()
        )

        result = executor.execute(
            "Hello from Ultron"
        )

        assert result.get_data() == (
            b"generated-audio"
        )

    def test_execute_adds_executor_metadata(
        self,
    ):
        executor, _ = (
            self.create_executor()
        )

        result = executor.execute(
            "Hello from Ultron"
        )

        assert (
            result.get_metadata(
                "executor"
            )
            == "voice-response-executor"
        )

    def test_execute_adds_response_text_metadata(
        self,
    ):
        executor, _ = (
            self.create_executor()
        )

        result = executor.execute(
            "Hello from Ultron"
        )

        assert (
            result.get_metadata(
                "response_text"
            )
            == "Hello from Ultron"
        )

    def test_execute_passes_runtime_context_id(
        self,
    ):
        executor, integration = (
            self.create_executor()
        )

        executor.execute(
            "Hello",
            runtime_context_id="context-123",
        )

        integration.synthesize.assert_called_once_with(
            "Hello",
            runtime_context_id="context-123",
            execution_id=None,
            metadata=None,
        )

    def test_execute_passes_execution_id(self):
        executor, integration = (
            self.create_executor()
        )

        executor.execute(
            "Hello",
            execution_id="execution-123",
        )

        integration.synthesize.assert_called_once_with(
            "Hello",
            runtime_context_id=None,
            execution_id="execution-123",
            metadata=None,
        )

    def test_execute_passes_custom_metadata(self):
        executor, integration = (
            self.create_executor()
        )

        metadata = {
            "response_type": "voice",
        }

        executor.execute(
            "Hello",
            metadata=metadata,
        )

        integration.synthesize.assert_called_once_with(
            "Hello",
            runtime_context_id=None,
            execution_id=None,
            metadata=metadata,
        )

    def test_empty_response_does_not_call_integration(
        self,
    ):
        executor, integration = (
            self.create_executor()
        )

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.execute("")

        integration.synthesize.assert_not_called()

    def test_whitespace_response_does_not_call_integration(
        self,
    ):
        executor, integration = (
            self.create_executor()
        )

        with pytest.raises(
            VoiceResponseExecutionError
        ):
            executor.execute("   ")

        integration.synthesize.assert_not_called()


class TestVoiceResponseExecutorSafeExecution:
    """Test safe voice response execution."""

    def test_safe_execute_returns_failed_result_on_error(
        self,
    ):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.synthesize.side_effect = (
            RuntimeError(
                "tts failure"
            )
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        result = executor.execute_safe(
            "Hello"
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

        assert result.status == "failed"
        assert result.success is False

    def test_safe_execute_preserves_error(self):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.synthesize.side_effect = (
            RuntimeError(
                "tts failure"
            )
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        result = executor.execute_safe(
            "Hello"
        )

        assert "tts failure" in str(
            result.error
        )

    def test_safe_execute_adds_executor_metadata(
        self,
    ):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.synthesize.side_effect = (
            RuntimeError(
                "tts failure"
            )
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        result = executor.execute_safe(
            "Hello"
        )

        assert (
            result.get_metadata(
                "executor"
            )
            == "voice-response-executor"
        )

    def test_safe_execute_adds_response_text_metadata(
        self,
    ):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.synthesize.side_effect = (
            RuntimeError(
                "tts failure"
            )
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        result = executor.execute_safe(
            "Hello"
        )

        assert (
            result.get_metadata(
                "response_text"
            )
            == "Hello"
        )

    def test_safe_execute_does_not_raise_error(
        self,
    ):
        integration = MagicMock(
            spec=TTSRuntimeIntegration
        )

        integration.synthesize.side_effect = (
            RuntimeError(
                "tts failure"
            )
        )

        executor = VoiceResponseExecutor(
            tts_integration=integration
        )

        result = executor.execute_safe(
            "Hello"
        )

        assert result.is_failed()