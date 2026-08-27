"""
Ultron Execution Event Persistence.

v0.47 — Persistent Execution History

Defines the persistence contract for execution events.

This module intentionally separates persistent execution history
from the runtime ExecutionEventStore implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.agent.execution_event import ExecutionEvent


class ExecutionEventPersistenceError(Exception):
    """Base exception for execution event persistence errors."""


class ExecutionEventPersistence(ABC):
    """
    Abstract persistence contract for execution events.

    Implementations are responsible for storing and retrieving
    immutable ExecutionEvent instances.

    The persistence layer must not control execution, modify
    execution state, or provide execution orchestration behavior.
    """

    @abstractmethod
    def save(
        self,
        event: ExecutionEvent,
    ) -> ExecutionEvent:
        """Persist and return an execution event."""

        raise NotImplementedError

    @abstractmethod
    def save_many(
        self,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        """Persist multiple execution events atomically."""

        raise NotImplementedError

    @abstractmethod
    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """Return all persisted events for an execution."""

        raise NotImplementedError

    @abstractmethod
    def get_latest(
        self,
        execution_id: str,
    ) -> ExecutionEvent | None:
        """Return the latest persisted event for an execution."""

        raise NotImplementedError

    @abstractmethod
    def count(
        self,
        execution_id: str,
    ) -> int:
        """Return the number of persisted events."""

        raise NotImplementedError

    @abstractmethod
    def execution_ids(self) -> list[str]:
        """Return all execution IDs with persisted events."""

        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
        execution_id: str | None = None,
    ) -> None:
        """
        Clear persisted execution events.

        If execution_id is None, clear all persisted events.
        Otherwise, clear only the specified execution.
        """

        raise NotImplementedError


__all__ = [
    "ExecutionEventPersistence",
    "ExecutionEventPersistenceError",
]