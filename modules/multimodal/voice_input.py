"""
Ultron Voice Input.

v0.52 — Voice Input Layer

Provides a standardized representation for audio/voice
inputs entering the Ultron multimodal runtime.

This module represents and validates voice input data.
Speech-to-text processing is intentionally kept outside
this class so that STT providers can remain modular.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from modules.multimodal.input import (
    MultimodalInput,
    MultimodalInputError,
)
from modules.multimodal.input_type import InputType


class VoiceInputError(Exception):
    """Base exception for voice input errors."""


class VoiceInput:
    """
    Represents a normalized voice/audio input.

    VoiceInput is responsible for representing audio data
    and its associated metadata. It does not perform
    speech-to-text processing.

    Architecture:

        Audio Source
              |
              v
          VoiceInput
              |
              v
       MultimodalInput
              |
              v
         InputRouter
              |
              v
        Voice Handler
              |
              v
          STT Layer
    """

    SUPPORTED_FORMATS = {
        "wav",
        "mp3",
        "m4a",
        "ogg",
        "flac",
        "webm",
        "pcm",
        "raw",
    }

    def __init__(
        self,
        audio_data: Any,
        *,
        input_id: str | None = None,
        source: str | None = None,
        audio_format: str | None = None,
        sample_rate: int | None = None,
        channels: int | None = None,
        duration: float | None = None,
        metadata: Dict[str, Any] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        """
        Initialize a voice input.

        Parameters:
            audio_data:
                Raw or normalized audio payload.

            input_id:
                Optional unique input identifier.

            source:
                Optional source such as microphone or audio file.

            audio_format:
                Audio format such as wav, mp3, or flac.

            sample_rate:
                Audio sample rate in Hz.

            channels:
                Number of audio channels.

            duration:
                Audio duration in seconds.

            metadata:
                Optional additional audio metadata.

            created_at:
                Optional creation timestamp.
        """

        self._validate_audio_data(audio_data)

        if input_id is not None:
            if not isinstance(input_id, str):
                raise VoiceInputError(
                    "input_id must be a string or None."
                )

            if not input_id.strip():
                raise VoiceInputError(
                    "input_id cannot be empty."
                )

        if source is not None:
            if not isinstance(source, str):
                raise VoiceInputError(
                    "source must be a string or None."
                )

            if not source.strip():
                raise VoiceInputError(
                    "source cannot be empty."
                )

        normalized_format = self._normalize_format(
            audio_format
        )

        self._validate_sample_rate(
            sample_rate
        )

        self._validate_channels(
            channels
        )

        self._validate_duration(
            duration
        )

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise VoiceInputError(
                "metadata must be a dictionary or None."
            )

        if created_at is not None and not isinstance(
            created_at,
            datetime,
        ):
            raise VoiceInputError(
                "created_at must be a datetime or None."
            )

        self.id = (
            input_id
            if input_id is not None
            else str(uuid4())
        )

        self.input_type = InputType.VOICE
        self.audio_data = audio_data
        self.source = source
        self.audio_format = normalized_format
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration

        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

        self.created_at = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc)
        )

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_audio_data(
        audio_data: Any,
    ) -> None:
        """Validate that audio data is present."""

        if audio_data is None:
            raise VoiceInputError(
                "audio_data cannot be None."
            )

    @classmethod
    def _normalize_format(
        cls,
        audio_format: str | None,
    ) -> str | None:
        """Normalize and validate audio format."""

        if audio_format is None:
            return None

        if not isinstance(
            audio_format,
            str,
        ):
            raise VoiceInputError(
                "audio_format must be a string or None."
            )

        normalized = audio_format.strip().lower()

        if not normalized:
            raise VoiceInputError(
                "audio_format cannot be empty."
            )

        if normalized not in cls.SUPPORTED_FORMATS:
            raise VoiceInputError(
                f"Unsupported audio format: {normalized}"
            )

        return normalized

    @staticmethod
    def _validate_sample_rate(
        sample_rate: int | None,
    ) -> None:
        """Validate sample rate."""

        if sample_rate is None:
            return

        if isinstance(
            sample_rate,
            bool,
        ) or not isinstance(
            sample_rate,
            int,
        ):
            raise VoiceInputError(
                "sample_rate must be an integer or None."
            )

        if sample_rate <= 0:
            raise VoiceInputError(
                "sample_rate must be greater than zero."
            )

    @staticmethod
    def _validate_channels(
        channels: int | None,
    ) -> None:
        """Validate audio channels."""

        if channels is None:
            return

        if isinstance(
            channels,
            bool,
        ) or not isinstance(
            channels,
            int,
        ):
            raise VoiceInputError(
                "channels must be an integer or None."
            )

        if channels <= 0:
            raise VoiceInputError(
                "channels must be greater than zero."
            )

    @staticmethod
    def _validate_duration(
        duration: float | None,
    ) -> None:
        """Validate audio duration."""

        if duration is None:
            return

        if isinstance(
            duration,
            bool,
        ) or not isinstance(
            duration,
            (int, float),
        ):
            raise VoiceInputError(
                "duration must be a number or None."
            )

        if duration < 0:
            raise VoiceInputError(
                "duration cannot be negative."
            )

    # ========================================================
    # Audio Data
    # ========================================================

    def get_audio_data(self) -> Any:
        """Return a defensive copy of audio data."""

        try:
            return deepcopy(
                self.audio_data
            )
        except Exception:
            return self.audio_data

    def set_audio_data(
        self,
        audio_data: Any,
    ) -> None:
        """Replace the audio payload."""

        self._validate_audio_data(
            audio_data
        )

        self.audio_data = audio_data

    # ========================================================
    # Input ID
    # ========================================================

    def get_id(self) -> str:
        """Return the unique input identifier."""

        return self.id

    # ========================================================
    # Type
    # ========================================================

    def is_voice(self) -> bool:
        """Return True for voice input."""

        return self.input_type is InputType.VOICE

    # ========================================================
    # Audio Properties
    # ========================================================

    def get_format(self) -> str | None:
        """Return the normalized audio format."""

        return self.audio_format

    def get_sample_rate(self) -> int | None:
        """Return the sample rate."""

        return self.sample_rate

    def get_channels(self) -> int | None:
        """Return the number of audio channels."""

        return self.channels

    def get_duration(self) -> float | None:
        """Return the audio duration."""

        return self.duration

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """Set voice input metadata."""

        if not isinstance(
            key,
            str,
        ):
            raise VoiceInputError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceInputError(
                "Metadata key cannot be empty."
            )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """Retrieve voice input metadata."""

        if not isinstance(
            key,
            str,
        ):
            raise VoiceInputError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise VoiceInputError(
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
    # Conversion
    # ========================================================

    def to_multimodal_input(
        self,
    ) -> MultimodalInput:
        """
        Convert this voice input into a MultimodalInput.

        The resulting input uses InputType.VOICE and carries
        voice-specific properties through metadata.
        """

        metadata = self.get_all_metadata()

        metadata.update(
            {
                "audio_format": self.audio_format,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
                "duration": self.duration,
            }
        )

        try:
            return MultimodalInput(
                InputType.VOICE,
                self.get_audio_data(),
                input_id=self.id,
                source=self.source,
                metadata=metadata,
                created_at=self.created_at,
            )
        except MultimodalInputError as exc:
            raise VoiceInputError(
                str(exc)
            ) from exc

    # ========================================================
    # Validation State
    # ========================================================

    def is_valid(self) -> bool:
        """
        Return True when the voice input passes validation.

        Construction already validates required fields, so
        this method provides a simple runtime validity check.
        """

        try:
            self._validate_audio_data(
                self.audio_data
            )

            self._normalize_format(
                self.audio_format
            )

            self._validate_sample_rate(
                self.sample_rate
            )

            self._validate_channels(
                self.channels
            )

            self._validate_duration(
                self.duration
            )

            return True

        except VoiceInputError:
            return False

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the voice input into a dictionary."""

        return {
            "id": self.id,
            "input_type": self.input_type.value,
            "audio_data": self.get_audio_data(),
            "source": self.source,
            "audio_format": self.audio_format,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "duration": self.duration,
            "metadata": self.get_all_metadata(),
            "created_at": self.created_at.isoformat(),
        }

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""

        return (
            "VoiceInput("
            f"id={self.id!r}, "
            f"audio_format={self.audio_format!r}, "
            f"source={self.source!r}, "
            f"duration={self.duration!r}"
            ")"
        )


__all__ = [
    "VoiceInput",
    "VoiceInputError",
]