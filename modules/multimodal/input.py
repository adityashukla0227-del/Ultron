"""
Ultron Multimodal Input.

v0.51 — Multimodal Input Foundation

Provides a standardized representation for multimodal
inputs entering the Ultron runtime.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from modules.multimodal.input_type import InputType


class MultimodalInputError(Exception):
    """Base exception for multimodal input errors."""


class MultimodalInput:
    """
    Represents a single multimodal input.

    A MultimodalInput does not process the input itself.
    It only represents normalized input data that can later
    be routed to the appropriate modality handler.

    Architecture:

        User / Device
              |
              v
        MultimodalInput
              |
              v
          InputRouter
              |
              v
        Agent Runtime
    """

    def __init__(
        self,
        input_type: str | InputType,
        data: Any,
        *,
        input_id: str | None = None,
        source: str | None = None,
        metadata: Dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        """
        Initialize a multimodal input.

        Parameters:
            input_type:
                Type of input being represented.

            data:
                Raw or normalized input payload.

            input_id:
                Optional unique input identifier.

            source:
                Optional source identifier such as keyboard,
                microphone, camera, or gesture sensor.

            metadata:
                Optional input-specific metadata.

            created_at:
                Optional creation timestamp.
        """

        try:
            normalized_type = InputType.from_value(
                input_type
            )
        except ValueError as exc:
            raise MultimodalInputError(
                str(exc)
            ) from exc

        if normalized_type is InputType.UNKNOWN:
            raise MultimodalInputError(
                "UNKNOWN input type cannot be used."
            )

        if input_id is not None:
            if not isinstance(input_id, str):
                raise MultimodalInputError(
                    "input_id must be a string or None."
                )

            if not input_id.strip():
                raise MultimodalInputError(
                    "input_id cannot be empty."
                )

        if source is not None:
            if not isinstance(source, str):
                raise MultimodalInputError(
                    "source must be a string or None."
                )

            if not source.strip():
                raise MultimodalInputError(
                    "source cannot be empty."
                )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise MultimodalInputError(
                "metadata must be a dictionary or None."
            )

        if created_at is not None and not isinstance(
            created_at,
            datetime,
        ):
            raise MultimodalInputError(
                "created_at must be a datetime or None."
            )

        self.id = (
            input_id
            if input_id is not None
            else str(uuid4())
        )

        self.input_type = normalized_type
        self.data = data
        self.source = source
        self.metadata: Dict[str, Any] = dict(
            metadata or {}
        )

        self.created_at = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc)
        )

    # ========================================================
    # Type
    # ========================================================

    def is_text(self) -> bool:
        """Return True when this input is text."""

        return self.input_type is InputType.TEXT

    def is_voice(self) -> bool:
        """Return True when this input is voice/audio."""

        return self.input_type is InputType.VOICE

    def is_vision(self) -> bool:
        """Return True when this input is visual."""

        return self.input_type is InputType.VISION

    def is_gesture(self) -> bool:
        """Return True when this input is a gesture."""

        return self.input_type is InputType.GESTURE

    # ========================================================
    # Data
    # ========================================================

    def get_data(self) -> Any:
        """Return a defensive copy of the input data."""

        try:
            return deepcopy(self.data)
        except Exception:
            return self.data

    def set_data(
        self,
        data: Any,
    ) -> None:
        """Replace the input payload."""

        self.data = data

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set input metadata."""

        if not isinstance(key, str):
            raise MultimodalInputError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise MultimodalInputError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve input metadata."""

        if not isinstance(key, str):
            raise MultimodalInputError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise MultimodalInputError(
                "Metadata key cannot be empty."
            )

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        """Return a defensive copy of all metadata."""

        return deepcopy(
            self.metadata
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the multimodal input into a dictionary.
        """

        return {
            "id": self.id,
            "input_type": self.input_type.value,
            "data": self.get_data(),
            "source": self.source,
            "metadata": self.get_all_metadata(),
            "created_at": self.created_at.isoformat(),
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            "MultimodalInput("
            f"id={self.id!r}, "
            f"input_type={self.input_type.value!r}, "
            f"source={self.source!r}"
            ")"
        )


__all__ = [
    "MultimodalInput",
    "MultimodalInputError",
]