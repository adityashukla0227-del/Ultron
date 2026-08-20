"""
Ultron Agent Tool
Version: v0.38

Represents a tool that can be assigned to an Ultron Agent.

Responsibilities:
- Store tool identity
- Store tool description
- Store tool configuration
- Track enabled/disabled state
- Store executable handler
- Execute tools safely
- Merge tool configuration with runtime parameters
- Return standardized ToolResult objects
- Serialize tool configuration
- Restore tool configuration
"""

from datetime import datetime
from typing import Any, Callable, Dict, Optional

from modules.agent.tool_result import ToolResult


class AgentTool:
    """
    Represents a tool available to an Ultron Agent.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None,
        handler: Optional[Callable[..., Any]] = None,
    ) -> None:

        self.name = (
            name.strip()
            if isinstance(name, str)
            else name
        )

        self.description = (
            description.strip()
            if isinstance(description, str)
            else description
        )

        self.enabled = bool(
            enabled
        )

        self.config = dict(
            config or {}
        )

        self.handler = handler

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete tool configuration.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise ValueError(
                "Tool name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Tool name is required."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise ValueError(
                "Tool description must be a string."
            )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise ValueError(
                "Tool enabled state must be a boolean."
            )

        if not isinstance(
            self.config,
            dict,
        ):
            raise ValueError(
                "Tool config must be a dictionary."
            )

        if (
            self.handler is not None
            and not callable(
                self.handler
            )
        ):
            raise ValueError(
                "Tool handler must be callable."
            )

        return True

    # ========================================================
    # Configuration Management
    # ========================================================

    def set_config(
        self,
        config: Optional[Dict[str, Any]],
    ) -> None:
        """
        Replace the complete tool configuration.
        """

        if config is None:
            config = {}

        if not isinstance(
            config,
            dict,
        ):
            raise ValueError(
                "Tool config must be a dictionary."
            )

        self.config = dict(
            config
        )

    def update_config(
        self,
        **config,
    ) -> None:
        """
        Update selected configuration values.
        """

        self.config.update(
            config
        )

    def get_config(
        self,
        key: Optional[str] = None,
        default: Any = None,
    ) -> Any:
        """
        Get a configuration value.

        If key is None, return the complete
        configuration dictionary.
        """

        if key is None:
            return dict(
                self.config
            )

        return self.config.get(
            key,
            default,
        )

    # ========================================================
    # Handler Management
    # ========================================================

    def set_handler(
        self,
        handler: Callable[..., Any],
    ) -> None:
        """
        Assign an executable handler to the tool.
        """

        if not callable(
            handler
        ):
            raise ValueError(
                "Tool handler must be callable."
            )

        self.handler = handler

    def has_handler(self) -> bool:
        """
        Return True when a handler is assigned.
        """

        return (
            self.handler is not None
        )

    # ========================================================
    # Execution
    # ========================================================

    def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        """
        Execute the tool handler.

        Returns:
            ToolResult containing success/failure,
            result, error and execution timing.

        Tool configuration is merged with runtime
        parameters.

        Runtime parameters take priority over
        stored configuration.
        """

        started_at = datetime.now()

        # ----------------------------------------------------
        # Disabled Tool
        # ----------------------------------------------------

        if not self.enabled:

            finished_at = datetime.now()

            return ToolResult(
                tool_name=self.name,
                success=False,
                result=None,
                error=(
                    f"Tool '{self.name}' is disabled."
                ),
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
            )

        # ----------------------------------------------------
        # Missing Handler
        # ----------------------------------------------------

        if self.handler is None:

            finished_at = datetime.now()

            return ToolResult(
                tool_name=self.name,
                success=False,
                result=None,
                error=(
                    f"Tool '{self.name}' has no handler."
                ),
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
            )

        # ----------------------------------------------------
        # Merge Configuration + Runtime Parameters
        # ----------------------------------------------------

        parameters = dict(
            self.config
        )

        parameters.update(
            kwargs
        )

        # ----------------------------------------------------
        # Execute Handler
        # ----------------------------------------------------

        try:

            result = self.handler(
                **parameters
            )

            finished_at = datetime.now()

            return ToolResult(
                tool_name=self.name,
                success=True,
                result=result,
                error=None,
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
            )

        except Exception as exc:

            finished_at = datetime.now()

            return ToolResult(
                tool_name=self.name,
                success=False,
                result=None,
                error=str(exc),
                started_at=started_at.isoformat(),
                finished_at=finished_at.isoformat(),
            )

    # ========================================================
    # Enable / Disable
    # ========================================================

    def enable(self) -> bool:
        """
        Enable the tool.
        """

        self.enabled = True

        return True

    def disable(self) -> bool:
        """
        Disable the tool.
        """

        self.enabled = False

        return True

    def is_enabled(self) -> bool:
        """
        Return whether the tool is enabled.
        """

        return self.enabled

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool into a serializable dictionary.

        The executable handler is intentionally not
        serialized.
        """

        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "config": dict(
                self.config
            ),
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AgentTool":
        """
        Restore an AgentTool from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise ValueError(
                "Tool data must be a dictionary."
            )

        return cls(
            name=data.get(
                "name",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            enabled=data.get(
                "enabled",
                True,
            ),
            config=data.get(
                "config",
                {},
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
            f"AgentTool("
            f"name='{self.name}', "
            f"enabled={self.enabled}, "
            f"has_handler={self.has_handler()}"
            f")"
        )