"""
Ultron Multimodal Input Result.

v0.51 — Multimodal Input Foundation

Represents the normalized result produced after
processing a multimodal input.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict

from modules.multimodal.input_type import InputType


class InputResultError(Exception):
    """Base exception for multimodal input result errors."""


class InputResult:
    """
    Represents the result of processing a multimodal input.

    The result starts in the ``created`` state by default.

    ``input_type`` is optional for backward compatibility and
    defaults to ``InputType.TEXT`` when omitted.
    """

    VALID_STATUSES = {
        "created",
        "processing",
        "completed",
        "failed",
        "skipped",
    }

    TERMINAL_STATUSES = {
        "completed",
        "failed",
        "skipped",
    }

    def __init__(
        self,
        *,
        input_id: str,
        input_type: str | InputType = InputType.TEXT,
        success: bool | None = None,
        data: Any = None,
        error: str | None = None,
        confidence: float | None = None,
        metadata: Dict[str, Any] | None = None,
        status: str | None = None,
        created_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> None:

        # ----------------------------------------------------
        # Input ID
        # ----------------------------------------------------

        if not isinstance(input_id, str):
            raise InputResultError(
                "input_id must be a string."
            )

        if not input_id.strip():
            raise InputResultError(
                "input_id cannot be empty."
            )

        # ----------------------------------------------------
        # Input Type
        # ----------------------------------------------------

        try:
            normalized_type = InputType.from_value(
                input_type
            )
        except (ValueError, TypeError) as exc:
            raise InputResultError(
                f"Invalid input type: {input_type!r}"
            ) from exc

        if normalized_type is InputType.UNKNOWN:
            raise InputResultError(
                "UNKNOWN input type cannot be used."
            )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        if status is None:
            normalized_status = "created"
        else:
            if not isinstance(status, str):
                raise InputResultError(
                    "status must be a string."
                )

            normalized_status = status.strip().lower()

            if normalized_status not in self.VALID_STATUSES:
                raise InputResultError(
                    f"Invalid result status: {normalized_status}"
                )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        if success is not None and not isinstance(
            success,
            bool,
        ):
            raise InputResultError(
                "success must be a boolean."
            )

        if success is None:
            success = normalized_status == "completed"

        # Keep lifecycle state and success flag consistent.
        if normalized_status == "completed":
            success = True
        elif normalized_status in {
            "created",
            "processing",
            "failed",
            "skipped",
        }:
            success = False

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        if confidence is not None:
            self._validate_confidence(
                confidence
            )

        # ----------------------------------------------------
        # Error
        # ----------------------------------------------------

        if error is not None:
            if not isinstance(error, str):
                raise InputResultError(
                    "error must be a string or None."
                )

            if not error.strip():
                raise InputResultError(
                    "error cannot be empty."
                )

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        if metadata is not None and not isinstance(
            metadata,
            dict,
        ):
            raise InputResultError(
                "metadata must be a dictionary or None."
            )

        # ----------------------------------------------------
        # Timestamps
        # ----------------------------------------------------

        if created_at is not None and not isinstance(
            created_at,
            datetime,
        ):
            raise InputResultError(
                "created_at must be a datetime or None."
            )

        if completed_at is not None and not isinstance(
            completed_at,
            datetime,
        ):
            raise InputResultError(
                "completed_at must be a datetime or None."
            )

        # ----------------------------------------------------
        # State
        # ----------------------------------------------------

        self.input_id = input_id
        self.input_type = normalized_type
        self.success = success
        self.data = data
        self.error = error
        self.confidence = confidence

        self.metadata: Dict[str, Any] = deepcopy(
            metadata or {}
        )

        self.status = normalized_status

        self.created_at = (
            created_at
            if created_at is not None
            else datetime.now(timezone.utc)
        )

        self.completed_at = completed_at

    # ========================================================
    # Status
    # ========================================================

    def is_created(self) -> bool:
        return self.status == "created"

    def is_processing(self) -> bool:
        return self.status == "processing"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def is_skipped(self) -> bool:
        return self.status == "skipped"

    def is_successful(self) -> bool:
        return self.success

    def is_unsuccessful(self) -> bool:
        return not self.success

    def is_terminal(self) -> bool:
        return self.status in self.TERMINAL_STATUSES

    # ========================================================
    # Lifecycle
    # ========================================================

    def start_processing(self) -> None:
        """
        Move the result into the processing state.

        Starting processing again while already processing
        is allowed and remains idempotent.
        """

        if self.is_terminal():
            raise InputResultError(
                "A terminal result cannot start processing."
            )

        self.status = "processing"
        self.success = False

    def complete(
        self,
        data: Any = None,
        *,
        confidence: float | None = None,
    ) -> None:
        """
        Mark the result as successfully completed.
        """

        if self.is_terminal():
            raise InputResultError(
                "A terminal result cannot be completed again."
            )

        if confidence is not None:
            self._validate_confidence(
                confidence
            )

        self.data = data

        if confidence is not None:
            self.confidence = confidence

        self.status = "completed"
        self.success = True
        self.error = None
        self.completed_at = datetime.now(
            timezone.utc
        )

    def fail(
        self,
        error: str,
    ) -> None:
        """
        Mark the result as failed.
        """

        if self.is_terminal():
            raise InputResultError(
                "A terminal result cannot be failed again."
            )

        if not isinstance(error, str):
            raise InputResultError(
                "error must be a string."
            )

        if not error.strip():
            raise InputResultError(
                "error cannot be empty."
            )

        self.status = "failed"
        self.success = False
        self.error = error
        self.completed_at = datetime.now(
            timezone.utc
        )

    def skip(
        self,
        reason: str | None = None,
    ) -> None:
        """
        Mark the result as skipped.
        """

        if self.is_terminal():
            raise InputResultError(
                "A terminal result cannot be skipped again."
            )

        if reason is not None:
            if not isinstance(reason, str):
                raise InputResultError(
                    "reason must be a string or None."
                )

            if not reason.strip():
                raise InputResultError(
                    "reason cannot be empty."
                )

            self.error = reason

        self.status = "skipped"
        self.success = False
        self.completed_at = datetime.now(
            timezone.utc
        )

    # ========================================================
    # Data
    # ========================================================

    def get_data(self) -> Any:
        """
        Return a defensive copy of result data.
        """

        try:
            return deepcopy(self.data)
        except Exception:
            return self.data

    def set_data(
        self,
        data: Any,
    ) -> None:
        self.data = data

    # ========================================================
    # Confidence
    # ========================================================

    def set_confidence(
        self,
        confidence: float | None,
    ) -> None:

        if confidence is not None:
            self._validate_confidence(
                confidence
            )

        self.confidence = confidence

    def has_confidence(self) -> bool:
        return self.confidence is not None

    # ========================================================
    # Error
    # ========================================================

    def has_error(self) -> bool:
        return self.error is not None

    def get_error(
        self,
        default: str | None = None,
    ) -> str | None:

        if self.error is None:
            return default

        return self.error

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._validate_metadata_key(key)

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        self._validate_metadata_key(key)

        return self.metadata.get(
            key,
            default,
        )

    def get_all_metadata(self) -> Dict[str, Any]:
        return deepcopy(
            self.metadata
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_id": self.input_id,
            "input_type": self.input_type.value,
            "success": self.success,
            "status": self.status,
            "data": self.get_data(),
            "error": self.error,
            "confidence": self.confidence,
            "metadata": self.get_all_metadata(),
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat()
                if self.completed_at is not None
                else None
            ),
        }

    # ========================================================
    # Validation Helpers
    # ========================================================

    @staticmethod
    def _validate_confidence(
        confidence: float | int,
    ) -> None:

        if isinstance(
            confidence,
            bool,
        ) or not isinstance(
            confidence,
            (int, float),
        ):
            raise InputResultError(
                "confidence must be a number."
            )

        if not 0.0 <= confidence <= 1.0:
            raise InputResultError(
                "confidence must be between 0.0 and 1.0."
            )

    @staticmethod
    def _validate_metadata_key(
        key: str,
    ) -> None:

        if not isinstance(key, str):
            raise InputResultError(
                "Metadata key must be a string."
            )

        if not key.strip():
            raise InputResultError(
                "Metadata key cannot be empty."
            )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            "MultimodalInputResult("
            f"input_id={self.input_id!r}, "
            f"status={self.status!r}, "
            f"confidence={self.confidence!r}"
            ")"
        )


# ============================================================
# Backward-compatible aliases
# ============================================================

MultimodalInputResult = InputResult
MultimodalInputResultError = InputResultError


__all__ = [
    "InputResult",
    "InputResultError",
    "MultimodalInputResult",
    "MultimodalInputResultError",
]