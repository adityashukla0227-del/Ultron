"""
Ultron Agent Plan
Version: v0.40

Execution plan model for Ultron AI Agents.

Responsibilities:
- Store execution plan identity
- Store agent identity
- Store user query
- Store planned execution steps
- Store selected tools
- Track plan status
- Track creation timestamp
- Validate execution plans
- Serialize plan configuration
- Restore plan configuration

The AgentPlan does NOT execute tools.
Execution belongs to AgentEngine.
Planning logic belongs to AgentPlanner.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


class AgentPlanValidationError(Exception):
    """Raised when an agent execution plan is invalid."""


class AgentPlan:
    """
    Represents a planned execution for an Ultron Agent.

    AgentPlan is a data model only.

    It describes:
    - Which agent is planning
    - What the user requested
    - Which tools may be required
    - Which execution steps should be performed
    - Current planning/execution state
    """

    VALID_STATUSES = {
        "draft",
        "planned",
        "executing",
        "completed",
        "failed",
        "cancelled",
    }

    def __init__(
        self,
        agent_id: str,
        query: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        selected_tools: Optional[List[str]] = None,
        plan_id: Optional[str] = None,
        status: str = "draft",
        created_at: Optional[str] = None,
    ) -> None:

        self.id = (
            plan_id
            if plan_id
            else str(uuid.uuid4())
        )

        self.agent_id = (
            agent_id.strip()
            if isinstance(agent_id, str)
            else agent_id
        )

        self.query = (
            query.strip()
            if isinstance(query, str)
            else query
        )

        self.steps: List[Dict[str, Any]] = []

        for step in steps or []:
            if not isinstance(step, dict):
                raise AgentPlanValidationError(
                    "Plan steps must contain dictionaries."
                )

            self.steps.append(
                dict(step)
            )

        self.selected_tools = list(
            selected_tools or []
        )

        self.status = status

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
        Validate the complete execution plan.
        """

        if not isinstance(
            self.id,
            str,
        ) or not self.id.strip():

            raise AgentPlanValidationError(
                "Plan ID is required."
            )

        if not isinstance(
            self.agent_id,
            str,
        ) or not self.agent_id.strip():

            raise AgentPlanValidationError(
                "Agent ID is required."
            )

        if not isinstance(
            self.query,
            str,
        ) or not self.query.strip():

            raise AgentPlanValidationError(
                "Plan query is required."
            )

        if not isinstance(
            self.steps,
            list,
        ):

            raise AgentPlanValidationError(
                "Plan steps must be a list."
            )

        for step in self.steps:

            if not isinstance(
                step,
                dict,
            ):

                raise AgentPlanValidationError(
                    "Each plan step must be a dictionary."
                )

        if not isinstance(
            self.selected_tools,
            list,
        ):

            raise AgentPlanValidationError(
                "Selected tools must be a list."
            )

        for tool_name in self.selected_tools:

            if not isinstance(
                tool_name,
                str,
            ) or not tool_name.strip():

                raise AgentPlanValidationError(
                    "Selected tool names must be "
                    "non-empty strings."
                )

        if self.status not in self.VALID_STATUSES:

            raise AgentPlanValidationError(
                f"Invalid plan status: {self.status}"
            )

        if not isinstance(
            self.created_at,
            str,
        ) or not self.created_at.strip():

            raise AgentPlanValidationError(
                "Plan creation timestamp is required."
            )

        return True

    # ========================================================
    # Step Management
    # ========================================================

    def add_step(
        self,
        step: Dict[str, Any],
    ) -> bool:
        """
        Add an execution step to the plan.

        Duplicate dictionaries are ignored.
        """

        if not isinstance(
            step,
            dict,
        ):

            raise AgentPlanValidationError(
                "Plan step must be a dictionary."
            )

        normalized_step = dict(
            step
        )

        if normalized_step in self.steps:
            return False

        self.steps.append(
            normalized_step
        )

        return True

    def remove_step(
        self,
        index: int,
    ) -> bool:
        """
        Remove an execution step by index.
        """

        if not isinstance(
            index,
            int,
        ):

            raise AgentPlanValidationError(
                "Step index must be an integer."
            )

        if index < 0 or index >= len(self.steps):
            return False

        self.steps.pop(
            index
        )

        return True

    def get_step(
        self,
        index: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Return an execution step by index.
        """

        if not isinstance(
            index,
            int,
        ):

            return None

        if index < 0 or index >= len(self.steps):
            return None

        return dict(
            self.steps[index]
        )

    def get_steps(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return a copy of all execution steps.
        """

        return [
            dict(step)
            for step in self.steps
        ]

    # ========================================================
    # Tool Management
    # ========================================================

    def add_selected_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Add a selected tool to the execution plan.

        Duplicate tool names are ignored.
        """

        if not isinstance(
            tool_name,
            str,
        ):

            raise AgentPlanValidationError(
                "Tool name must be a string."
            )

        tool_name = tool_name.strip()

        if not tool_name:

            raise AgentPlanValidationError(
                "Tool name is required."
            )

        if tool_name in self.selected_tools:
            return False

        self.selected_tools.append(
            tool_name
        )

        return True

    def remove_selected_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Remove a selected tool from the plan.
        """

        if not isinstance(
            tool_name,
            str,
        ):

            raise AgentPlanValidationError(
                "Tool name must be a string."
            )

        tool_name = tool_name.strip()

        if tool_name not in self.selected_tools:
            return False

        self.selected_tools.remove(
            tool_name
        )

        return True

    def has_selected_tool(
        self,
        tool_name: str,
    ) -> bool:
        """
        Check whether a tool is selected.
        """

        if not isinstance(
            tool_name,
            str,
        ):

            return False

        return (
            tool_name.strip()
            in self.selected_tools
        )

    def get_selected_tools(
        self,
    ) -> List[str]:
        """
        Return all selected tool names.
        """

        return list(
            self.selected_tools
        )

    # ========================================================
    # Status Management
    # ========================================================

    def set_status(
        self,
        status: str,
    ) -> None:
        """
        Update the plan status.
        """

        if not isinstance(
            status,
            str,
        ):

            raise AgentPlanValidationError(
                "Plan status must be a string."
            )

        status = status.strip().lower()

        if status not in self.VALID_STATUSES:

            raise AgentPlanValidationError(
                f"Invalid plan status: {status}"
            )

        self.status = status

    def mark_planned(self) -> bool:
        """
        Mark the plan as ready for execution.
        """

        self.status = "planned"

        return True

    def mark_executing(self) -> bool:
        """
        Mark the plan as currently executing.
        """

        self.status = "executing"

        return True

    def mark_completed(self) -> bool:
        """
        Mark the plan as successfully completed.
        """

        self.status = "completed"

        return True

    def mark_failed(self) -> bool:
        """
        Mark the plan as failed.
        """

        self.status = "failed"

        return True

    def cancel(self) -> bool:
        """
        Cancel the execution plan.
        """

        self.status = "cancelled"

        return True

    def is_ready(self) -> bool:
        """
        Return True when the plan is ready for execution.
        """

        return self.status == "planned"

    def is_finished(self) -> bool:
        """
        Return True when the plan reached a terminal state.
        """

        return self.status in {
            "completed",
            "failed",
            "cancelled",
        }

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the execution plan into a serializable dictionary.
        """

        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "query": self.query,
            "steps": [
                dict(step)
                for step in self.steps
            ],
            "selected_tools": list(
                self.selected_tools
            ),
            "status": self.status,
            "created_at": self.created_at,
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AgentPlan":
        """
        Restore an AgentPlan from persistent data.
        """

        if not isinstance(
            data,
            dict,
        ):

            raise AgentPlanValidationError(
                "Plan data must be a dictionary."
            )

        return cls(
            agent_id=data.get(
                "agent_id",
                "",
            ),
            query=data.get(
                "query",
                "",
            ),
            steps=data.get(
                "steps",
                [],
            ),
            selected_tools=data.get(
                "selected_tools",
                [],
            ),
            plan_id=data.get(
                "id"
            ),
            status=data.get(
                "status",
                "draft",
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
            f"AgentPlan("
            f"id='{self.id}', "
            f"agent_id='{self.agent_id}', "
            f"status='{self.status}', "
            f"steps={len(self.steps)}, "
            f"tools={self.selected_tools}"
            f")"
        )