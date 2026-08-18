"""
Ultron Automation Scheduler
Version: v0.36

Persistent scheduling layer for one-time and recurring
automation execution.

Responsibilities:
- Create schedules
- Validate schedules
- Persist schedules
- Restore schedules
- Track next execution time
- Enable/disable schedules
- Detect due schedules
- Calculate recurring execution times

The scheduler does not execute automations.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from modules.automation.storage import AutomationStorage


class SchedulerError(Exception):
    """Base scheduler exception."""


class ScheduleValidationError(SchedulerError):
    """Raised when a schedule is invalid."""


class AutomationScheduler:
    """
    Scheduler for one-time and recurring automations.

    Persistence is optional so existing in-memory usage
    remains fully compatible.
    """

    def __init__(
        self,
        storage: Optional[AutomationStorage] = None,
        persist: bool = False,
    ) -> None:

        self.schedules: Dict[str, Dict[str, Any]] = {}

        self._counter = 0

        self.storage = storage
        self.persist = persist

        if self.persist and self.storage is not None:
            self._restore_schedules()

    # ========================================================
    # ID Generation
    # ========================================================

    def _generate_id(self) -> str:
        """Generate a unique schedule ID."""

        self._counter += 1

        return f"schedule-{self._counter}"

    # ========================================================
    # Serialization Helpers
    # ========================================================

    def _serialize_schedule(
        self,
        schedule: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert a schedule into JSON-safe data.
        """

        data = dict(schedule)

        run_at = data.get("run_at")
        last_run = data.get("last_run")

        if isinstance(run_at, datetime):
            data["run_at"] = run_at.isoformat()

        if isinstance(last_run, datetime):
            data["last_run"] = last_run.isoformat()

        return data

    def _deserialize_schedule(
        self,
        schedule: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Convert stored schedule data back into runtime data.
        """

        data = dict(schedule)

        run_at = data.get("run_at")
        last_run = data.get("last_run")

        try:
            if isinstance(run_at, str):
                data["run_at"] = datetime.fromisoformat(
                    run_at
                )

            if isinstance(last_run, str):
                data["last_run"] = datetime.fromisoformat(
                    last_run
                )

        except ValueError:
            return None

        return data

    # ========================================================
    # Persistence Helpers
    # ========================================================

    def _persist_schedule(
        self,
        schedule_id: str,
    ) -> None:
        """Persist one schedule if persistence is enabled."""

        if not self.persist or self.storage is None:
            return

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return

        self.storage.save_schedule(
            self._serialize_schedule(
                schedule
            )
        )

    def _remove_persisted_schedule(
        self,
        schedule_id: str,
    ) -> None:
        """Remove one schedule from persistent storage."""

        if not self.persist or self.storage is None:
            return

        self.storage.delete_schedule(
            schedule_id
        )

    def _restore_schedules(self) -> None:
        """Restore valid schedules from persistent storage."""

        if self.storage is None:
            return

        stored_schedules = (
            self.storage.list_schedules()
        )

        highest_counter = 0

        for stored in stored_schedules:

            schedule = self._deserialize_schedule(
                stored
            )

            if schedule is None:
                continue

            schedule_id = schedule.get("id")

            if not isinstance(
                schedule_id,
                str,
            ):
                continue

            self.schedules[
                schedule_id
            ] = schedule

            if schedule_id.startswith(
                "schedule-"
            ):

                try:
                    number = int(
                        schedule_id.split(
                            "-",
                            1,
                        )[1]
                    )

                    highest_counter = max(
                        highest_counter,
                        number,
                    )

                except (
                    ValueError,
                    IndexError,
                ):
                    pass

        self._counter = highest_counter

    # ========================================================
    # Validation
    # ========================================================

    def _validate_interval(
        self,
        interval_minutes: Optional[int],
    ) -> None:
        """Validate recurring interval."""

        if interval_minutes is None:
            return

        if not isinstance(
            interval_minutes,
            int,
        ):
            raise ScheduleValidationError(
                "Interval must be an integer."
            )

        if interval_minutes <= 0:
            raise ScheduleValidationError(
                "Interval must be greater than zero."
            )

    def _validate_schedule(
        self,
        automation_id: str,
        run_at: datetime,
        recurring: bool,
        interval_minutes: Optional[int],
    ) -> None:
        """Validate schedule parameters."""

        if not isinstance(
            automation_id,
            str,
        ) or not automation_id.strip():

            raise ScheduleValidationError(
                "Automation ID is required."
            )

        if not isinstance(
            run_at,
            datetime,
        ):
            raise ScheduleValidationError(
                "run_at must be a datetime object."
            )

        if not isinstance(
            recurring,
            bool,
        ):
            raise ScheduleValidationError(
                "recurring must be boolean."
            )

        self._validate_interval(
            interval_minutes
        )

        if recurring and interval_minutes is None:
            raise ScheduleValidationError(
                "Recurring schedules require "
                "interval_minutes."
            )

    # ========================================================
    # Create Schedule
    # ========================================================

    def create_schedule(
        self,
        automation_id: str,
        run_at: datetime,
        recurring: bool = False,
        interval_minutes: Optional[int] = None,
    ) -> str:
        """Create and optionally persist a schedule."""

        self._validate_schedule(
            automation_id=automation_id,
            run_at=run_at,
            recurring=recurring,
            interval_minutes=interval_minutes,
        )

        schedule_id = self._generate_id()

        self.schedules[schedule_id] = {
            "id": schedule_id,
            "automation_id": automation_id,
            "run_at": run_at,
            "recurring": recurring,
            "interval_minutes": interval_minutes,
            "enabled": True,
            "last_run": None,
            "run_count": 0,
        }

        self._persist_schedule(
            schedule_id
        )

        return schedule_id

    # ========================================================
    # Get Schedule
    # ========================================================

    def get_schedule(
        self,
        schedule_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return a schedule by ID."""

        return self.schedules.get(
            schedule_id
        )

    # ========================================================
    # List Schedules
    # ========================================================

    def list_schedules(
        self,
    ) -> list[Dict[str, Any]]:
        """Return all schedules."""

        return list(
            self.schedules.values()
        )

    # ========================================================
    # Enable Schedule
    # ========================================================

    def enable_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """Enable a schedule."""

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return False

        schedule["enabled"] = True

        self._persist_schedule(
            schedule_id
        )

        return True

    # ========================================================
    # Disable Schedule
    # ========================================================

    def disable_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """Disable a schedule."""

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return False

        schedule["enabled"] = False

        self._persist_schedule(
            schedule_id
        )

        return True

    # ========================================================
    # Due Schedule Detection
    # ========================================================

    def get_due_schedules(
        self,
        now: Optional[datetime] = None,
    ) -> list[Dict[str, Any]]:
        """Return enabled schedules that are due."""

        now = now or datetime.now()

        due = []

        for schedule in self.schedules.values():

            if not schedule["enabled"]:
                continue

            if schedule["run_at"] <= now:
                due.append(schedule)

        return due

    # ========================================================
    # Mark Schedule Executed
    # ========================================================

    def mark_executed(
        self,
        schedule_id: str,
        executed_at: Optional[datetime] = None,
    ) -> bool:
        """
        Mark a schedule as executed.

        One-time schedules are disabled.

        Recurring schedules receive their next run time.
        """

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return False

        executed_at = (
            executed_at
            or datetime.now()
        )

        schedule["last_run"] = executed_at

        schedule["run_count"] += 1

        if schedule["recurring"]:

            interval = schedule[
                "interval_minutes"
            ]

            schedule["run_at"] = (
                executed_at
                + timedelta(
                    minutes=interval
                )
            )

        else:

            schedule["enabled"] = False

        self._persist_schedule(
            schedule_id
        )

        return True

    # ========================================================
    # Delete Schedule
    # ========================================================

    def delete_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """Delete a schedule."""

        if schedule_id not in self.schedules:
            return False

        del self.schedules[
            schedule_id
        ]

        self._remove_persisted_schedule(
            schedule_id
        )

        return True