"""
Ultron Agent Runtime Context
Version: v0.49

Runtime context shared across the Ultron agent execution lifecycle.

Responsibilities:
- Hold the active Agent
- Hold the current user query
- Hold session information
- Hold memory/context information
- Hold the current AgentPlan
- Hold runtime execution state
- Hold permission information
- Hold execution metadata
- Provide controlled runtime state updates
- Support serialization and restoration

Design principles:
- Agent configuration remains inside Agent.
- Execution logic remains inside runtime/execution layers.
- RuntimeContext only represents the state and context of one execution.
- No tool execution is performed here.
- No planning is performed here.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from modules.agent.agent import Agent


class AgentRuntimeContextError(Exception):
    """Raised when an agent runtime context is invalid."""


class AgentRuntimeContext:
    """
    Runtime context for a single Ultron agent execution.

    The context acts as a shared state container between:

        Agent
            ↓
        Planner
            ↓
        Orchestrator
            ↓
        Execution Controller
            ↓
        Tools / Capabilities

    It intentionally does not perform execution itself.
    """

    VALID_STATUSES = {
        "created",
        "ready",
        "planning",
        "planned",
        "executing",
        "waiting",
        "resuming",
        "completed",
        "failed",
        "cancelled",
    }

    def __init__(
        self,
        agent: Agent,
        query: str = "",
        session: Optional[Dict[str, Any]] = None,
        memory: Optional[Dict[str, Any]] = None,
        plan: Any = None,
        state: Optional[Dict[str, Any]] = None,
        permissions: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution: Optional[Dict[str, Any]] = None,
        context_id: Optional[str] = None,
        status: str = "created",
        created_at: Optional[str] = None,
    ) -> None:

        if not isinstance(agent, Agent):
            raise AgentRuntimeContextError(
                "Runtime context requires a valid Agent instance."
            )

        self.id = (
            context_id
            if context_id
            else self._generate_context_id()
        )

        self.agent = agent

        self.query = (
            query.strip()
            if isinstance(query, str)
            else query
        )

        self.session = dict(
            session or {}
        )

        self.memory = dict(
            memory or {}
        )

        self.plan = plan

        self.state = dict(
            state or {}
        )

        self.permissions = dict(
            permissions or {}
        )

        self.metadata = dict(
            metadata or {}
        )

        self.execution = dict(
            execution or {}
        )

        self.status = status

        self.created_at = (
            created_at
            if created_at
            else datetime.now().isoformat()
        )

        self.validate()

    # ========================================================
    # Identity
    # ========================================================

    @staticmethod
    def _generate_context_id() -> str:
        """
        Generate a unique runtime context identifier.
        """

        from uuid import uuid4

        return str(uuid4())

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the runtime context.
        """

        if not isinstance(
            self.agent,
            Agent,
        ):
            raise AgentRuntimeContextError(
                "Context agent must be an Agent instance."
            )

        if not isinstance(
            self.query,
            str,
        ):
            raise AgentRuntimeContextError(
                "Context query must be a string."
            )

        if not isinstance(
            self.session,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context session must be a dictionary."
            )

        if not isinstance(
            self.memory,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context memory must be a dictionary."
            )

        if not isinstance(
            self.state,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context state must be a dictionary."
            )

        if not isinstance(
            self.permissions,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context permissions must be a dictionary."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context metadata must be a dictionary."
            )

        if not isinstance(
            self.execution,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Context execution must be a dictionary."
            )

        if self.status not in self.VALID_STATUSES:
            raise AgentRuntimeContextError(
                f"Invalid runtime context status: "
                f"{self.status}"
            )

        if not isinstance(
            self.created_at,
            str,
        ):
            raise AgentRuntimeContextError(
                "Context created_at must be a string."
            )

        return True

    # ========================================================
    # Query
    # ========================================================

    def set_query(
        self,
        query: str,
    ) -> None:
        """
        Update the current user query.
        """

        if not isinstance(
            query,
            str,
        ):
            raise AgentRuntimeContextError(
                "Query must be a string."
            )

        self.query = query.strip()

    def get_query(self) -> str:
        """
        Return the current user query.
        """

        return self.query

    # ========================================================
    # Session
    # ========================================================

    def set_session_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store a value inside session context.
        """

        self._validate_key(
            key,
            "Session key",
        )

        self.session[key] = value

    def get_session_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a session value.
        """

        self._validate_key(
            key,
            "Session key",
        )

        return self.session.get(
            key,
            default,
        )

    def remove_session_value(
        self,
        key: str,
    ) -> bool:
        """
        Remove a session value.
        """

        self._validate_key(
            key,
            "Session key",
        )

        if key not in self.session:
            return False

        del self.session[key]

        return True

    # ========================================================
    # Memory
    # ========================================================

    def set_memory_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store runtime memory/context data.
        """

        self._validate_key(
            key,
            "Memory key",
        )

        self.memory[key] = value

    def get_memory_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve runtime memory/context data.
        """

        self._validate_key(
            key,
            "Memory key",
        )

        return self.memory.get(
            key,
            default,
        )

    def remove_memory_value(
        self,
        key: str,
    ) -> bool:
        """
        Remove runtime memory/context data.
        """

        self._validate_key(
            key,
            "Memory key",
        )

        if key not in self.memory:
            return False

        del self.memory[key]

        return True

    # ========================================================
    # State
    # ========================================================

    def set_state(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store execution state.
        """

        self._validate_key(
            key,
            "State key",
        )

        self.state[key] = value

    def get_state(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve execution state.
        """

        self._validate_key(
            key,
            "State key",
        )

        return self.state.get(
            key,
            default,
        )

    def remove_state(
        self,
        key: str,
    ) -> bool:
        """
        Remove execution state.
        """

        self._validate_key(
            key,
            "State key",
        )

        if key not in self.state:
            return False

        del self.state[key]

        return True

    # ========================================================
    # Permissions
    # ========================================================

    def set_permission(
        self,
        capability: str,
        value: Any,
    ) -> None:
        """
        Define a runtime permission.
        """

        self._validate_key(
            capability,
            "Permission key",
        )

        self.permissions[capability] = value

    def get_permission(
        self,
        capability: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve a runtime permission.
        """

        self._validate_key(
            capability,
            "Permission key",
        )

        return self.permissions.get(
            capability,
            default,
        )

    def has_permission(
        self,
        capability: str,
    ) -> bool:
        """
        Check whether a permission is explicitly enabled.
        """

        self._validate_key(
            capability,
            "Permission key",
        )

        return bool(
            self.permissions.get(
                capability,
                False,
            )
        )

    # ========================================================
    # Metadata
    # ========================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store execution metadata.
        """

        self._validate_key(
            key,
            "Metadata key",
        )

        self.metadata[key] = value

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve execution metadata.
        """

        self._validate_key(
            key,
            "Metadata key",
        )

        return self.metadata.get(
            key,
            default,
        )

    # ========================================================
    # Execution Data
    # ========================================================

    def set_execution_value(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store execution-specific data.
        """

        self._validate_key(
            key,
            "Execution key",
        )

        self.execution[key] = value

    def get_execution_value(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Retrieve execution-specific data.
        """

        self._validate_key(
            key,
            "Execution key",
        )

        return self.execution.get(
            key,
            default,
        )

    # ========================================================
    # Plan
    # ========================================================

    def set_plan(
        self,
        plan: Any,
    ) -> None:
        """
        Attach an execution plan to the context.
        """

        self.plan = plan

    def get_plan(self) -> Any:
        """
        Return the current execution plan.
        """

        return self.plan

    # ========================================================
    # Status
    # ========================================================

    def set_status(
        self,
        status: str,
    ) -> None:
        """
        Update runtime lifecycle status.
        """

        if not isinstance(
            status,
            str,
        ):
            raise AgentRuntimeContextError(
                "Runtime status must be a string."
            )

        status = status.strip().lower()

        if status not in self.VALID_STATUSES:
            raise AgentRuntimeContextError(
                f"Invalid runtime context status: "
                f"{status}"
            )

        self.status = status

    def is_terminal(self) -> bool:
        """
        Return True when execution reached a terminal state.
        """

        return self.status in {
            "completed",
            "failed",
            "cancelled",
        }

    # ========================================================
    # Helpers
    # ========================================================

    @staticmethod
    def _validate_key(
        key: str,
        label: str,
    ) -> None:
        """
        Validate dictionary keys used by runtime context.
        """

        if not isinstance(
            key,
            str,
        ):
            raise AgentRuntimeContextError(
                f"{label} must be a string."
            )

        if not key.strip():
            raise AgentRuntimeContextError(
                f"{label} cannot be empty."
            )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the runtime context.

        Agent and plan objects are serialized when they
        provide a to_dict() method.
        """

        if hasattr(
            self.agent,
            "to_dict",
        ):
            agent_data = self.agent.to_dict()
        else:
            agent_data = self.agent

        if self.plan is not None and hasattr(
            self.plan,
            "to_dict",
        ):
            plan_data = self.plan.to_dict()
        else:
            plan_data = self.plan

        return {
            "id": self.id,
            "agent": agent_data,
            "query": self.query,
            "session": dict(self.session),
            "memory": dict(self.memory),
            "plan": plan_data,
            "state": dict(self.state),
            "permissions": dict(self.permissions),
            "metadata": dict(self.metadata),
            "execution": dict(self.execution),
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
    ) -> "AgentRuntimeContext":
        """
        Restore a runtime context from serialized data.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise AgentRuntimeContextError(
                "Runtime context data must be a dictionary."
            )

        agent_data = data.get(
            "agent"
        )

        if isinstance(
            agent_data,
            dict,
        ):
            agent = Agent.from_dict(
                agent_data
            )

        elif isinstance(
            agent_data,
            Agent,
        ):
            agent = agent_data

        else:
            raise AgentRuntimeContextError(
                "Runtime context contains invalid agent data."
            )

        return cls(
            agent=agent,
            query=data.get(
                "query",
                "",
            ),
            session=data.get(
                "session",
                {},
            ),
            memory=data.get(
                "memory",
                {},
            ),
            plan=data.get(
                "plan"
            ),
            state=data.get(
                "state",
                {},
            ),
            permissions=data.get(
                "permissions",
                {},
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
            execution=data.get(
                "execution",
                {},
            ),
            context_id=data.get(
                "id"
            ),
            status=data.get(
                "status",
                "created",
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
            f"AgentRuntimeContext("
            f"id='{self.id}', "
            f"agent='{self.agent.name}', "
            f"status='{self.status}', "
            f"query='{self.query}'"
            f")"
        )