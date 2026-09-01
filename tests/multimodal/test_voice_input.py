"""
Tests for Ultron Voice Input.

v0.52 — Voice Input Layer
"""

from datetime import datetime, timezone

import pytest

from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import (
    VoiceInput,
    VoiceInputError,
)


# ============================================================
# Helpers
# ============================================================


def create_voice_input(**overrides):
    data = {
        "audio_data": b"voice-data",
        "source": "microphone",
        "audio_format": "wav",
        "sample_rate": 16000,
        "channels": 1,
        "duration": 2.5,
    }

    data.update(overrides)

    return VoiceInput(**data)


# ============================================================
# Construction
# ============================================================


def test_voice_input_creation():
    voice = create_voice_input()

    assert isinstance(voice, VoiceInput)
    assert voice.input_type is InputType.VOICE
    assert voice.audio_data == b"voice-data"
    assert voice.source == "microphone"
    assert voice.audio_format == "wav"
    assert voice.sample_rate == 16000
    assert voice.channels == 1
    assert voice.duration == 2.5


def test_voice_input_generates_id():
    voice = create_voice_input()

    assert isinstance(voice.id, str)
    assert voice.id


def test_voice_input_accepts_custom_id():
    voice = create_voice_input(
        input_id="voice-001"
    )

    assert voice.id == "voice-001"


def test_voice_input_accepts_custom_timestamp():
    timestamp = datetime(
        2026,
        8,
        31,
        tzinfo=timezone.utc,
    )

    voice = create_voice_input(
        created_at=timestamp
    )

    assert voice.created_at == timestamp


# ============================================================
# Input Type
# ============================================================


def test_voice_input_is_voice():
    voice = create_voice_input()

    assert voice.is_voice() is True


def test_voice_input_type_is_voice():
    voice = create_voice_input()

    assert voice.input_type is InputType.VOICE


# ============================================================
# Audio Data
# ============================================================


def test_get_audio_data_returns_copy():
    audio = bytearray(b"voice-data")

    voice = create_voice_input(
        audio_data=audio
    )

    returned = voice.get_audio_data()

    assert returned == audio
    assert returned is not audio


def test_get_audio_data_returns_value_for_bytes():
    voice = create_voice_input(
        audio_data=b"audio"
    )

    assert voice.get_audio_data() == b"audio"


def test_set_audio_data():
    voice = create_voice_input()

    voice.set_audio_data(
        b"new-audio"
    )

    assert voice.audio_data == b"new-audio"


def test_set_audio_data_rejects_none():
    voice = create_voice_input()

    with pytest.raises(
        VoiceInputError,
        match="audio_data cannot be None",
    ):
        voice.set_audio_data(None)


def test_none_audio_data_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="audio_data cannot be None",
    ):
        create_voice_input(
            audio_data=None
        )


# ============================================================
# Audio Format
# ============================================================


@pytest.mark.parametrize(
    "audio_format",
    [
        "wav",
        "mp3",
        "m4a",
        "ogg",
        "flac",
        "webm",
        "pcm",
        "raw",
    ],
)
def test_supported_audio_formats(
    audio_format,
):
    voice = create_voice_input(
        audio_format=audio_format
    )

    assert voice.audio_format == audio_format


def test_audio_format_is_normalized():
    voice = create_voice_input(
        audio_format="  WAV  "
    )

    assert voice.audio_format == "wav"


def test_audio_format_is_case_insensitive():
    voice = create_voice_input(
        audio_format="FLAC"
    )

    assert voice.audio_format == "flac"


def test_none_audio_format_is_allowed():
    voice = create_voice_input(
        audio_format=None
    )

    assert voice.audio_format is None


def test_invalid_audio_format_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="Unsupported audio format",
    ):
        create_voice_input(
            audio_format="invalid"
        )


def test_empty_audio_format_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="audio_format cannot be empty",
    ):
        create_voice_input(
            audio_format="   "
        )


def test_non_string_audio_format_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="audio_format must be a string",
    ):
        create_voice_input(
            audio_format=123
        )


# ============================================================
# Sample Rate
# ============================================================


def test_sample_rate():
    voice = create_voice_input(
        sample_rate=44100
    )

    assert voice.sample_rate == 44100
    assert voice.get_sample_rate() == 44100


def test_none_sample_rate_is_allowed():
    voice = create_voice_input(
        sample_rate=None
    )

    assert voice.sample_rate is None


def test_zero_sample_rate_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="sample_rate must be greater than zero",
    ):
        create_voice_input(
            sample_rate=0
        )


def test_negative_sample_rate_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="sample_rate must be greater than zero",
    ):
        create_voice_input(
            sample_rate=-16000
        )


def test_non_integer_sample_rate_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="sample_rate must be an integer",
    ):
        create_voice_input(
            sample_rate=16000.5
        )


def test_boolean_sample_rate_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="sample_rate must be an integer",
    ):
        create_voice_input(
            sample_rate=True
        )


# ============================================================
# Channels
# ============================================================


def test_channels():
    voice = create_voice_input(
        channels=2
    )

    assert voice.channels == 2
    assert voice.get_channels() == 2


def test_none_channels_is_allowed():
    voice = create_voice_input(
        channels=None
    )

    assert voice.channels is None


def test_zero_channels_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="channels must be greater than zero",
    ):
        create_voice_input(
            channels=0
        )


def test_negative_channels_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="channels must be greater than zero",
    ):
        create_voice_input(
            channels=-1
        )


def test_non_integer_channels_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="channels must be an integer",
    ):
        create_voice_input(
            channels=1.5
        )


def test_boolean_channels_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="channels must be an integer",
    ):
        create_voice_input(
            channels=True
        )


# ============================================================
# Duration
# ============================================================


def test_duration():
    voice = create_voice_input(
        duration=4.75
    )

    assert voice.duration == 4.75
    assert voice.get_duration() == 4.75


def test_integer_duration_is_allowed():
    voice = create_voice_input(
        duration=5
    )

    assert voice.duration == 5


def test_none_duration_is_allowed():
    voice = create_voice_input(
        duration=None
    )

    assert voice.duration is None


def test_zero_duration_is_allowed():
    voice = create_voice_input(
        duration=0
    )

    assert voice.duration == 0


def test_negative_duration_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="duration cannot be negative",
    ):
        create_voice_input(
            duration=-1
        )


def test_invalid_duration_type_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="duration must be a number",
    ):
        create_voice_input(
            duration="2.5"
        )


def test_boolean_duration_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="duration must be a number",
    ):
        create_voice_input(
            duration=True
        )


# ============================================================
# Source
# ============================================================


def test_source():
    voice = create_voice_input(
        source="microphone"
    )

    assert voice.source == "microphone"


def test_none_source_is_allowed():
    voice = create_voice_input(
        source=None
    )

    assert voice.source is None


def test_empty_source_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="source cannot be empty",
    ):
        create_voice_input(
            source="   "
        )


def test_non_string_source_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="source must be a string",
    ):
        create_voice_input(
            source=123
        )


# ============================================================
# Metadata
# ============================================================


def test_metadata():
    voice = create_voice_input(
        metadata={
            "device": "default-mic",
            "language": "en-US",
        }
    )

    assert voice.get_metadata(
        "device"
    ) == "default-mic"

    assert voice.get_metadata(
        "language"
    ) == "en-US"


def test_metadata_default():
    voice = create_voice_input()

    assert voice.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_set_metadata():
    voice = create_voice_input()

    voice.set_metadata(
        "language",
        "en-US",
    )

    assert voice.get_metadata(
        "language"
    ) == "en-US"


def test_get_all_metadata_returns_copy():
    metadata = {
        "device": "mic"
    }

    voice = create_voice_input(
        metadata=metadata
    )

    returned = voice.get_all_metadata()

    returned["device"] = "changed"

    assert voice.get_metadata(
        "device"
    ) == "mic"


def test_metadata_is_deep_copied():
    metadata = {
        "nested": {
            "value": 1
        }
    }

    voice = create_voice_input(
        metadata=metadata
    )

    metadata["nested"]["value"] = 99

    assert (
        voice.get_metadata(
            "nested"
        )["value"]
        == 1
    )


def test_empty_metadata_key_is_rejected():
    voice = create_voice_input()

    with pytest.raises(
        VoiceInputError,
        match="Metadata key cannot be empty",
    ):
        voice.set_metadata(
            "   ",
            "value",
        )


def test_non_string_metadata_key_is_rejected():
    voice = create_voice_input()

    with pytest.raises(
        VoiceInputError,
        match="Metadata key must be a string",
    ):
        voice.set_metadata(
            123,
            "value",
        )


def test_metadata_must_be_dict():
    with pytest.raises(
        VoiceInputError,
        match="metadata must be a dictionary",
    ):
        create_voice_input(
            metadata="invalid"
        )


# ============================================================
# Conversion to MultimodalInput
# ============================================================


def test_to_multimodal_input():
    voice = create_voice_input()

    multimodal = voice.to_multimodal_input()

    assert multimodal.id == voice.id
    assert multimodal.input_type is InputType.VOICE
    assert multimodal.source == voice.source
    assert multimodal.get_data() == voice.audio_data


def test_to_multimodal_input_preserves_audio_metadata():
    voice = create_voice_input(
        audio_format="wav",
        sample_rate=16000,
        channels=1,
        duration=3.2,
    )

    multimodal = voice.to_multimodal_input()

    assert multimodal.get_metadata(
        "audio_format"
    ) == "wav"

    assert multimodal.get_metadata(
        "sample_rate"
    ) == 16000

    assert multimodal.get_metadata(
        "channels"
    ) == 1

    assert multimodal.get_metadata(
        "duration"
    ) == 3.2


def test_to_multimodal_input_preserves_custom_metadata():
    voice = create_voice_input(
        metadata={
            "language": "en-US",
            "device": "microphone",
        }
    )

    multimodal = voice.to_multimodal_input()

    assert multimodal.get_metadata(
        "language"
    ) == "en-US"

    assert multimodal.get_metadata(
        "device"
    ) == "microphone"


# ============================================================
# Validity
# ============================================================


def test_is_valid():
    voice = create_voice_input()

    assert voice.is_valid() is True


def test_is_valid_with_optional_audio_metadata_missing():
    voice = create_voice_input(
        audio_format=None,
        sample_rate=None,
        channels=None,
        duration=None,
    )

    assert voice.is_valid() is True


# ============================================================
# Serialization
# ============================================================


def test_to_dict():
    voice = create_voice_input()

    result = voice.to_dict()

    assert result["id"] == voice.id
    assert result["input_type"] == "voice"
    assert result["audio_data"] == b"voice-data"
    assert result["source"] == "microphone"
    assert result["audio_format"] == "wav"
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert result["duration"] == 2.5
    assert "created_at" in result


def test_to_dict_returns_metadata_copy():
    voice = create_voice_input(
        metadata={
            "device": "mic"
        }
    )

    result = voice.to_dict()

    result["metadata"]["device"] = "changed"

    assert voice.get_metadata(
        "device"
    ) == "mic"


# ============================================================
# ID
# ============================================================


def test_get_id():
    voice = create_voice_input(
        input_id="voice-123"
    )

    assert voice.get_id() == "voice-123"


def test_empty_input_id_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="input_id cannot be empty",
    ):
        create_voice_input(
            input_id="   "
        )


def test_non_string_input_id_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="input_id must be a string",
    ):
        create_voice_input(
            input_id=123
        )


# ============================================================
# Timestamp
# ============================================================


def test_invalid_created_at_is_rejected():
    with pytest.raises(
        VoiceInputError,
        match="created_at must be a datetime",
    ):
        create_voice_input(
            created_at="invalid"
        )


# ============================================================
# Representation
# ============================================================


def test_repr():
    voice = create_voice_input(
        input_id="voice-001",
        audio_format="wav",
        source="microphone",
        duration=2.5,
    )

    representation = repr(voice)

    assert "VoiceInput" in representation
    assert "voice-001" in representation
    assert "wav" in representation
    assert "microphone" in representation
    assert "2.5" in representation