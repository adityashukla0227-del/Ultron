"""
Ultron Agent Registry
Version: v0.37

Central registry for managing Ultron AI Agents.

Responsibilities:
- Register agents
- Retrieve agents
- List agents
- Update agents
- Delete agents
- Restore agents from dictionaries
- Prevent duplicate agent IDs
- Support backward-compatible list/remove APIs
"""

from typing import Dict, List, Optional

from modules.agent.agent import (
    Agent,
    AgentValidationError,
)


class AgentRegistryError(Exception):
    """Base exception for agent registry errors."""


class AgentAlreadyExistsError(AgentRegistryError):
    """Raised when an agent already exists."""


class AgentNotFoundError(AgentRegistryError):
    """Raised when an agent cannot be found."""


class AgentRegistry:
    """
    Central in-memory registry for Ultron agents.

    The registry is intentionally independent from persistence.
    Persistence can be added later without coupling the core
    agent registry to a storage implementation.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    # ========================================================
    # Register
    # ========================================================

    def register(
        self,
        agent: Agent,
    ) -> bool:
        """
        Register an Agent instance.

        Returns:
            True when registration succeeds.

        Raises:
            AgentValidationError:
                If the supplied object is not an Agent.
            AgentAlreadyExistsError:
                If the agent ID is already registered.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentValidationError(
                "Only Agent instances can be registered."
            )

        agent.validate()

        if agent.id in self._agents:
            raise AgentAlreadyExistsError(
                f"Agent already exists: {agent.id}"
            )

        self._agents[agent.id] = agent

        return True

    # ========================================================
    # Unregister
    # ========================================================

    def unregister(
        self,
        agent_id: str,
    ) -> bool:
        """
        Remove an agent from the registry.

        Returns:
            True if removed, otherwise False.
        """

        if agent_id not in self._agents:
            return False

        del self._agents[agent_id]

        return True

    # ========================================================
    # Backward-Compatible Remove
    # ========================================================

    def remove(
        self,
        agent_id: str,
    ) -> bool:
        """
        Backward-compatible alias for unregister().

        This keeps compatibility with earlier AgentRegistry
        APIs and existing tests.
        """

        return self.unregister(
            agent_id
        )

    # ========================================================
    # Get
    # ========================================================

    def get(
        self,
        agent_id: str,
    ) -> Optional[Agent]:
        """
        Return an agent by ID.

        Returns:
            Agent instance or None.
        """

        return self._agents.get(
            agent_id
        )

    # ========================================================
    # Require
    # ========================================================

    def require(
        self,
        agent_id: str,
    ) -> Agent:
        """
        Return an agent by ID.

        Raises:
            AgentNotFoundError:
                If the agent does not exist.
        """

        agent = self.get(
            agent_id
        )

        if agent is None:
            raise AgentNotFoundError(
                f"Agent not found: {agent_id}"
            )

        return agent

    # ========================================================
    # Exists
    # ========================================================

    def exists(
        self,
        agent_id: str,
    ) -> bool:
        """
        Check whether an agent exists.
        """

        return agent_id in self._agents

    # ========================================================
    # List Agents
    # ========================================================

    def list_agents(
        self,
    ) -> List[Agent]:
        """
        Return all registered agents.
        """

        return list(
            self._agents.values()
        )

    # ========================================================
    # Backward-Compatible List
    # ========================================================

    def list(
        self,
    ) -> List[Agent]:
        """
        Backward-compatible alias for list_agents().

        This keeps compatibility with earlier AgentRegistry
        APIs and existing tests.
        """

        return self.list_agents()

    # ========================================================
    # Count
    # ========================================================

    def count(
        self,
    ) -> int:
        """
        Return the number of registered agents.
        """

        return len(
            self._agents
        )

    # ========================================================
    # Clear
    # ========================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all registered agents.
        """

        self._agents.clear()

    # ========================================================
    # Restore
    # ========================================================

    def restore(
        self,
        data: dict,
    ) -> Agent:
        """
        Restore and register an agent from a dictionary.

        Returns:
            Restored Agent instance.
        """

        agent = Agent.from_dict(
            data
        )

        self.register(
            agent
        )

        return agent

    # ========================================================
    # Export
    # ========================================================

    def export_all(
        self,
    ) -> List[dict]:
        """
        Export all registered agents as dictionaries.
        """

        return [
            agent.to_dict()
            for agent in self.list_agents()
        ]

    # ========================================================
    # Replace
    # ========================================================

    def replace(
        self,
        agent: Agent,
    ) -> bool:
        """
        Replace an existing agent with the same ID.

        Returns:
            True when replacement succeeds.

        Raises:
            AgentValidationError:
                If the object is not an Agent.
        """

        if not isinstance(
            agent,
            Agent,
        ):
            raise AgentValidationError(
                "Only Agent instances can be registered."
            )

        agent.validate()

        self._agents[agent.id] = agent

        return True

    # ========================================================
    # Find By Name
    # ========================================================

    def find_by_name(
        self,
        name: str,
    ) -> Optional[Agent]:
        """
        Find the first agent matching a name.

        Name comparison is case-insensitive.
        """

        if not isinstance(
            name,
            str,
        ):
            return None

        target = name.strip().lower()

        for agent in self._agents.values():

            if agent.name.lower() == target:
                return agent

        return None

    # ========================================================
    # Active Agents
    # ========================================================

    def list_active(
        self,
    ) -> List[Agent]:
        """
        Return all currently active agents.
        """

        return [
            agent
            for agent in self._agents.values()
            if agent.is_active()
        ]

    # ========================================================
    # Status Filtering
    # ========================================================

    def list_by_status(
        self,
        status: str,
    ) -> List[Agent]:
        """
        Return all agents with a specific status.
        """

        if status not in Agent.VALID_STATUSES:
            raise AgentValidationError(
                f"Invalid agent status: {status}"
            )

        return [
            agent
            for agent in self._agents.values()
            if agent.status == status
        ]

    # ========================================================
    # Representation
    # ========================================================

    def __len__(
        self,
    ) -> int:
        """
        Return the number of registered agents.
        """

        return self.count()

    def __contains__(
        self,
        agent_id: str,
    ) -> bool:
        """
        Support:

            agent_id in registry
        """

        return self.exists(
            agent_id
        )

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"AgentRegistry("
            f"count={self.count()}"
            f")"
        )