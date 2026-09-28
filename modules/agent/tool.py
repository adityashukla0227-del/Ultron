"""
Ultron Agent Tool
Version: v0.91

Represents a tool that can be assigned to an Ultron Agent.

Responsibilities:
- Store tool identity
- Store tool description
- Store tool configuration
- Track enabled/disabled state
- Store executable handler
- Store tool version
- Store tool capabilities
- Store extensibility metadata
- Execute tools safely
- Merge tool configuration with runtime parameters
- Return standardized ToolResult objects
- Serialize tool configuration
- Restore tool configuration
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from modules.agent.tool_result import ToolResult


class AgentTool:
    """
    Represents a tool available to an Ultron Agent.

    v0.91 adds an extensibility metadata layer without
    changing the existing tool execution and serialization
    contracts.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        enabled: bool = True,
        config: Optional[Dict[str, Any]] = None,
        handler: Optional[Callable[..., Any]] = None,
        version: str = "1.0",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
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

        self.version = version

        if capabilities is None:
            self.capabilities = []
        elif not isinstance(capabilities, list):
            raise ValueError(
                "Tool capabilities must be a list."
            )
        else:
            self.capabilities = list(
                capabilities
            )

        self.metadata = dict(
            metadata or {}
        )

        self.validate()

    # Validation
    def validate(self) -> bool:

        if not isinstance(self.name, str):
            raise ValueError(
                "Tool name must be a string."
            )

        if not self.name.strip():
            raise ValueError(
                "Tool name is required."
            )

        if not isinstance(self.description, str):
            raise ValueError(
                "Tool description must be a string."
            )

        if not isinstance(self.enabled, bool):
            raise ValueError(
                "Tool enabled state must be a boolean."
            )

        if not isinstance(self.config, dict):
            raise ValueError(
                "Tool config must be a dictionary."
            )

        if self.handler is not None and not callable(
            self.handler
        ):
            raise ValueError(
                "Tool handler must be callable."
            )

        if not isinstance(self.version, str):
            raise ValueError(
                "Tool version must be a string."
            )

        if not self.version.strip():
            raise ValueError(
                "Tool version is required."
            )

        if not isinstance(self.capabilities, list):
            raise ValueError(
                "Tool capabilities must be a list."
            )

        for capability in self.capabilities:
            if not isinstance(capability, str):
                raise ValueError(
                    "Tool capabilities must contain strings."
                )

        if not isinstance(self.metadata, dict):
            raise ValueError(
                "Tool metadata must be a dictionary."
            )

        return True

    # Configuration
    def set_config(
        self,
        config: Optional[Dict[str, Any]],
    ) -> None:

        if config is None:
            config = {}

        if not isinstance(config, dict):
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

        self.config.update(
            config
        )

    def get_config(
        self,
        key: Optional[str] = None,
        default: Any = None,
    ) -> Any:

        if key is None:
            return dict(
                self.config
            )

        return self.config.get(
            key,
            default,
        )

    # Extensibility Metadata
    def set_version(
        self,
        version: str,
    ) -> None:

        if not isinstance(version, str):
            raise ValueError(
                "Tool version must be a string."
            )

        version = version.strip()

        if not version:
            raise ValueError(
                "Tool version is required."
            )

        self.version = version

    def get_version(self) -> str:

        return self.version

    def set_capabilities(
        self,
        capabilities: Optional[List[str]],
    ) -> None:

        if capabilities is None:
            capabilities = []

        if not isinstance(capabilities, list):
            raise ValueError(
                "Tool capabilities must be a list."
            )

        for capability in capabilities:
            if not isinstance(capability, str):
                raise ValueError(
                    "Tool capabilities must contain strings."
                )

        self.capabilities = list(
            capabilities
        )

    def add_capability(
        self,
        capability: str,
    ) -> bool:

        if not isinstance(capability, str):
            raise ValueError(
                "Tool capability must be a string."
            )

        capability = capability.strip()

        if not capability:
            raise ValueError(
                "Tool capability is required."
            )

        if capability in self.capabilities:
            return False

        self.capabilities.append(
            capability
        )

        return True

    def remove_capability(
        self,
        capability: str,
    ) -> bool:

        if not isinstance(capability, str):
            return False

        capability = capability.strip()

        if capability not in self.capabilities:
            return False

        self.capabilities.remove(
            capability
        )

        return True

    def get_capabilities(self) -> List[str]:

        return list(
            self.capabilities
        )

    def set_metadata(
        self,
        metadata: Optional[Dict[str, Any]],
    ) -> None:

        if metadata is None:
            metadata = {}

        if not isinstance(metadata, dict):
            raise ValueError(
                "Tool metadata must be a dictionary."
            )

        self.metadata = dict(
            metadata
        )

    def update_metadata(
        self,
        **metadata,
    ) -> None:

        self.metadata.update(
            metadata
        )

    def get_metadata(
        self,
        key: Optional[str] = None,
        default: Any = None,
    ) -> Any:

        if key is None:
            return dict(
                self.metadata
            )

        return self.metadata.get(
            key,
            default,
        )

    # Handler
    def set_handler(
        self,
        handler: Callable[..., Any],
    ) -> None:

        if not callable(handler):
            raise ValueError(
                "Tool handler must be callable."
            )

        self.handler = handler

    def has_handler(self) -> bool:

        return self.handler is not None

    # Execution
    def execute(
        self,
        **kwargs,
    ) -> ToolResult:

        started_at = datetime.now()

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

        parameters = dict(
            self.config
        )

        parameters.update(
            kwargs
        )

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

    # Enable / Disable
    def enable(self) -> bool:

        self.enabled = True

        return True

    def disable(self) -> bool:

        self.enabled = False

        return True

    def is_enabled(self) -> bool:

        return self.enabled

    # Serialization
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool into a serializable dictionary.

        The executable handler and extensibility metadata are
        intentionally not serialized in the existing tool
        serialization contract.
        """

        return {
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "config": dict(
                self.config
            ),
        }

    # Restoration
    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AgentTool":

        if not isinstance(data, dict):
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
            version=data.get(
                "version",
                "1.0",
            ),
            capabilities=data.get(
                "capabilities",
                [],
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    def __repr__(self) -> str:

        return (
            f"AgentTool("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"enabled={self.enabled}, "
            f"capabilities={self.capabilities}, "
            f"has_handler={self.has_handler()}"
            f")"
        )
