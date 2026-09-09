"""
Ultron End-to-End Voice Assistant

v0.69 — End-to-End Voice Assistant

Coordinates the complete voice interaction pipeline:

    Audio Capture
        ↓
    Voice Conversation Loop
        ↓
    Voice Processing
        ↓
    Agent Execution
        ↓
    TTS Response
        ↓
    Synthesized Audio
        ↓
    Voice Playback
        ↓
    Audio Output Device

This module is responsible only for top-level
end-to-end voice orchestration.

It does NOT:
- perform STT directly
- perform TTS directly
- execute tools directly
- manage agent execution internals
- discover audio devices
- implement playback backends
- implement wake-word detection
- implement continuous listening
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.voice_conversation_loop import (
    VoiceConversationLoop,
)
from modules.multimodal.voice_playback_executor import (
    VoicePlaybackExecutor,
)


class EndToEndVoiceAssistantError(Exception):
    """Base exception for end-to-end voice assistant errors."""


class EndToEndVoiceAssistant:
    """
    Top-level orchestrator for one complete voice interaction.

    Existing conversation and playback components remain
    responsible for their individual domains.

    EndToEndVoiceAssistant only connects:

        VoiceConversationLoop
                ↓
        Synthesized Audio
                ↓
        VoicePlaybackExecutor
    """

    ASSISTANT_NAME = "end-to-end-voice-assistant"

    def __init__(
        self,
        *,
        voice_conversation_loop: VoiceConversationLoop,
        voice_playback_executor: VoicePlaybackExecutor,
    ) -> None:
        if not isinstance(
            voice_conversation_loop,
            VoiceConversationLoop,
        ):
            raise EndToEndVoiceAssistantError(
                "voice_conversation_loop must be a "
                "VoiceConversationLoop instance."
            )

        if not isinstance(
            voice_playback_executor,
            VoicePlaybackExecutor,
        ):
            raise EndToEndVoiceAssistantError(
                "voice_playback_executor must be a "
                "VoicePlaybackExecutor instance."
            )

        self._voice_conversation_loop = (
            voice_conversation_loop
        )

        self._voice_playback_executor = (
            voice_playback_executor
        )

        self._last_result: Dict[str, Any] | None = None

    # ========================================================
    # Component Access
    # ========================================================

    def get_voice_conversation_loop(
        self,
    ) -> VoiceConversationLoop:
        """Return the configured voice conversation loop."""

        return self._voice_conversation_loop

    def get_voice_playback_executor(
        self,
    ) -> VoicePlaybackExecutor:
        """Return the configured voice playback executor."""

        return self._voice_playback_executor

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the complete voice assistant can run.

        Both the conversation loop and playback executor
        must currently be available.
        """

        return (
            self._voice_conversation_loop.is_available()
            and self._voice_playback_executor.is_available()
        )

    # ========================================================
    # Execution
    # ========================================================

    def execute_once(self) -> Dict[str, Any]:
        """
        Execute one complete end-to-end voice interaction.

        Pipeline:

            VoiceConversationLoop
                    ↓
            Synthesized Audio
                    ↓
            VoicePlaybackExecutor
                    ↓
            Audio Output
        """

        # ----------------------------------------------------
        # 1. Execute conversation loop
        # ----------------------------------------------------

        try:
            conversation_result = (
                self._voice_conversation_loop.execute_once()
            )

        except Exception as exc:
            result = self._failure_result(
                stage="conversation",
                error=str(exc),
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 2. Validate conversation result
        # ----------------------------------------------------

        if not isinstance(
            conversation_result,
            dict,
        ):
            result = self._failure_result(
                stage="conversation",
                error=(
                    "Voice conversation loop returned "
                    "an invalid result."
                ),
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 3. Validate conversation success
        # ----------------------------------------------------

        if conversation_result.get("success") is not True:
            result = self._failure_result(
                stage=conversation_result.get(
                    "stage",
                    "conversation",
                ),
                error=conversation_result.get(
                    "error",
                    "Voice conversation failed.",
                ),
                conversation_result=conversation_result,
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 4. Resolve synthesized response
        # ----------------------------------------------------

        response_result = conversation_result.get(
            "response_result"
        )

        if not isinstance(
            response_result,
            MultimodalInputResult,
        ):
            result = self._failure_result(
                stage="playback",
                error=(
                    "Voice conversation result does not "
                    "contain a valid response result."
                ),
                conversation_result=conversation_result,
            )

            self._last_result = result

            return deepcopy(result)

        if not response_result.is_successful():
            result = self._failure_result(
                stage="response",
                error=response_result.get_error(
                    "Voice response failed."
                ),
                conversation_result=conversation_result,
                response_result=response_result,
            )

            self._last_result = result

            return deepcopy(result)

        audio = response_result.get_data()

        if audio is None:
            result = self._failure_result(
                stage="playback",
                error=(
                    "Voice response result does not "
                    "contain synthesized audio."
                ),
                conversation_result=conversation_result,
                response_result=response_result,
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 5. Execute audio playback
        # ----------------------------------------------------

        try:
            playback_result = (
                self._voice_playback_executor.execute(
                    audio
                )
            )

        except Exception as exc:
            result = self._failure_result(
                stage="playback",
                error=str(exc),
                conversation_result=conversation_result,
                response_result=response_result,
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 6. Validate playback result
        # ----------------------------------------------------

        if not isinstance(
            playback_result,
            dict,
        ):
            result = self._failure_result(
                stage="playback",
                error=(
                    "Voice playback executor returned "
                    "an invalid result."
                ),
                conversation_result=conversation_result,
                response_result=response_result,
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 7. Validate playback success
        # ----------------------------------------------------

        if playback_result.get("success") is not True:
            result = self._failure_result(
                stage="playback",
                error=playback_result.get(
                    "error",
                    "Voice playback failed.",
                ),
                conversation_result=conversation_result,
                response_result=response_result,
                playback_result=playback_result,
            )

            self._last_result = result

            return deepcopy(result)

        # ----------------------------------------------------
        # 8. Complete end-to-end result
        # ----------------------------------------------------

        result = {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "assistant": self.ASSISTANT_NAME,
            "end_to_end": True,

            "conversation_result": conversation_result,

            "voice_input": conversation_result.get(
                "voice_input"
            ),

            "transcription_result": conversation_result.get(
                "transcription_result"
            ),

            "transcription": conversation_result.get(
                "transcription"
            ),

            "execution_result": conversation_result.get(
                "execution_result"
            ),

            "response_text": conversation_result.get(
                "response_text"
            ),

            "response_result": response_result,

            "playback_result": playback_result,
        }

        self._last_result = result

        return deepcopy(result)

    # ========================================================
    # State
    # ========================================================

    def get_last_result(
        self,
    ) -> Dict[str, Any]:
        """
        Return a defensive copy of the latest result.
        """

        return deepcopy(
            self._last_result
            or {
                "success": False,
                "status": "idle",
                "stage": "idle",
                "assistant": self.ASSISTANT_NAME,
                "end_to_end": False,
            }
        )

    def reset(self) -> None:
        """
        Reset end-to-end assistant state.

        Existing child components retain ownership
        of their own internal state.
        """

        self._last_result = None

    # ========================================================
    # Failure Handling
    # ========================================================

    @classmethod
    def _failure_result(
        cls,
        *,
        stage: str,
        error: str,
        conversation_result: Dict[str, Any] | None = None,
        response_result: MultimodalInputResult | None = None,
        playback_result: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Build a normalized end-to-end failure result.
        """

        return {
            "success": False,
            "status": "failed",
            "stage": stage,
            "assistant": cls.ASSISTANT_NAME,
            "end_to_end": False,
            "error": error,
            "conversation_result": conversation_result,
            "response_result": response_result,
            "playback_result": playback_result,
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "EndToEndVoiceAssistant("
            f"assistant={self.ASSISTANT_NAME!r}"
            ")"
        )


__all__ = [
    "EndToEndVoiceAssistant",
    "EndToEndVoiceAssistantError",
]