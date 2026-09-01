"""
Ultron Voice Input Integration Tests.

v0.52 — Voice Input Layer

Tests the end-to-end integration between:

VoiceInput
    ↓
MultimodalInput
    ↓
InputRouter
    ↓
Voice Handler
    ↓
MultimodalInputResult
"""

from __future__ import annotations

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.input_router import (
    InputRouter,
)
from modules.multimodal.input_type import (
    InputType,
)
from modules.multimodal.voice_input import (
    VoiceInput,
)


def test_voice_input_converts_to_multimodal_input() -> None:
    voice_input = VoiceInput(
        b"voice-data",
        input_id="voice-001",
        source="microphone",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=2.5,
    )

    multimodal_input = voice_input.to_multimodal_input()

    assert multimodal_input.id == "voice-001"
    assert multimodal_input.input_type is InputType.VOICE
    assert multimodal_input.data == b"voice-data"
    assert multimodal_input.source == "microphone"


def test_voice_audio_metadata_is_preserved() -> None:
    voice_input = VoiceInput(
        b"voice-data",
        input_id="voice-002",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=3.0,
    )

    multimodal_input = voice_input.to_multimodal_input()

    assert multimodal_input.metadata["audio_format"] == "wav"
    assert multimodal_input.metadata["sample_rate"] == 16000
    assert multimodal_input.metadata["channels"] == 1
    assert multimodal_input.metadata["duration"] == 3.0


def test_voice_input_routes_to_voice_handler() -> None:
    received = []

    def voice_handler(data):
        received.append(data)
        return "transcribed voice"

    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        voice_handler,
    )

    voice_input = VoiceInput(
        b"audio-payload",
        input_id="voice-003",
    )

    multimodal_input = voice_input.to_multimodal_input()

    result = router.route(
        multimodal_input
    )

    assert received == [b"audio-payload"]
    assert isinstance(
        result,
        MultimodalInputResult,
    )
    assert result.input_id == "voice-003"
    assert result.input_type is InputType.VOICE
    assert result.status == "completed"


def test_voice_input_result_preserves_identity() -> None:
    voice_input = VoiceInput(
        b"audio",
        input_id="voice-004",
    )

    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        lambda data: "processed",
    )

    result = router.route(
        voice_input.to_multimodal_input()
    )

    assert result.input_id == voice_input.id
    assert result.input_type is InputType.VOICE


def test_voice_handler_receives_original_audio_data() -> None:
    received = {}

    def voice_handler(data):
        received["data"] = data
        return {"text": "hello"}

    router = InputRouter(
        handlers={
            InputType.VOICE: voice_handler,
        }
    )

    voice_input = VoiceInput(
        b"raw-audio",
        input_id="voice-005",
    )

    result = router.route(
        voice_input.to_multimodal_input()
    )

    assert received["data"] == b"raw-audio"
    assert result.status == "completed"


def test_voice_handler_failure_returns_failed_result() -> None:
    def voice_handler(data):
        raise RuntimeError("voice processing failed")

    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        voice_handler,
    )

    voice_input = VoiceInput(
        b"audio",
        input_id="voice-006",
    )

    result = router.route(
        voice_input.to_multimodal_input()
    )

    assert isinstance(
        result,
        MultimodalInputResult,
    )
    assert result.input_id == "voice-006"
    assert result.input_type is InputType.VOICE
    assert result.status == "failed"
    assert result.error == "voice processing failed"


def test_voice_input_end_to_end_flow() -> None:
    processed = []

    def voice_handler(data):
        processed.append(data)
        return {
            "transcription": "hello ultron",
        }

    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        voice_handler,
    )

    voice_input = VoiceInput(
        b"voice-stream",
        input_id="voice-e2e-001",
        source="microphone",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=1.8,
        metadata={
            "device": "microphone",
        },
    )

    multimodal_input = voice_input.to_multimodal_input()

    result = router.route(
        multimodal_input
    )

    assert processed == [b"voice-stream"]

    assert result.input_id == "voice-e2e-001"
    assert result.input_type is InputType.VOICE
    assert result.status == "completed"
    assert result.data == {
        "transcription": "hello ultron",
    }


def test_voice_input_metadata_reaches_router_input() -> None:
    voice_input = VoiceInput(
        b"audio",
        input_id="voice-007",
        metadata={
            "device": "headset",
            "language": "en",
        },
    )

    multimodal_input = voice_input.to_multimodal_input()

    assert multimodal_input.metadata["device"] == "headset"
    assert multimodal_input.metadata["language"] == "en"
    assert multimodal_input.input_type is InputType.VOICE


def test_voice_input_is_valid_before_routing() -> None:
    voice_input = VoiceInput(
        b"audio",
        input_id="voice-008",
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=2.0,
    )

    assert voice_input.is_valid() is True

    multimodal_input = voice_input.to_multimodal_input()

    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        lambda data: "ok",
    )

    result = router.route(
        multimodal_input
    )

    assert result.status == "completed"
