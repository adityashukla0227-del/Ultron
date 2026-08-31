"""
Tests for Ultron Multimodal Input.

v0.51 — Multimodal Input Foundation
"""

from datetime import datetime, timezone

import pytest

from modules.multimodal.input import (
    MultimodalInput,
    MultimodalInputError,
)
from modules.multimodal.input_type import InputType


# ========================================================
# Construction
# ========================================================


def test_create_text_input():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello Ultron",
    )

    assert item.input_type is InputType.TEXT
    assert item.data == "Hello Ultron"
    assert item.source is None


def test_create_input_with_string_type():
    item = MultimodalInput(
        "text",
        "Hello",
    )

    assert item.input_type is InputType.TEXT


def test_input_generates_id():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    assert isinstance(item.id, str)
    assert item.id


def test_custom_input_id():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
        input_id="input-001",
    )

    assert item.id == "input-001"


def test_custom_source():
    item = MultimodalInput(
        InputType.VOICE,
        b"audio",
        source="microphone",
    )

    assert item.source == "microphone"


def test_custom_metadata():
    item = MultimodalInput(
        InputType.VISION,
        b"image",
        metadata={
            "camera": "front",
            "confidence": 0.95,
        },
    )

    assert item.get_metadata("camera") == "front"
    assert item.get_metadata("confidence") == 0.95


def test_custom_created_at():
    timestamp = datetime.now(timezone.utc)

    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
        created_at=timestamp,
    )

    assert item.created_at == timestamp


# ========================================================
# Validation
# ========================================================


def test_invalid_input_type_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            "invalid",
            "Hello",
        )


def test_unknown_input_type_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.UNKNOWN,
            "Hello",
        )


def test_empty_input_id_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            input_id="",
        )


def test_non_string_input_id_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            input_id=123,
        )


def test_empty_source_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            source="",
        )


def test_non_string_source_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            source=123,
        )


def test_invalid_metadata_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            metadata="invalid",
        )


def test_invalid_created_at_raises():
    with pytest.raises(MultimodalInputError):
        MultimodalInput(
            InputType.TEXT,
            "Hello",
            created_at="invalid",
        )


# ========================================================
# Type Helpers
# ========================================================


def test_is_text():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    assert item.is_text()
    assert not item.is_voice()
    assert not item.is_vision()
    assert not item.is_gesture()


def test_is_voice():
    item = MultimodalInput(
        InputType.VOICE,
        b"audio",
    )

    assert item.is_voice()
    assert not item.is_text()


def test_is_vision():
    item = MultimodalInput(
        InputType.VISION,
        b"image",
    )

    assert item.is_vision()
    assert not item.is_text()


def test_is_gesture():
    item = MultimodalInput(
        InputType.GESTURE,
        {"gesture": "wave"},
    )

    assert item.is_gesture()
    assert not item.is_text()


# ========================================================
# Data
# ========================================================


def test_get_data_returns_data():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    assert item.get_data() == "Hello"


def test_get_data_returns_defensive_copy():
    payload = {
        "value": [1, 2, 3],
    }

    item = MultimodalInput(
        InputType.TEXT,
        payload,
    )

    result = item.get_data()

    result["value"].append(4)

    assert item.data == {
        "value": [1, 2, 3],
    }


def test_set_data():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    item.set_data("Updated")

    assert item.get_data() == "Updated"


# ========================================================
# Metadata
# ========================================================


def test_set_metadata():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    item.set_metadata(
        "language",
        "en",
    )

    assert item.get_metadata("language") == "en"


def test_get_metadata_default():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    assert item.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_get_all_metadata_returns_copy():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
        metadata={
            "key": "value",
        },
    )

    metadata = item.get_all_metadata()

    metadata["key"] = "changed"

    assert item.get_metadata("key") == "value"


def test_empty_metadata_key_raises():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    with pytest.raises(MultimodalInputError):
        item.set_metadata(
            "",
            "value",
        )


def test_non_string_metadata_key_raises():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    with pytest.raises(MultimodalInputError):
        item.set_metadata(
            123,
            "value",
        )


def test_get_metadata_invalid_key_raises():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
    )

    with pytest.raises(MultimodalInputError):
        item.get_metadata("")


# ========================================================
# Serialization
# ========================================================


def test_to_dict():
    timestamp = datetime.now(timezone.utc)

    item = MultimodalInput(
        InputType.VOICE,
        b"audio",
        input_id="voice-001",
        source="microphone",
        metadata={
            "format": "wav",
        },
        created_at=timestamp,
    )

    result = item.to_dict()

    assert result["id"] == "voice-001"
    assert result["input_type"] == "voice"
    assert result["data"] == b"audio"
    assert result["source"] == "microphone"
    assert result["metadata"] == {
        "format": "wav",
    }
    assert result["created_at"] == timestamp.isoformat()


# ========================================================
# Representation
# ========================================================


def test_repr():
    item = MultimodalInput(
        InputType.TEXT,
        "Hello",
        input_id="input-001",
        source="keyboard",
    )

    representation = repr(item)

    assert "MultimodalInput" in representation
    assert "input-001" in representation
    assert "text" in representation
    assert "keyboard" in representation