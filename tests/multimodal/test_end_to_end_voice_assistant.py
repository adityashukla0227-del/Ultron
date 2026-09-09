"""
Tests for Ultron End-to-End Voice Assistant.

v0.69 — End-to-End Voice Assistant
"""

from __future__ import annotations

from typing import Any

import pytest

from modules.multimodal.audio_output_device import (
    AudioOutputDevice,
)
from modules.multimodal.audio_output_device_manager import (
    AudioOutputDeviceManager,
)
from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.voice_conversation_loop import (
    VoiceConversationLoop,
)
from modules.multimodal.voice_playback_executor import (
    VoicePlaybackExecutor,
)
from modules.multimodal.end_to_end_voice_assistant import (
    EndToEndVoiceAssistant,
    EndToEndVoiceAssistantError,
)


# ============================================================
# Mocks
# ============================================================


class MockConversationLoop(VoiceConversationLoop):
    """
    Lightweight conversation loop mock.

    Bypasses the real VoiceConversationLoop constructor while
    preserving the correct subclass type required by the
    EndToEndVoiceAssistant constructor validation.
    """

    def __new__(
        cls,
        result: Any,
    ) -> "MockConversationLoop":
        instance = object.__new__(cls)
        instance._result = result
        return instance

    def __init__(
        self,
        result: Any,
    ) -> None:
        pass

    def is_available(self) -> bool:
        return True

    def execute_once(self) -> dict[str, Any]:
        if isinstance(self._result, Exception):
            raise self._result

        return self._result


class MockPlaybackBackend:
    """Simple playback backend used by tests."""

    def __init__(self) -> None:
        self.calls: list[
            tuple[Any, AudioOutputDevice]
        ] = []
        self.should_fail = False

    def __call__(
        self,
        audio: Any,
        device: AudioOutputDevice,
    ) -> None:
        if self.should_fail:
            raise RuntimeError(
                "Mock playback failure."
            )

        self.calls.append(
            (audio, device)
        )


# ============================================================
# Helpers
# ============================================================


def create_playback_executor(
    *,
    available: bool = True,
) -> tuple[
    VoicePlaybackExecutor,
    MockPlaybackBackend,
]:
    manager = AudioOutputDeviceManager()

    device = AudioOutputDevice(
        device_id="speaker-1",
        name="Mock Speaker",
        available=available,
        is_default=True,
    )

    manager.register_device(device)

    backend = MockPlaybackBackend()

    executor = VoicePlaybackExecutor(
        device_manager=manager,
        playback_backend=backend,
    )

    return executor, backend


def create_success_response_result(
    *,
    audio: Any = b"audio-data",
) -> MultimodalInputResult:
    """
    Create a successful response result.

    Synthesized audio is carried by the result's `data`
    field. The current MultimodalInputResult implementation
    uses its supported default input type.
    """

    response_result = MultimodalInputResult(
        input_id="voice-response",
    )

    response_result.complete(
        data=audio
    )

    return response_result


def create_success_conversation_result(
    *,
    audio: Any = b"audio-data",
) -> dict[str, Any]:
    response_result = create_success_response_result(
        audio=audio
    )

    return {
        "success": True,
        "status": "completed",
        "stage": "completed",
        "conversation_loop": "voice-conversation-loop",
        "voice_input": None,
        "transcription_result": None,
        "transcription": "play music",
        "execution_result": {
            "success": True,
            "result": "Playing music",
            "context_id": "context-1",
            "execution_id": "execution-1",
        },
        "response_text": "Playing music",
        "response_result": response_result,
    }


# ============================================================
# Initial State
# ============================================================


def test_initial_state() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.get_last_result()

    assert result["success"] is False
    assert result["status"] == "idle"
    assert result["stage"] == "idle"
    assert result["end_to_end"] is False


# ============================================================
# Component Access
# ============================================================


def test_component_access() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    assert (
        assistant.get_voice_conversation_loop()
        is conversation
    )

    assert (
        assistant.get_voice_playback_executor()
        is playback
    )


# ============================================================
# Successful Execution
# ============================================================


def test_successful_end_to_end_execution() -> None:
    conversation_result = (
        create_success_conversation_result()
    )

    conversation = MockConversationLoop(
        conversation_result
    )

    playback, backend = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is True
    assert result["status"] == "completed"
    assert result["stage"] == "completed"
    assert result["end_to_end"] is True

    # execute_once() returns a defensive copy.
    assert (
        result["conversation_result"]["response_text"]
        == "Playing music"
    )

    assert result["transcription"] == "play music"
    assert result["response_text"] == "Playing music"

    assert (
        result["playback_result"]["success"]
        is True
    )

    assert len(backend.calls) == 1
    assert backend.calls[0][0] == b"audio-data"


def test_audio_is_extracted_from_response_result() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result(
            audio=b"voice-audio"
        )
    )

    playback, backend = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is True
    assert backend.calls[0][0] == b"voice-audio"


# ============================================================
# Last Result
# ============================================================


def test_last_result_is_stored() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()
    stored = assistant.get_last_result()

    assert stored["success"] is True
    assert stored["status"] == "completed"
    assert stored["stage"] == "completed"
    assert stored["end_to_end"] is True

    assert (
        stored["response_text"]
        == result["response_text"]
    )

    assert (
        stored["transcription"]
        == result["transcription"]
    )

    assert (
        stored["playback_result"]
        == result["playback_result"]
    )


def test_last_result_is_defensive() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    result["status"] = "modified"

    assert (
        assistant.get_last_result()["status"]
        == "completed"
    )


# ============================================================
# Conversation Failures
# ============================================================


def test_conversation_failure_is_propagated() -> None:
    conversation = MockConversationLoop(
        {
            "success": False,
            "status": "failed",
            "stage": "processing",
            "error": "STT failed.",
        }
    )

    playback, backend = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "processing"
    assert result["error"] == "STT failed."
    assert backend.calls == []


def test_invalid_conversation_result() -> None:
    conversation = MockConversationLoop(
        "invalid-result"
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "conversation"
    assert "invalid result" in result["error"]


def test_conversation_exception() -> None:
    conversation = MockConversationLoop(
        RuntimeError("Conversation failure.")
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "conversation"
    assert result["error"] == "Conversation failure."


# ============================================================
# Response Result Validation
# ============================================================


def test_missing_response_result() -> None:
    conversation = MockConversationLoop(
        {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "response_text": "Hello",
        }
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "playback"


def test_invalid_response_result() -> None:
    conversation = MockConversationLoop(
        {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "response_result": "invalid",
        }
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "playback"


def test_failed_response_result() -> None:
    response_result = MultimodalInputResult(
        input_id="voice-response",
    )

    response_result.fail(
        "TTS failed."
    )

    conversation = MockConversationLoop(
        {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "response_result": response_result,
        }
    )

    playback, backend = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "response"
    assert result["error"] == "TTS failed."
    assert backend.calls == []


def test_missing_audio_data() -> None:
    response_result = MultimodalInputResult(
        input_id="voice-response",
    )

    response_result.complete(
        data=None
    )

    conversation = MockConversationLoop(
        {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "response_result": response_result,
        }
    )

    playback, backend = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "playback"
    assert backend.calls == []


# ============================================================
# Playback
# ============================================================


def test_playback_failure() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, backend = create_playback_executor()

    backend.should_fail = True

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert result["success"] is False
    assert result["stage"] == "playback"
    assert "playback failed" in result["error"].lower()


def test_playback_result_is_preserved() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    result = assistant.execute_once()

    assert (
        result["playback_result"]["success"]
        is True
    )

    assert (
        result["playback_result"]["device_id"]
        == "speaker-1"
    )


# ============================================================
# Availability
# ============================================================


def test_availability() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    assert assistant.is_available() is True


def test_unavailable_playback() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor(
        available=False
    )

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    assert assistant.is_available() is False


# ============================================================
# Reset
# ============================================================


def test_reset() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    assistant.execute_once()

    assert (
        assistant.get_last_result()["success"]
        is True
    )

    assistant.reset()

    result = assistant.get_last_result()

    assert result["success"] is False
    assert result["status"] == "idle"
    assert result["stage"] == "idle"


# ============================================================
# Constructor Validation
# ============================================================


def test_invalid_conversation_loop() -> None:
    playback, _ = create_playback_executor()

    with pytest.raises(
        EndToEndVoiceAssistantError
    ):
        EndToEndVoiceAssistant(
            voice_conversation_loop="invalid",
            voice_playback_executor=playback,
        )


def test_invalid_playback_executor() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    with pytest.raises(
        EndToEndVoiceAssistantError
    ):
        EndToEndVoiceAssistant(
            voice_conversation_loop=conversation,
            voice_playback_executor="invalid",
        )


# ============================================================
# Representation
# ============================================================


def test_repr() -> None:
    conversation = MockConversationLoop(
        create_success_conversation_result()
    )

    playback, _ = create_playback_executor()

    assistant = EndToEndVoiceAssistant(
        voice_conversation_loop=conversation,
        voice_playback_executor=playback,
    )

    representation = repr(assistant)

    assert (
        "EndToEndVoiceAssistant"
        in representation
    )

    assert (
        "end-to-end-voice-assistant"
        in representation
    )