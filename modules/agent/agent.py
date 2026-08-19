"""
Ultron Agent Core
Version: v0.37

Core data model for Ultron AI Agents.

Responsibilities:
- Define an AI agent
- Store agent identity and configuration
- Store executable action
- Store action parameters
- Manage instructions
- Manage tools
- Manage goals
- Manage memory configuration
- Track agent status
- Track enabled/disabled state
- Export agent configuration
- Restore agent configuration
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


class AgentValidationError(Exception):
    """Raised when an agent configuration is invalid."""


class Agent:
    """
    Core representation of an Ultron AI Agent.

    An Agent contains the configuration required to describe
    an AI agent before execution is handled by AgentEngine.

    Backward compatibility:
    - action
    - parameters
    - enabled
    - enable()
    - disable()
    """

    VALID_STATUSES = {
        "draft",
        "active",
        "paused",
        "disabled",
    }

    def __init__(
        self,
        name: str,
        description: str = "",
        action: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        instructions: str = "",
        tools: Optional[List[str]] = None,
        goals: Optional[List[str]] = None,
        memory_enabled: bool = True,
        agent_id: Optional[str] = None,
        status: str = "active",
        enabled: bool = True,
        created_at: Optional[str] = None,
    ) -> None:

        self.id = (
            agent_id
            if agent_id
            else str(uuid.uuid4())
        )

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

        self.action = (
            action.strip()
            if isinstance(action, str)
            else action
        )

        self.parameters = dict(
            parameters or {}
        )

        self.instructions = (
            instructions.strip()
            if isinstance(instructions, str)
            else instructions
        )

        self.tools = list(
            tools or []
        )

        self.goals = list(
            goals or []
        )

        self.memory_enabled = bool(
            memory_enabled
        )

        self.status = status

        self.enabled = bool(
            enabled
        )

        self.created_at = (
            created_at
            if created_at
            else datetime.now().isoformat()
        )

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete agent configuration.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise AgentValidationError(
                "Agent name must be a string."
            )

        if not self.name.strip():
            raise AgentValidationError(
                "Agent name is required."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise AgentValidationError(
                "Agent description must be a string."
            )

        if not isinstance(
            self.action,
            str,
        ):
            raise AgentValidationError(
                "Agent action must be a string."
            )

        if not self.action.strip():
            raise AgentValidationError(
                "Agent action is required."
            )

        if not isinstance(
            self.parameters,
            dict,
        ):
            raise AgentValidationError(
                "Agent parameters must be a dictionary."
            )

        if not isinstance(
            self.instructions,
            str,
        ):
            raise AgentValidationError(
                "Agent instructions must be a string."
            )

        if not isinstance(
            self.tools,
            list,
        ):
            raise AgentValidationError(
                "Agent tools must be a list."
            )

        if not isinstance(
            self.goals,
            list,
        ):
            raise AgentValidationError(
                "Agent goals must be a list."
            )

        if self.status not in self.VALID_STATUSES:
            raise AgentValidationError(
                f"Invalid agent status: {self.status}"
            )

        if not isinstance(
            self.enabled,
            bool,
        ):
            raise AgentValidationError(
                "Agent enabled state must be a boolean."
            )

        return True

    # ========================================================
    # Action Management
    # ========================================================

    def set_action(
        self,
        action: str,
    ) -> None:
        """
        Update the executable action.
        """

        if not isinstance(
            action,
            str,
        ):
            raise AgentValidationError(
                "Agent action must be a string."
            )

        action = action.strip()

        if not action:
            raise AgentValidationError(
                "Agent action is required."
            )

        self.action = action

    def set_parameters(
        self,
        parameters: Optional[Dict[str, Any]],
    ) -> None:
        """
        Replace the agent's action parameters.
        """

        if parameters is None:
            parameters = {}

        if not isinstance(
            parameters,
            dict,
        ):
            raise AgentValidationError(
                "Agent parameters must be a dictionary."
            )

        self.parameters = dict(
            parameters
        )

    # ========================================================
    # Tool Management
    # ========================================================

    def add_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Add a tool to the agent.

        Duplicate tools are ignored.
        """

        if not isinstance(
            tool_name,
            str,
        ):
            raise AgentValidationError(
                "Tool name must be a string."
            )

        tool_name = tool_name.strip()

        if not tool_name:
            raise AgentValidationError(
                "Tool name is required."
            )

        if tool_name in self.tools:
            return False

        self.tools.append(
            tool_name
        )

        return True

    def remove_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Remove a tool from the agent.
        """

        if tool_name not in self.tools:
            return False

        self.tools.remove(
            tool_name
        )

        return True

    # ========================================================
    # Goal Management
    # ========================================================

    def add_goal(
        self,
        goal: str,
    ) -> bool:
        """
        Add a goal to the agent.

        Duplicate goals are ignored.
        """

        if not isinstance(
            goal,
            str,
        ):
            raise AgentValidationError(
                "Goal must be a string."
            )

        goal = goal.strip()

        if not goal:
            raise AgentValidationError(
                "Goal is required."
            )

        if goal in self.goals:
            return False

        self.goals.append(
            goal
        )

        return True

    def remove_goal(
        self,
        goal: str,
    ) -> bool:
        """
        Remove a goal from the agent.
        """

        if goal not in self.goals:
            return False

        self.goals.remove(
            goal
        )

        return True

    # ========================================================
    # Enable / Disable
    # ========================================================

    def enable(self) -> bool:
        """
        Enable the agent.

        Enabled state is independent from the richer
        lifecycle status used by the v0.37 agent model.
        """

        self.enabled = True

        if self.status == "disabled":
            self.status = "active"

        return True

    def disable(self) -> bool:
        """
        Disable the agent.
        """

        self.enabled = False

        if self.status == "active":
            self.status = "disabled"

        return True

    def is_enabled(self) -> bool:
        """
        Return True when the agent is enabled.
        """

        return self.enabled

    # ========================================================
    # Status Management
    # ========================================================

    def activate(self) -> bool:
        """
        Activate the agent.
        """

        self.status = "active"
        self.enabled = True

        return True

    def pause(self) -> bool:
        """
        Pause the agent.
        """

        self.status = "paused"

        return True

    def set_disabled_status(self) -> bool:
        """
        Set the agent lifecycle status to disabled.
        """

        self.status = "disabled"
        self.enabled = False

        return True

    def set_draft(self) -> bool:
        """
        Return the agent to draft state.
        """

        self.status = "draft"

        return True

    def is_active(self) -> bool:
        """
        Return True when the agent is active and enabled.
        """

        return (
            self.status == "active"
            and self.enabled
        )

    # ========================================================
    # Configuration
    # ========================================================

    def update_instructions(
        self,
        instructions: str,
    ) -> None:
        """
        Update the agent's instructions.
        """

        if not isinstance(
            instructions,
            str,
        ):
            raise AgentValidationError(
                "Instructions must be a string."
            )

        self.instructions = (
            instructions.strip()
        )

    def update_description(
        self,
        description: str,
    ) -> None:
        """
        Update the agent description.
        """

        if not isinstance(
            description,
            str,
        ):
            raise AgentValidationError(
                "Description must be a string."
            )

        self.description = (
            description.strip()
        )

    def set_memory(
        self,
        enabled: bool,
    ) -> None:
        """
        Enable or disable agent memory.
        """

        self.memory_enabled = bool(
            enabled
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent into a serializable dictionary.
        """

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "action": self.action,
            "parameters": dict(
                self.parameters
            ),
            "instructions": self.instructions,
            "tools": list(self.tools),
            "goals": list(self.goals),
            "memory_enabled": self.memory_enabled,
            "status": self.status,
            "enabled": self.enabled,
            "created_at": self.created_at,
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Agent":
        """
        Restore an Agent from persistent data.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise AgentValidationError(
                "Agent data must be a dictionary."
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
            action=data.get(
                "action",
                "",
            ),
            parameters=data.get(
                "parameters",
                {},
            ),
            instructions=data.get(
                "instructions",
                "",
            ),
            tools=data.get(
                "tools",
                [],
            ),
            goals=data.get(
                "goals",
                [],
            ),
            memory_enabled=data.get(
                "memory_enabled",
                True,
            ),
            agent_id=data.get(
                "id"
            ),
            status=data.get(
                "status",
                "active",
            ),
            enabled=data.get(
                "enabled",
                True,
            ),
            created_at=data.get(
                "created_at"
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
            f"Agent("
            f"id='{self.id}', "
            f"name='{self.name}', "
            f"action='{self.action}', "
            f"status='{self.status}', "
            f"enabled={self.enabled}"
            f")"
        )