"""
Tests for Ultron Multimodal Input Types.

v0.51 — Multimodal Input Foundation
"""

import pytest

from modules.multimodal.input_type import InputType


def test_input_types_exist():
    assert InputType.TEXT.value == "text"
    assert InputType.VOICE.value == "voice"
    assert InputType.VISION.value == "vision"
    assert InputType.GESTURE.value == "gesture"
    assert InputType.UNKNOWN.value == "unknown"


def test_from_value_accepts_string():
    assert InputType.from_value("text") is InputType.TEXT
    assert InputType.from_value("voice") is InputType.VOICE
    assert InputType.from_value("vision") is InputType.VISION
    assert InputType.from_value("gesture") is InputType.GESTURE


def test_from_value_normalizes_string():
    assert InputType.from_value(" TEXT ") is InputType.TEXT
    assert InputType.from_value("Voice") is InputType.VOICE
    assert InputType.from_value("VISION") is InputType.VISION
    assert InputType.from_value(" Gesture ") is InputType.GESTURE


def test_from_value_accepts_existing_enum():
    assert InputType.from_value(InputType.TEXT) is InputType.TEXT
    assert InputType.from_value(InputType.VOICE) is InputType.VOICE


def test_from_value_rejects_invalid_value():
    with pytest.raises(ValueError):
        InputType.from_value("invalid")


def test_from_value_rejects_non_string():
    with pytest.raises(ValueError):
        InputType.from_value(123)


def test_is_supported():
    assert InputType.is_supported("text") is True
    assert InputType.is_supported("voice") is True
    assert InputType.is_supported("vision") is True
    assert InputType.is_supported("gesture") is True


def test_unknown_is_not_supported():
    assert InputType.is_supported("unknown") is False
    assert InputType.UNKNOWN.is_unknown() is True


def test_values():
    assert InputType.values() == (
        "text",
        "voice",
        "vision",
        "gesture",
        "unknown",
    )


def test_type_helpers():
    assert InputType.TEXT.is_text() is True
    assert InputType.VOICE.is_voice() is True
    assert InputType.VISION.is_vision() is True
    assert InputType.GESTURE.is_gesture() is True


def test_type_helpers_return_false_for_other_types():
    assert InputType.TEXT.is_voice() is False
    assert InputType.VOICE.is_vision() is False
    assert InputType.VISION.is_gesture() is False
    assert InputType.GESTURE.is_text() is False