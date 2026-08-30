"""
Ultron Agent Planner
Version: v0.40

Planning engine for Ultron AI Agents.

Responsibilities:
- Create executable agent plans
- Represent individual plan steps
- Validate agent plans
- Add and remove plan steps
- Reorder plan steps
- Track plan state
- Resolve tools for plan steps
- Support sequential agent execution
- Export and restore plans
- Provide a foundation for future AI-powered planning

The planner does NOT execute actions or tools.
Execution belongs to AgentEngine.
"""

from typing import Any, Dict, List, Optional
import uuid

from modules.agent.agent import Agent


class AgentPlanError(Exception):
    """Base exception for agent planning errors."""


class AgentPlanStep:
    """
    Represents a single step inside an AgentPlan.
    """

    VALID_STATUSES = {
        "pending",
        "running",
        "completed",
        "failed",
        "skipped",
    }

    def __init__(
        self,
        action: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        tool_name: Optional[str] = None,
        step_id: Optional[str] = None,
        status: str = "pending",
        result: Any = None,
        error: Optional[str] = None,
    ) -> None:

        self.id = (
            step_id
            if step_id
            else str(uuid.uuid4())
        )

        self.action = (
            action.strip()
            if isinstance(action, str)
            else action
        )

        self.description = (
            description.strip()
            if isinstance(description, str)
            else description
        )

        # Validate before converting so invalid values
        # raise AgentPlanError instead of raw ValueError.
        if parameters is None:
            self.parameters = {}
        elif isinstance(parameters, dict):
            self.parameters = dict(parameters)
        else:
            raise AgentPlanError(
                "Plan step parameters must be a dictionary."
            )

        self.tool_name = (
            tool_name.strip()
            if isinstance(tool_name, str)
            else tool_name
        )

        self.status = status

        self.result = result

        self.error = error

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete plan step.
        """

        if not isinstance(
            self.action,
            str,
        ):
            raise AgentPlanError(
                "Plan step action must be a string."
            )

        if not self.action.strip():
            raise AgentPlanError(
                "Plan step action is required."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise AgentPlanError(
                "Plan step description must be a string."
            )

        if not isinstance(
            self.parameters,
            dict,
        ):
            raise AgentPlanError(
                "Plan step parameters must be a dictionary."
            )

        if self.tool_name is not None:

            if not isinstance(
                self.tool_name,
                str,
            ):
                raise AgentPlanError(
                    "Plan step tool name must be a string or None."
                )

            if not self.tool_name.strip():
                raise AgentPlanError(
                    "Plan step tool name cannot be empty."
                )

        if self.status not in self.VALID_STATUSES:

            raise AgentPlanError(
                f"Invalid plan step status: {self.status}"
            )

        if (
            self.error is not None
            and not isinstance(
                self.error,
                str,
            )
        ):
            raise AgentPlanError(
                "Plan step error must be a string or None."
            )

        return True

    # ========================================================
    # State Management
    # ========================================================

    def start(self) -> bool:
        """
        Mark the step as running.
        """

        if self.status not in {
            "pending",
            "failed",
        }:
            return False

        self.status = "running"

        self.error = None

        return True

    def complete(
        self,
        result: Any = None,
    ) -> bool:
        """
        Mark the step as completed.
        """

        self.status = "completed"

        self.result = result

        self.error = None

        return True

    def fail(
        self,
        error: str,
    ) -> bool:
        """
        Mark the step as failed.
        """

        if not isinstance(
            error,
            str,
        ):
            error = str(error)

        self.status = "failed"

        self.error = error

        return True

    def skip(self) -> bool:
        """
        Mark the step as skipped.
        """

        self.status = "skipped"

        return True

    def reset(self) -> bool:
        """
        Reset the step to pending state.
        """

        self.status = "pending"

        self.result = None

        self.error = None

        return True

    # ========================================================
    # State Queries
    # ========================================================

    def is_pending(self) -> bool:
        return self.status == "pending"

    def is_running(self) -> bool:
        return self.status == "running"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def is_skipped(self) -> bool:
        return self.status == "skipped"

    def is_finished(self) -> bool:
        return self.status in {
            "completed",
            "failed",
            "skipped",
        }

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the plan step into a dictionary.
        """

        return {
            "id": self.id,
            "action": self.action,
            "description": self.description,
            "parameters": dict(
                self.parameters
            ),
            "tool_name": self.tool_name,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "AgentPlanStep":
        """
        Restore a plan step from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise AgentPlanError(
                "Plan step data must be a dictionary."
            )

        return cls(
            action=data.get(
                "action",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            parameters=data.get(
                "parameters",
                {},
            ),
            tool_name=data.get(
                "tool_name"
            ),
            step_id=data.get(
                "id"
            ),
            status=data.get(
                "status",
                "pending",
            ),
            result=data.get(
                "result"
            ),
            error=data.get(
                "error"
            ),
        )

    def __repr__(self) -> str:
        return (
            f"AgentPlanStep("
            f"id='{self.id}', "
            f"action='{self.action}', "
            f"status='{self.status}'"
            f")"
        )


class AgentPlan:
    """
    Represents an executable plan for an Agent.

    A plan contains ordered AgentPlanStep objects.
    The planner creates and manages the plan.
    AgentEngine is responsible for execution.
    """

    VALID_STATUSES = {
        "draft",
        "ready",
        "running",
        "completed",
        "failed",
        "cancelled",
    }

    def __init__(
        self,
        agent: Agent,
        name: str = "",
        description: str = "",
        steps: Optional[List[AgentPlanStep]] = None,
        plan_id: Optional[str] = None,
        status: str = "draft",
    ) -> None:

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentPlanError(
                "AgentPlan requires an Agent instance."
            )

        self.id = (
            plan_id
            if plan_id
            else str(uuid.uuid4())
        )

        self.agent_id = agent.id

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

        self.steps: List[AgentPlanStep] = []

        for step in steps or []:

            if isinstance(
                step,
                AgentPlanStep,
            ):
                self.steps.append(
                    step
                )

            elif isinstance(
                step,
                dict,
            ):
                self.steps.append(
                    AgentPlanStep.from_dict(
                        step
                    )
                )

            else:
                raise AgentPlanError(
                    "Plan steps must contain "
                    "AgentPlanStep objects or dictionaries."
                )

        self.status = status

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete agent plan.
        """

        if not isinstance(
            self.agent_id,
            str,
        ) or not self.agent_id.strip():

            raise AgentPlanError(
                "Plan agent ID is required."
            )

        if not isinstance(
            self.name,
            str,
        ):
            raise AgentPlanError(
                "Plan name must be a string."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise AgentPlanError(
                "Plan description must be a string."
            )

        if not isinstance(
            self.steps,
            list,
        ):
            raise AgentPlanError(
                "Plan steps must be a list."
            )

        for step in self.steps:

            if not isinstance(
                step,
                AgentPlanStep,
            ):
                raise AgentPlanError(
                    "Plan steps must contain "
                    "AgentPlanStep objects."
                )

            step.validate()

        if self.status not in self.VALID_STATUSES:

            raise AgentPlanError(
                f"Invalid plan status: {self.status}"
            )

        return True

    # ========================================================
    # Step Management
    # ========================================================

    def add_step(
        self,
        step: AgentPlanStep,
    ) -> bool:
        """
        Add a step to the end of the plan.
        """

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentPlanError(
                "Only AgentPlanStep objects can be added."
            )

        if any(
            existing.id == step.id
            for existing in self.steps
        ):
            return False

        self.steps.append(
            step
        )

        return True

    def insert_step(
        self,
        index: int,
        step: AgentPlanStep,
    ) -> bool:
        """
        Insert a step at a specific position.
        """

        if not isinstance(
            index,
            int,
        ):
            raise AgentPlanError(
                "Step index must be an integer."
            )

        if not isinstance(
            step,
            AgentPlanStep,
        ):
            raise AgentPlanError(
                "Only AgentPlanStep objects can be inserted."
            )

        if any(
            existing.id == step.id
            for existing in self.steps
        ):
            return False

        if index < 0 or index > len(self.steps):

            raise AgentPlanError(
                "Step index is out of range."
            )

        self.steps.insert(
            index,
            step
        )

        return True

    def remove_step(
        self,
        step_id: str,
    ) -> bool:
        """
        Remove a step by ID.
        """

        for step in self.steps:

            if step.id == step_id:

                self.steps.remove(
                    step
                )

                return True

        return False

    def get_step(
        self,
        step_id: str,
    ) -> Optional[AgentPlanStep]:
        """
        Retrieve a step by ID.
        """

        for step in self.steps:

            if step.id == step_id:

                return step

        return None

    def get_step_by_index(
        self,
        index: int,
    ) -> Optional[AgentPlanStep]:
        """
        Retrieve a step by position.
        """

        if (
            not isinstance(index, int)
            or index < 0
            or index >= len(self.steps)
        ):
            return None

        return self.steps[index]

    def list_steps(self) -> List[AgentPlanStep]:
        """
        Return all plan steps.
        """

        return list(
            self.steps
        )

    def clear_steps(self) -> None:
        """
        Remove all plan steps.
        """

        self.steps.clear()

    def reorder_step(
        self,
        step_id: str,
        new_index: int,
    ) -> bool:
        """
        Move a step to a new position.

        Missing step IDs return False before validating
        the requested destination index.
        """

        # ----------------------------------------------------
        # Step existence must be checked first.
        # ----------------------------------------------------

        step = self.get_step(
            step_id
        )

        if step is None:
            return False

        # ----------------------------------------------------
        # Validate destination index only when the step exists.
        # ----------------------------------------------------

        if not isinstance(
            new_index,
            int,
        ):
            raise AgentPlanError(
                "New step index must be an integer."
            )

        if (
            new_index < 0
            or new_index >= len(self.steps)
        ):
            raise AgentPlanError(
                "New step index is out of range."
            )

        self.steps.remove(
            step
        )

        self.steps.insert(
            new_index,
            step
        )

        return True

    # ========================================================
    # Step Queries
    # ========================================================

    def pending_steps(self) -> List[AgentPlanStep]:
        return [
            step
            for step in self.steps
            if step.is_pending()
        ]

    def completed_steps(self) -> List[AgentPlanStep]:
        return [
            step
            for step in self.steps
            if step.is_completed()
        ]

    def failed_steps(self) -> List[AgentPlanStep]:
        return [
            step
            for step in self.steps
            if step.is_failed()
        ]

    def is_empty(self) -> bool:
        return len(self.steps) == 0

    def is_complete(self) -> bool:
        if self.is_empty():
            return False

        return all(
            step.is_finished()
            for step in self.steps
        )

    def is_finished(self) -> bool:
        """
        Return True when the plan has reached a terminal state.

        Terminal plan states are:
        - completed
        - failed
        - cancelled
        """

        return self.status in {
            "completed",
            "failed",
            "cancelled",
        }

    # ========================================================
    # Lifecycle
    # ========================================================

    def prepare(self) -> bool:
        """
        Mark the plan as ready for execution.
        """

        self.validate()

        if self.is_empty():

            raise AgentPlanError(
                "Cannot prepare an empty plan."
            )

        if self.status not in {
            "draft",
            "failed",
        }:
            return False

        self.status = "ready"

        return True

    def start(self) -> bool:
        """
        Mark the plan as running.
        """

        if self.status != "ready":
            return False

        self.status = "running"

        return True

    def complete(self) -> bool:
        """
        Mark the plan as completed.
        """

        if not self.is_complete():
            return False

        self.status = "completed"

        return True

    def fail(
        self,
    ) -> bool:
        """
        Mark the plan as failed.
        """

        self.status = "failed"

        return True

    def cancel(self) -> bool:
        """
        Cancel the plan.
        """

        self.status = "cancelled"

        return True

    def reset(self) -> bool:
        """
        Reset plan and all steps.
        """

        for step in self.steps:
            step.reset()

        self.status = "draft"

        return True

    # ========================================================
    # Status Queries
    # ========================================================

    def is_draft(self) -> bool:
        return self.status == "draft"

    def is_ready(self) -> bool:
        return self.status == "ready"

    def is_running(self) -> bool:
        return self.status == "running"

    def is_completed(self) -> bool:
        return self.status == "completed"

    def is_failed(self) -> bool:
        return self.status == "failed"

    def is_cancelled(self) -> bool:
        return self.status == "cancelled"

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the complete plan into a dictionary.
        """

        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "steps": [
                step.to_dict()
                for step in self.steps
            ],
            "status": self.status,
        }

    @classmethod
    def from_dict(
        cls,
        agent: Agent,
        data: Dict[str, Any],
    ) -> "AgentPlan":
        """
        Restore an AgentPlan from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise AgentPlanError(
                "Plan data must be a dictionary."
            )

        if data.get(
            "agent_id"
        ) not in {
            None,
            agent.id,
        }:
            raise AgentPlanError(
                "Plan agent ID does not match the supplied agent."
            )

        return cls(
            agent=agent,
            name=data.get(
                "name",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            steps=data.get(
                "steps",
                [],
            ),
            plan_id=data.get(
                "id"
            ),
            status=data.get(
                "status",
                "draft",
            ),
        )

    # ========================================================
    # Representation
    # ========================================================

    def __len__(self) -> int:
        return len(
            self.steps
        )

    def __repr__(self) -> str:
        return (
            f"AgentPlan("
            f"id='{self.id}', "
            f"agent_id='{self.agent_id}', "
            f"steps={len(self.steps)}, "
            f"status='{self.status}'"
            f")"
        )


class AgentPlanner:
    """
    Planning service for Ultron Agents.

    AgentPlanner creates deterministic execution plans.
    It does not execute actions or tools.
    """

    def __init__(self) -> None:
        pass

    # ========================================================
    # Plan Creation
    # ========================================================

    def create_plan(
        self,
        agent: Agent,
        name: str = "",
        description: str = "",
    ) -> AgentPlan:
        """
        Create an empty plan for an agent.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentPlanError(
                "Only Agent instances can have plans."
            )

        return AgentPlan(
            agent=agent,
            name=name,
            description=description,
        )

    # ========================================================
    # Step Creation
    # ========================================================

    def create_step(
        self,
        action: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        tool_name: Optional[str] = None,
    ) -> AgentPlanStep:
        """
        Create a new plan step.
        """

        return AgentPlanStep(
            action=action,
            description=description,
            parameters=parameters,
            tool_name=tool_name,
        )

    # ========================================================
    # Add Step
    # ========================================================

    def add_step(
        self,
        plan: AgentPlan,
        step: AgentPlanStep,
    ) -> bool:
        """
        Add a step to an existing plan.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentPlanError(
                "Only AgentPlan objects can be modified."
            )

        return plan.add_step(
            step
        )

    # ========================================================
    # Plan Validation
    # ========================================================

    def validate_plan(
        self,
        plan: AgentPlan,
        agent: Optional[Agent] = None,
    ) -> bool:
        """
        Validate a plan.

        If an agent is supplied, its ID must match
        the plan's agent ID.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentPlanError(
                "Only AgentPlan objects can be validated."
            )

        plan.validate()

        if agent is not None:

            if not isinstance(
                agent,
                Agent,
            ):
                raise AgentPlanError(
                    "Agent must be an Agent instance."
                )

            if plan.agent_id != agent.id:
                raise AgentPlanError(
                    "Plan does not belong to the supplied agent."
                )

        return True

    # ========================================================
    # Prepare Plan
    # ========================================================

    def prepare_plan(
        self,
        plan: AgentPlan,
    ) -> bool:
        """
        Validate and prepare a plan for execution.
        """

        self.validate_plan(
            plan
        )

        return plan.prepare()

    # ========================================================
    # Next Step
    # ========================================================

    def get_next_step(
        self,
        plan: AgentPlan,
    ) -> Optional[AgentPlanStep]:
        """
        Return the next pending step.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentPlanError(
                "Only AgentPlan objects can be inspected."
            )

        for step in plan.steps:

            if step.is_pending():
                return step

        return None

    # ========================================================
    # Plan Progress
    # ========================================================

    def get_progress(
        self,
        plan: AgentPlan,
    ) -> Dict[str, Any]:
        """
        Return deterministic plan progress information.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentPlanError(
                "Only AgentPlan objects are supported."
            )

        total = len(
            plan.steps
        )

        completed = len(
            plan.completed_steps()
        )

        failed = len(
            plan.failed_steps()
        )

        pending = len(
            plan.pending_steps()
        )

        skipped = sum(
            1
            for step in plan.steps
            if step.is_skipped()
        )

        percentage = (
            0.0
            if total == 0
            else (
                completed
                + skipped
            )
            / total
            * 100
        )

        return {
            "plan_id": plan.id,
            "agent_id": plan.agent_id,
            "status": plan.status,
            "total_steps": total,
            "completed_steps": completed,
            "failed_steps": failed,
            "pending_steps": pending,
            "skipped_steps": skipped,
            "progress_percent": percentage,
        }

    # ========================================================
    # Reset
    # ========================================================

    def reset_plan(
        self,
        plan: AgentPlan,
    ) -> bool:
        """
        Reset an existing plan.
        """

        if not isinstance(
            plan,
            AgentPlan,
        ):
            raise AgentPlanError(
                "Only AgentPlan objects can be reset."
            )

        return plan.reset()

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return "AgentPlanner()"
