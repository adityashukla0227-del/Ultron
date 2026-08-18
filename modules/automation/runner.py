"""
Ultron Automation Runner
Version: v0.34

Connects the scheduler with the automation engine.

Flow:

Scheduler
    ↓
Due Schedule
    ↓
Automation Engine
    ↓
Action Registry
    ↓
Action Execution
"""

from datetime import datetime
from typing import Any, Dict, Optional

from modules.automation.engine import (
    AutomationEngine,
    AutomationExecutionError,
)

from modules.automation.scheduler import (
    AutomationScheduler,
)


class AutomationRunner:
    """
    Executes automations that are due according to
    the scheduler.
    """

    def __init__(
        self,
        engine: AutomationEngine,
        scheduler: AutomationScheduler,
    ) -> None:

        self.engine = engine
        self.scheduler = scheduler

    # ========================================================
    # Run One Schedule
    # ========================================================

    def run_schedule(
        self,
        schedule_id: str,
        now: Optional[datetime] = None,
    ) -> Any:
        """
        Execute a single scheduled automation.

        The schedule must exist and be enabled.
        """

        schedule = self.scheduler.get_schedule(
            schedule_id
        )

        if schedule is None:
            raise AutomationExecutionError(
                "Schedule not found."
            )

        if not schedule["enabled"]:
            raise AutomationExecutionError(
                "Schedule is disabled."
            )

        automation_id = schedule[
            "automation_id"
        ]

        try:
            result = self.engine.execute(
                automation_id
            )

            self.scheduler.mark_executed(
                schedule_id,
                executed_at=now,
            )

            return result

        except Exception as exc:

            raise AutomationExecutionError(
                f"Scheduled automation failed: "
                f"{exc}"
            ) from exc

    # ========================================================
    # Run Due Schedules
    # ========================================================

    def run_due(
        self,
        now: Optional[datetime] = None,
    ) -> list[Dict[str, Any]]:
        """
        Execute all schedules that are currently due.

        Returns a result list containing:
        - schedule ID
        - automation ID
        - success state
        - result or error
        """

        due_schedules = (
            self.scheduler.get_due_schedules(
                now=now
            )
        )

        results = []

        for schedule in due_schedules:

            schedule_id = schedule["id"]

            automation_id = schedule[
                "automation_id"
            ]

            try:

                result = self.run_schedule(
                    schedule_id,
                    now=now,
                )

                results.append(
                    {
                        "schedule_id": schedule_id,
                        "automation_id": automation_id,
                        "success": True,
                        "result": result,
                    }
                )

            except Exception as exc:

                results.append(
                    {
                        "schedule_id": schedule_id,
                        "automation_id": automation_id,
                        "success": False,
                        "error": str(exc),
                    }
                )

        return results

    # ========================================================
    # Check Due Schedules
    # ========================================================

    def has_due_schedules(
        self,
        now: Optional[datetime] = None,
    ) -> bool:
        """
        Check whether at least one enabled schedule
        is currently due.
        """

        return bool(
            self.scheduler.get_due_schedules(
                now=now
            )
        )