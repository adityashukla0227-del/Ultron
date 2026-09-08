"""
Tests for Ultron Voice Conversation Loop.

v0.65 — Full Voice Conversation Loop
"""

from unittest.mock import MagicMock

import pytest

from modules.multimodal.audio_capture import (
    AudioCapture,
    AudioCaptureError,
)
from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.voice_command_executor import (
    VoiceCommandExecutor,
)
from modules.multimodal.voice_conversation_loop import (
    VoiceConversationLoop,
    VoiceConversationLoopError,
)
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_response_executor import (
    VoiceResponseExecutor,
)
from modules.multimodal.voice_runtime_integration import (
    VoiceRuntimeIntegration,
)


class MockAudioCapture(AudioCapture):
    """Test audio capture implementation."""

    def __init__(self):
        super().__init__()
        self.started = False
        self.stopped = False
        self.voice_input = VoiceInput(
            b"test-audio",
            source="test",
            audio_format="wav",
            sample_rate=16000,
            channels=1,
            duration=1.0,
        )

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True
        return self.voice_input

    def is_recording(self):
        return self.started and not self.stopped

    def is_available(self):
        return True

    def get_device_info(self):
        return {"name": "test-device"}


class UnavailableAudioCapture(MockAudioCapture):
    """Unavailable audio capture implementation."""

    def is_available(self):
        return False


class FailingAudioCapture(MockAudioCapture):
    """Audio capture that fails during start."""

    def start(self):
        raise AudioCaptureError("capture failed")


class TestVoiceConversationLoop:
    """Test VoiceConversationLoop behavior."""

    def _build_dependencies(self):
        audio_capture = MockAudioCapture()

        runtime_integration = MagicMock(
            spec=VoiceRuntimeIntegration
        )

        command_executor = MagicMock(
            spec=VoiceCommandExecutor
        )

        response_executor = MagicMock(
            spec=VoiceResponseExecutor
        )

        response_executor.is_available.return_value = True

        return (
            audio_capture,
            runtime_integration,
            command_executor,
            response_executor,
        )

    def _build_loop(self):
        dependencies = self._build_dependencies()

        loop = VoiceConversationLoop(
            audio_capture=dependencies[0],
            voice_runtime_integration=dependencies[1],
            voice_command_executor=dependencies[2],
            voice_response_executor=dependencies[3],
        )

        return loop, dependencies

    def _successful_transcription(self):
        result = MultimodalInputResult(
            input_id="voice-1",
            input_type="voice",
            status="processing",
        )

        result.complete(
            "open the browser"
        )

        return result

    def _successful_response(self):
        result = MultimodalInputResult(
            input_id="tts-1",
            input_type="text",
            status="processing",
        )

        result.complete(
            b"audio-output"
        )

        return result

    def test_constructor_validates_dependencies(self):
        with pytest.raises(
            VoiceConversationLoopError
        ):
            VoiceConversationLoop(
                audio_capture=object(),
                voice_runtime_integration=MagicMock(
                    spec=VoiceRuntimeIntegration
                ),
                voice_command_executor=MagicMock(
                    spec=VoiceCommandExecutor
                ),
                voice_response_executor=MagicMock(
                    spec=VoiceResponseExecutor
                ),
            )

    def test_constructor_accepts_valid_dependencies(self):
        loop, dependencies = self._build_loop()

        assert loop.get_audio_capture() is dependencies[0]

        assert (
            loop.get_voice_runtime_integration()
            is dependencies[1]
        )

        assert (
            loop.get_voice_command_executor()
            is dependencies[2]
        )

        assert (
            loop.get_voice_response_executor()
            is dependencies[3]
        )

    def test_is_available_requires_capture_and_tts(self):
        loop, dependencies = self._build_loop()

        assert loop.is_available() is True

        unavailable_capture = (
            UnavailableAudioCapture()
        )

        loop = VoiceConversationLoop(
            audio_capture=unavailable_capture,
            voice_runtime_integration=dependencies[1],
            voice_command_executor=dependencies[2],
            voice_response_executor=dependencies[3],
        )

        assert loop.is_available() is False

    def test_is_available_requires_tts(self):
        loop, dependencies = self._build_loop()

        dependencies[3].is_available.return_value = False

        assert loop.is_available() is False

    def test_execute_once_success(self):
        loop, dependencies = self._build_loop()

        transcription_result = (
            self._successful_transcription()
        )

        execution_result = {
            "success": True,
            "query": "open the browser",
            "context_id": "context-1",
            "plan_id": "plan-1",
            "execution_id": "execution-1",
            "tool_name": "browser",
            "result": "The browser has been opened.",
            "status": "completed",
            "progress": 1.0,
        }

        response_result = (
            self._successful_response()
        )

        dependencies[1].process_voice.return_value = (
            transcription_result
        )

        dependencies[2].execute.return_value = (
            execution_result
        )

        dependencies[3].execute.return_value = (
            response_result
        )

        result = loop.execute_once()

        assert result["success"] is True
        assert result["status"] == "completed"
        assert result["stage"] == "completed"

        assert (
            result["conversation_loop"]
            == "voice-conversation-loop"
        )

        assert result["voice_input"] is not None

        assert (
            result["transcription"]
            == "open the browser"
        )

        assert (
            result["execution_result"]
            == execution_result
        )

        assert (
            result["response_text"]
            == "The browser has been opened."
        )

        assert (
            result["response_result"]
            is response_result
        )

        assert (
            dependencies[0].started
            is True
        )

        assert (
            dependencies[0].stopped
            is True
        )

        dependencies[1].process_voice.assert_called_once_with(
            dependencies[0].voice_input
        )

        dependencies[2].execute.assert_called_once()

        dependencies[3].execute.assert_called_once_with(
            "The browser has been opened.",
            runtime_context_id="context-1",
            execution_id="execution-1",
            metadata={
                "conversation_loop":
                    "voice-conversation-loop"
            },
        )

    def test_execute_once_fails_when_capture_fails(self):
        capture = FailingAudioCapture()

        runtime_integration = MagicMock(
            spec=VoiceRuntimeIntegration
        )

        command_executor = MagicMock(
            spec=VoiceCommandExecutor
        )

        response_executor = MagicMock(
            spec=VoiceResponseExecutor
        )

        loop = VoiceConversationLoop(
            audio_capture=capture,
            voice_runtime_integration=runtime_integration,
            voice_command_executor=command_executor,
            voice_response_executor=response_executor,
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["status"] == "failed"
        assert result["stage"] == "capture"

        assert (
            "capture failed"
            in result["error"]
        )

        runtime_integration.process_voice.assert_not_called()
        command_executor.execute.assert_not_called()
        response_executor.execute.assert_not_called()

    def test_execute_once_fails_when_processing_fails(self):
        loop, dependencies = self._build_loop()

        failed_result = MultimodalInputResult(
            input_id="voice-1",
            input_type="voice",
            status="processing",
        )

        failed_result.fail(
            "STT processing failed."
        )

        dependencies[1].process_voice.return_value = (
            failed_result
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "processing"

        assert (
            result["error"]
            == "STT processing failed."
        )

        dependencies[2].execute.assert_not_called()
        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_runtime_integration_raises(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.side_effect = (
            RuntimeError("runtime integration failed")
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "processing"

        assert (
            result["error"]
            == "runtime integration failed"
        )

        dependencies[2].execute.assert_not_called()
        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_execution_fails(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            self._successful_transcription()
        )

        dependencies[2].execute.return_value = {
            "success": False,
            "error": "No suitable tool found.",
            "status": "failed",
        }

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "execution"

        assert (
            result["error"]
            == "No suitable tool found."
        )

        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_execution_result_is_invalid(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            self._successful_transcription()
        )

        dependencies[2].execute.return_value = None

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "execution"

        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_response_text_is_missing(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            self._successful_transcription()
        )

        dependencies[2].execute.return_value = {
            "success": True,
            "result": None,
        }

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "response"

        assert (
            "without a usable response"
            in result["error"]
        )

        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_response_execution_fails(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            self._successful_transcription()
        )

        dependencies[2].execute.return_value = {
            "success": True,
            "context_id": "context-1",
            "execution_id": "execution-1",
            "result": "Done.",
        }

        failed_response = MultimodalInputResult(
            input_id="tts-1",
            input_type="text",
            status="processing",
        )

        failed_response.fail(
            "TTS synthesis failed."
        )

        dependencies[3].execute.return_value = (
            failed_response
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "response"

        assert (
            result["error"]
            == "TTS synthesis failed."
        )

    def test_execute_once_fails_when_response_executor_raises(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            self._successful_transcription()
        )

        dependencies[2].execute.return_value = {
            "success": True,
            "context_id": "context-1",
            "execution_id": "execution-1",
            "result": "Done.",
        }

        dependencies[3].execute.side_effect = (
            RuntimeError("TTS executor failed")
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "response"

        assert (
            result["error"]
            == "TTS executor failed"
        )

    def test_execute_once_fails_when_transcription_result_is_invalid(self):
        loop, dependencies = self._build_loop()

        dependencies[1].process_voice.return_value = (
            None
        )

        result = loop.execute_once()

        assert result["success"] is False
        assert result["stage"] == "processing"

        dependencies[2].execute.assert_not_called()
        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_transcription_data_is_not_text(self):
        loop, dependencies = self._build_loop()

        result = MultimodalInputResult(
            input_id="voice-1",
            input_type="voice",
            status="processing",
        )

        result.complete(
            b"not-text"
        )

        dependencies[1].process_voice.return_value = (
            result
        )

        output = loop.execute_once()

        assert output["success"] is False
        assert output["stage"] == "processing"

        dependencies[2].execute.assert_not_called()
        dependencies[3].execute.assert_not_called()

    def test_execute_once_fails_when_transcription_is_empty(self):
        loop, dependencies = self._build_loop()

        result = MultimodalInputResult(
            input_id="voice-1",
            input_type="voice",
            status="processing",
        )

        result.complete("   ")

        dependencies[1].process_voice.return_value = (
            result
        )

        output = loop.execute_once()

        assert output["success"] is False
        assert output["stage"] == "processing"

        dependencies[2].execute.assert_not_called()
        dependencies[3].execute.assert_not_called()

    def test_string_result_is_used_as_response(self):
        execution_result = {
            "result": "Hello from Ultron."
        }

        assert (
            VoiceConversationLoop._resolve_response_text(
                execution_result
            )
            == "Hello from Ultron."
        )

    def test_string_result_is_stripped(self):
        execution_result = {
            "result": "  Hello from Ultron.  "
        }

        assert (
            VoiceConversationLoop._resolve_response_text(
                execution_result
            )
            == "Hello from Ultron."
        )

    def test_empty_string_result_returns_none(self):
        execution_result = {
            "result": "   "
        }

        assert (
            VoiceConversationLoop._resolve_response_text(
                execution_result
            )
            is None
        )

    def test_numeric_result_is_converted_to_text(self):
        assert (
            VoiceConversationLoop._resolve_response_text(
                {"result": 42}
            )
            == "42"
        )

    def test_boolean_result_is_converted_to_text(self):
        assert (
            VoiceConversationLoop._resolve_response_text(
                {"result": True}
            )
            == "True"
        )

    def test_none_result_returns_none(self):
        assert (
            VoiceConversationLoop._resolve_response_text(
                {"result": None}
            )
            is None
        )

    def test_complex_result_returns_none(self):
        assert (
            VoiceConversationLoop._resolve_response_text(
                {
                    "result": {
                        "message": "done"
                    }
                }
            )
            is None
        )

    def test_repr(self):
        loop, _ = self._build_loop()

        assert repr(loop) == (
            "VoiceConversationLoop("
            "name='voice-conversation-loop'"
            ")"
        )