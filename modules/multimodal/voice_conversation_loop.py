"""
Ultron Voice Conversation Loop.

v0.65 — Full Voice Conversation Loop

Coordinates one complete voice interaction:

    Microphone
        ↓
    VoiceInput
        ↓
    VoiceRuntimeIntegration
        ↓
    AgentRuntimeContext
        ↓
    VoiceCommandExecutor
        ↓
    Execution Result
        ↓
    VoiceResponseExecutor
        ↓
    Synthesized Audio

This module is responsible only for conversation-level
orchestration.

It does NOT:
- perform STT directly
- perform TTS directly
- execute tools directly
- control AgentOrchestrator internals
- manage audio devices
- implement audio playback
- contain provider-specific logic
- implement wake-word detection
- implement continuous always-listening behavior
"""

from __future__ import annotations

from typing import Any, Dict, Optional

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
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_response_executor import (
    VoiceResponseExecutor,
)
from modules.multimodal.voice_runtime_integration import (
    VoiceRuntimeIntegration,
)


class VoiceConversationLoopError(Exception):
    """Base exception for voice conversation loop errors."""


class VoiceConversationLoop:
    """
    Orchestrates one complete voice request-response cycle.

    The loop connects the existing input-side and output-side
    voice architecture without taking ownership of any of
    those individual responsibilities.

    Lifecycle:

        capture
            ↓
        process
            ↓
        execute
            ↓
        respond
    """

    LOOP_NAME = "voice-conversation-loop"

    def __init__(
        self,
        *,
        audio_capture: AudioCapture,
        voice_runtime_integration: VoiceRuntimeIntegration,
        voice_command_executor: VoiceCommandExecutor,
        voice_response_executor: VoiceResponseExecutor,
    ) -> None:
        if not isinstance(
            audio_capture,
            AudioCapture,
        ):
            raise VoiceConversationLoopError(
                "audio_capture must be an AudioCapture instance."
            )

        if not isinstance(
            voice_runtime_integration,
            VoiceRuntimeIntegration,
        ):
            raise VoiceConversationLoopError(
                "voice_runtime_integration must be a "
                "VoiceRuntimeIntegration instance."
            )

        if not isinstance(
            voice_command_executor,
            VoiceCommandExecutor,
        ):
            raise VoiceConversationLoopError(
                "voice_command_executor must be a "
                "VoiceCommandExecutor instance."
            )

        if not isinstance(
            voice_response_executor,
            VoiceResponseExecutor,
        ):
            raise VoiceConversationLoopError(
                "voice_response_executor must be a "
                "VoiceResponseExecutor instance."
            )

        self._audio_capture = audio_capture
        self._voice_runtime_integration = (
            voice_runtime_integration
        )
        self._voice_command_executor = (
            voice_command_executor
        )
        self._voice_response_executor = (
            voice_response_executor
        )

    # ========================================================
    # Component Access
    # ========================================================

    def get_audio_capture(self) -> AudioCapture:
        """Return the configured audio capture component."""

        return self._audio_capture

    def get_voice_runtime_integration(
        self,
    ) -> VoiceRuntimeIntegration:
        """Return the voice runtime integration."""

        return self._voice_runtime_integration

    def get_voice_command_executor(
        self,
    ) -> VoiceCommandExecutor:
        """Return the voice command executor."""

        return self._voice_command_executor

    def get_voice_response_executor(
        self,
    ) -> VoiceResponseExecutor:
        """Return the voice response executor."""

        return self._voice_response_executor

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the conversation loop can currently run.

        Both microphone capture and TTS response execution
        must be available.
        """

        return (
            self._audio_capture.is_available()
            and self._voice_response_executor.is_available()
        )

    # ========================================================
    # Conversation Execution
    # ========================================================

    def execute_once(self) -> Dict[str, Any]:
        """
        Execute one complete voice conversation cycle.

        Returns a structured conversation result containing:

        - captured voice input
        - transcription result
        - execution result
        - response result
        - overall status
        """

        voice_input: Optional[VoiceInput] = None
        transcription_result: Optional[
            MultimodalInputResult
        ] = None
        response_result: Optional[
            MultimodalInputResult
        ] = None
        execution_result: Optional[Dict[str, Any]] = None

        # ----------------------------------------------------
        # 1. Capture
        # ----------------------------------------------------

        try:
            self._audio_capture.start()
            voice_input = self._audio_capture.stop()

        except AudioCaptureError as exc:
            return self._failure_result(
                stage="capture",
                error=str(exc),
            )

        except Exception as exc:
            return self._failure_result(
                stage="capture",
                error=str(exc),
            )

        if not isinstance(
            voice_input,
            VoiceInput,
        ):
            return self._failure_result(
                stage="capture",
                error=(
                    "Audio capture returned an invalid "
                    "VoiceInput."
                ),
            )

        # ----------------------------------------------------
        # 2. Voice → Runtime
        # ----------------------------------------------------

        try:
            transcription_result = (
                self._voice_runtime_integration.process_voice(
                    voice_input
                )
            )

        except Exception as exc:
            return self._failure_result(
                stage="processing",
                error=str(exc),
                voice_input=voice_input,
            )

        if not isinstance(
            transcription_result,
            MultimodalInputResult,
        ):
            return self._failure_result(
                stage="processing",
                error=(
                    "Voice runtime integration returned "
                    "an invalid result."
                ),
                voice_input=voice_input,
            )

        if not transcription_result.is_successful():
            return self._failure_result(
                stage="processing",
                error=(
                    transcription_result.get_error(
                        "Voice processing failed."
                    )
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
            )

        transcription = transcription_result.get_data()

        if not isinstance(
            transcription,
            str,
        ):
            return self._failure_result(
                stage="processing",
                error=(
                    "Voice processing result does not "
                    "contain text."
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
            )

        transcription = transcription.strip()

        if not transcription:
            return self._failure_result(
                stage="processing",
                error="Voice transcription is empty.",
                voice_input=voice_input,
                transcription_result=transcription_result,
            )

        # ----------------------------------------------------
        # 3. Command Execution
        # ----------------------------------------------------

        try:
            execution_result = (
                self._voice_command_executor.execute()
            )

        except Exception as exc:
            return self._failure_result(
                stage="execution",
                error=str(exc),
                voice_input=voice_input,
                transcription_result=transcription_result,
            )

        if not isinstance(
            execution_result,
            dict,
        ):
            return self._failure_result(
                stage="execution",
                error=(
                    "Voice command executor returned "
                    "an invalid result."
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
            )

        if execution_result.get("success") is not True:
            return self._failure_result(
                stage="execution",
                error=execution_result.get(
                    "error",
                    "Voice command execution failed.",
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
                execution_result=execution_result,
            )

        # ----------------------------------------------------
        # 4. Resolve Response Text
        # ----------------------------------------------------

        response_text = self._resolve_response_text(
            execution_result
        )

        if response_text is None:
            return self._failure_result(
                stage="response",
                error=(
                    "Voice command execution completed "
                    "without a usable response."
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
                execution_result=execution_result,
            )

        # ----------------------------------------------------
        # 5. Text → Voice
        # ----------------------------------------------------

        try:
            response_result = (
                self._voice_response_executor.execute(
                    response_text,
                    runtime_context_id=(
                        execution_result.get(
                            "context_id"
                        )
                    ),
                    execution_id=(
                        execution_result.get(
                            "execution_id"
                        )
                    ),
                    metadata={
                        "conversation_loop": self.LOOP_NAME,
                    },
                )
            )

        except Exception as exc:
            return self._failure_result(
                stage="response",
                error=str(exc),
                voice_input=voice_input,
                transcription_result=transcription_result,
                execution_result=execution_result,
            )

        if not isinstance(
            response_result,
            MultimodalInputResult,
        ):
            return self._failure_result(
                stage="response",
                error=(
                    "Voice response executor returned "
                    "an invalid result."
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
                execution_result=execution_result,
            )

        if not response_result.is_successful():
            return self._failure_result(
                stage="response",
                error=(
                    response_result.get_error(
                        "Voice response execution failed."
                    )
                ),
                voice_input=voice_input,
                transcription_result=transcription_result,
                execution_result=execution_result,
                response_result=response_result,
            )

        # ----------------------------------------------------
        # 6. Complete Conversation Result
        # ----------------------------------------------------

        return {
            "success": True,
            "status": "completed",
            "stage": "completed",
            "conversation_loop": self.LOOP_NAME,
            "voice_input": voice_input,
            "transcription_result": transcription_result,
            "transcription": transcription,
            "execution_result": execution_result,
            "response_text": response_text,
            "response_result": response_result,
        }

    # ========================================================
    # Response Resolution
    # ========================================================

    @staticmethod
    def _resolve_response_text(
        execution_result: Dict[str, Any],
    ) -> Optional[str]:
        """
        Resolve a TTS-safe response string from an execution result.

        String results are used directly.

        Other primitive values are converted to strings.

        Complex structures are intentionally not converted
        automatically because arbitrary dictionaries or lists
        may not represent a user-facing response.
        """

        result = execution_result.get("result")

        if isinstance(result, str):
            text = result.strip()
            return text or None

        if result is None:
            return None

        if isinstance(
            result,
            (int, float, bool),
        ):
            return str(result)

        return None

    # ========================================================
    # Failure Handling
    # ========================================================

    @staticmethod
    def _failure_result(
        *,
        stage: str,
        error: str,
        voice_input: Optional[VoiceInput] = None,
        transcription_result: Optional[
            MultimodalInputResult
        ] = None,
        execution_result: Optional[
            Dict[str, Any]
        ] = None,
        response_result: Optional[
            MultimodalInputResult
        ] = None,
    ) -> Dict[str, Any]:
        """Build a structured conversation failure result."""

        return {
            "success": False,
            "status": "failed",
            "stage": stage,
            "conversation_loop": VoiceConversationLoop.LOOP_NAME,
            "error": error,
            "voice_input": voice_input,
            "transcription_result": transcription_result,
            "execution_result": execution_result,
            "response_result": response_result,
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "VoiceConversationLoop("
            f"name={self.LOOP_NAME!r}"
            ")"
        )


__all__ = [
    "VoiceConversationLoop",
    "VoiceConversationLoopError",
]