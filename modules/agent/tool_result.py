"""
Ultron Tool Result
Version: v0.38

Standardized result model for Ultron Agent Tools.

Responsibilities:
- Store tool execution result
- Track success/failure
- Store tool name
- Store error information
- Track execution timestamps
- Calculate execution duration
- Serialize results
- Restore results
"""

from datetime import datetime
from typing import Any, Dict, Optional


class ToolResult:
    """
    Standardized result returned by an AgentTool execution.
    """

    def __init__(
        self,
        tool_name: str,
        success: bool,
        result: Any = None,
        error: Optional[str] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
    ) -> None:

        self.tool_name = (
            tool_name.strip()
            if isinstance(tool_name, str)
            else tool_name
        )

        self.success = bool(
            success
        )

        self.result = result

        self.error = error

        self.started_at = (
            started_at
            if started_at
            else datetime.now().isoformat()
        )

        self.finished_at = (
            finished_at
            if finished_at
            else datetime.now().isoformat()
        )

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the ToolResult.
        """

        if not isinstance(
            self.tool_name,
            str,
        ):
            raise ValueError(
                "Tool name must be a string."
            )

        if not self.tool_name.strip():
            raise ValueError(
                "Tool name is required."
            )

        if not isinstance(
            self.success,
            bool,
        ):
            raise ValueError(
                "Success state must be a boolean."
            )

        if (
            self.error is not None
            and not isinstance(
                self.error,
                str,
            )
        ):
            raise ValueError(
                "Tool error must be a string or None."
            )

        return True

    # ========================================================
    # State
    # ========================================================

    def is_success(self) -> bool:
        """
        Return True when execution succeeded.
        """

        return self.success

    def is_failure(self) -> bool:
        """
        Return True when execution failed.
        """

        return not self.success

    # ========================================================
    # Duration
    # ========================================================

    def execution_duration(self) -> Optional[float]:
        """
        Return execution duration in seconds.

        Returns None when timestamps cannot be parsed.
        """

        try:

            started = datetime.fromisoformat(
                self.started_at
            )

            finished = datetime.fromisoformat(
                self.finished_at
            )

            return (
                finished - started
            ).total_seconds()

        except (
            TypeError,
            ValueError,
        ):

            return None

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the result into a serializable dictionary.
        """

        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "execution_duration": (
                self.execution_duration()
            ),
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "ToolResult":
        """
        Restore a ToolResult from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Tool result data must be a dictionary."
            )

        return cls(
            tool_name=data.get(
                "tool_name",
                "",
            ),
            success=data.get(
                "success",
                False,
            ),
            result=data.get(
                "result"
            ),
            error=data.get(
                "error"
            ),
            started_at=data.get(
                "started_at"
            ),
            finished_at=data.get(
                "finished_at"
            ),
        )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"ToolResult("
            f"tool_name='{self.tool_name}', "
            f"success={self.success}, "
            f"result={self.result!r}, "
            f"error={self.error!r}"
            f")"
        )