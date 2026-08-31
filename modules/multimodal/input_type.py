"""
Ultron Multimodal Input Types.

v0.51 — Multimodal Input Foundation

Defines the supported input modalities that can enter
the Ultron multimodal processing pipeline.
"""

from __future__ import annotations

from enum import Enum


class InputType(str, Enum):
    """
    Supported multimodal input types.

    TEXT:
        Traditional text input.

    VOICE:
        Spoken/audio input.

    VISION:
        Image or visual input.

    GESTURE:
        Hand/body gesture input.

    UNKNOWN:
        Unrecognized or unsupported input type.
    """

    TEXT = "text"
    VOICE = "voice"
    VISION = "vision"
    GESTURE = "gesture"
    UNKNOWN = "unknown"

    @classmethod
    def from_value(
        cls,
        value: str | "InputType",
    ) -> "InputType":
        """
        Convert a string or InputType value into InputType.
        """

        if isinstance(value, cls):
            return value

        if not isinstance(value, str):
            raise ValueError(
                "Input type must be a string or InputType."
            )

        normalized = value.strip().lower()

        for input_type in cls:
            if input_type.value == normalized:
                return input_type

        raise ValueError(
            f"Unsupported input type: {value!r}"
        )

    @classmethod
    def is_supported(
        cls,
        value: str | "InputType",
    ) -> bool:
        """
        Return True when the supplied value is supported.
        """

        try:
            input_type = cls.from_value(value)
        except ValueError:
            return False

        return input_type is not cls.UNKNOWN

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """
        Return all input type values.
        """

        return tuple(
            input_type.value
            for input_type in cls
        )

    def is_text(self) -> bool:
        """Return True when this is a text input."""

        return self is InputType.TEXT

    def is_voice(self) -> bool:
        """Return True when this is a voice input."""

        return self is InputType.VOICE

    def is_vision(self) -> bool:
        """Return True when this is a vision input."""

        return self is InputType.VISION

    def is_gesture(self) -> bool:
        """Return True when this is a gesture input."""

        return self is InputType.GESTURE

    def is_unknown(self) -> bool:
        """Return True when this is an unknown input."""

        return self is InputType.UNKNOWN


__all__ = [
    "InputType",
]