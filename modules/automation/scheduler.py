"""
Ultron Automation Scheduler
Version: v0.34

Provides scheduling primitives for one-time and recurring
automation execution.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional


class SchedulerError(Exception):
    """Base scheduler exception."""


class ScheduleValidationError(SchedulerError):
    """Raised when a schedule is invalid."""


class AutomationScheduler:
    """
    Lightweight in-memory scheduler.

    Responsibilities:
    - Create schedules
    - Validate schedules
    - Track next execution time
    - Enable/disable schedules
    - Detect due schedules
    - Calculate recurring execution times

    Actual background execution will be added later.
    """

    def __init__(self) -> None:
        self.schedules: Dict[str, Dict[str, Any]] = {}

        self._counter = 0

    # ========================================================
    # ID Generation
    # ========================================================

    def _generate_id(self) -> str:
        """
        Generate a unique schedule ID.
        """

        self._counter += 1

        return f"schedule-{self._counter}"

    # ========================================================
    # Validation
    # ========================================================

    def _validate_interval(
        self,
        interval_minutes: Optional[int],
    ) -> None:
        """
        Validate recurring interval.
        """

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
        """
        Validate schedule parameters.
        """

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
        """
        Create a one-time or recurring schedule.

        Returns:
            Schedule ID.
        """

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

        return schedule_id

    # ========================================================
    # Get Schedule
    # ========================================================

    def get_schedule(
        self,
        schedule_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Return a schedule by ID.
        """

        return self.schedules.get(
            schedule_id
        )

    # ========================================================
    # List Schedules
    # ========================================================

    def list_schedules(
        self,
    ) -> list[Dict[str, Any]]:
        """
        Return all schedules.
        """

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
        """
        Enable a schedule.
        """

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return False

        schedule["enabled"] = True

        return True

    # ========================================================
    # Disable Schedule
    # ========================================================

    def disable_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """
        Disable a schedule.
        """

        schedule = self.get_schedule(
            schedule_id
        )

        if schedule is None:
            return False

        schedule["enabled"] = False

        return True

    # ========================================================
    # Due Schedule Detection
    # ========================================================

    def get_due_schedules(
        self,
        now: Optional[datetime] = None,
    ) -> list[Dict[str, Any]]:
        """
        Return enabled schedules that are due.
        """

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

        One-time schedules are automatically disabled.

        Recurring schedules receive a new run_at time.
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

        return True

    # ========================================================
    # Delete Schedule
    # ========================================================

    def delete_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """
        Delete a schedule.
        """

        if schedule_id not in self.schedules:
            return False

        del self.schedules[
            schedule_id
        ]

        return True