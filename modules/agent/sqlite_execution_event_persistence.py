"""
Ultron SQLite Execution Event Persistence.

v0.47 — Persistent Execution History

Provides SQLite-backed persistence for immutable
ExecutionEvent instances.

This layer implements the ExecutionEventPersistence
contract without coupling persistence to execution control.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import RLock

from modules.agent.execution_event import ExecutionEvent
from modules.agent.execution_event_persistence import (
    ExecutionEventPersistence,
    ExecutionEventPersistenceError,
)


class SQLiteExecutionEventPersistence(ExecutionEventPersistence):
    """
    SQLite-backed persistence for execution events.

    Responsibilities:
    - Persist execution events
    - Retrieve execution history
    - Preserve event ordering
    - Provide execution-level queries
    - Keep persistence independent from execution control
    """

    def __init__(
        self,
        database_path: str | Path,
    ) -> None:
        """
        Initialize SQLite execution event persistence.

        Args:
            database_path:
                Path to the SQLite database file.
        """

        if not isinstance(database_path, (str, Path)):
            raise ExecutionEventPersistenceError(
                "database_path must be a string or Path."
            )

        database_path = Path(database_path)

        if not str(database_path).strip():
            raise ExecutionEventPersistenceError(
                "database_path cannot be empty."
            )

        self.database_path = database_path
        self._lock = RLock()

        try:
            self.database_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self._connection = sqlite3.connect(
                str(self.database_path),
                check_same_thread=False,
            )

            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    step_id TEXT,
                    step_index INTEGER,
                    message TEXT,
                    metadata TEXT NOT NULL
                )
                """
            )

            self._connection.commit()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to initialize SQLite persistence: {exc}"
            ) from exc

    # ========================================================
    # Validation
    # ========================================================

    @staticmethod
    def _validate_execution_id(
        execution_id: object,
    ) -> None:
        """Validate an execution identifier."""

        if not isinstance(execution_id, str):
            raise ExecutionEventPersistenceError(
                "execution_id must be a string."
            )

        if not execution_id.strip():
            raise ExecutionEventPersistenceError(
                "execution_id cannot be empty."
            )

    @staticmethod
    def _validate_event(
        event: object,
    ) -> None:
        """Validate an execution event."""

        if not isinstance(event, ExecutionEvent):
            raise ExecutionEventPersistenceError(
                "event must be an ExecutionEvent instance."
            )

    # ========================================================
    # Persistence
    # ========================================================

    def save(
        self,
        event: ExecutionEvent,
    ) -> ExecutionEvent:
        """Persist and return an execution event."""

        self._validate_event(event)

        try:
            with self._lock:
                self._connection.execute(
                    """
                    INSERT INTO execution_events (
                        event_type,
                        execution_id,
                        timestamp,
                        step_id,
                        step_index,
                        message,
                        metadata
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.event_type.value,
                        event.execution_id,
                        event.timestamp.isoformat(),
                        event.step_id,
                        event.step_index,
                        event.message,
                        self._serialize_metadata(event),
                    ),
                )

                self._connection.commit()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to persist execution event: {exc}"
            ) from exc

        return event

    def save_many(
        self,
        events: list[ExecutionEvent],
    ) -> list[ExecutionEvent]:
        """Persist multiple execution events atomically."""

        if not isinstance(events, list):
            raise ExecutionEventPersistenceError(
                "events must be a list."
            )

        for event in events:
            self._validate_event(event)

        try:
            with self._lock:
                self._connection.executemany(
                    """
                    INSERT INTO execution_events (
                        event_type,
                        execution_id,
                        timestamp,
                        step_id,
                        step_index,
                        message,
                        metadata
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            event.event_type.value,
                            event.execution_id,
                            event.timestamp.isoformat(),
                            event.step_id,
                            event.step_index,
                            event.message,
                            self._serialize_metadata(event),
                        )
                        for event in events
                    ],
                )

                self._connection.commit()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to persist execution events: {exc}"
            ) from exc

        return list(events)

    # ========================================================
    # Retrieval
    # ========================================================

    def get_events(
        self,
        execution_id: str,
    ) -> list[ExecutionEvent]:
        """Return all persisted events for an execution."""

        self._validate_execution_id(execution_id)

        try:
            with self._lock:
                cursor = self._connection.execute(
                    """
                    SELECT
                        event_type,
                        execution_id,
                        timestamp,
                        step_id,
                        step_index,
                        message,
                        metadata
                    FROM execution_events
                    WHERE execution_id = ?
                    ORDER BY id ASC
                    """,
                    (execution_id,),
                )

                rows = cursor.fetchall()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to retrieve execution events: {exc}"
            ) from exc

        return [
            self._row_to_event(row)
            for row in rows
        ]

    def get_latest(
        self,
        execution_id: str,
    ) -> ExecutionEvent | None:
        """Return the latest persisted event."""

        events = self.get_events(execution_id)

        if not events:
            return None

        return events[-1]

    def count(
        self,
        execution_id: str,
    ) -> int:
        """Return the number of persisted events."""

        self._validate_execution_id(execution_id)

        try:
            with self._lock:
                cursor = self._connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM execution_events
                    WHERE execution_id = ?
                    """,
                    (execution_id,),
                )

                result = cursor.fetchone()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to count execution events: {exc}"
            ) from exc

        return int(result[0])

    def execution_ids(self) -> list[str]:
        """
        Return all execution IDs with persisted events.

        Execution IDs are returned in the order in which
        they first appeared in the database.
        """

        try:
            with self._lock:
                cursor = self._connection.execute(
                    """
                    SELECT execution_id
                    FROM execution_events
                    GROUP BY execution_id
                    ORDER BY MIN(id) ASC
                    """
                )

                rows = cursor.fetchall()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to retrieve execution IDs: {exc}"
            ) from exc

        return [
            row[0]
            for row in rows
        ]

    # ========================================================
    # Clearing
    # ========================================================

    def clear(
        self,
        execution_id: str | None = None,
    ) -> None:
        """
        Clear persisted execution events.

        If execution_id is None, clear the complete database table.
        Otherwise, clear only the specified execution.
        """

        if execution_id is not None:
            self._validate_execution_id(execution_id)

        try:
            with self._lock:
                if execution_id is None:
                    self._connection.execute(
                        "DELETE FROM execution_events"
                    )
                else:
                    self._connection.execute(
                        """
                        DELETE FROM execution_events
                        WHERE execution_id = ?
                        """,
                        (execution_id,),
                    )

                self._connection.commit()

        except sqlite3.Error as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to clear execution events: {exc}"
            ) from exc

    # ========================================================
    # Serialization
    # ========================================================

    @staticmethod
    def _serialize_metadata(
        event: ExecutionEvent,
    ) -> str:
        """Serialize event metadata into JSON."""

        import json

        try:
            return json.dumps(
                event.metadata,
                sort_keys=True,
            )
        except (TypeError, ValueError) as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to serialize event metadata: {exc}"
            ) from exc

    @staticmethod
    def _row_to_event(
        row: tuple,
    ) -> ExecutionEvent:
        """Convert a SQLite row into an ExecutionEvent."""

        import json

        (
            event_type,
            execution_id,
            timestamp,
            step_id,
            step_index,
            message,
            metadata,
        ) = row

        try:
            return ExecutionEvent.from_dict(
                {
                    "event_type": event_type,
                    "execution_id": execution_id,
                    "timestamp": timestamp,
                    "step_id": step_id,
                    "step_index": step_index,
                    "message": message,
                    "metadata": json.loads(metadata),
                }
            )

        except (
            TypeError,
            ValueError,
            KeyError,
            json.JSONDecodeError,
        ) as exc:
            raise ExecutionEventPersistenceError(
                f"Failed to deserialize execution event: {exc}"
            ) from exc

    # ========================================================
    # Lifecycle
    # ========================================================

    def close(self) -> None:
        """Close the SQLite connection."""

        with self._lock:
            self._connection.close()

    def __enter__(
        self,
    ) -> "SQLiteExecutionEventPersistence":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()


__all__ = [
    "SQLiteExecutionEventPersistence",
]