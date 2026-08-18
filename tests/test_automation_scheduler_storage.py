"""
Tests for persistent AutomationScheduler.

Ultron v0.36
"""

from datetime import datetime, timedelta

from modules.automation.scheduler import (
    AutomationScheduler,
)
from modules.automation.storage import (
    AutomationStorage,
)


def create_scheduler(tmp_path):
    """Create an isolated persistent scheduler."""

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    return scheduler, storage


# ========================================================
# Creation
# ========================================================


def test_create_schedule_persists(tmp_path):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    run_at = datetime.now() + timedelta(
        minutes=10
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-1",
        run_at=run_at,
    )

    stored = storage.get_schedule(
        schedule_id
    )

    assert stored is not None
    assert stored["id"] == schedule_id
    assert stored["automation_id"] == "auto-1"


# ========================================================
# Restore
# ========================================================


def test_schedule_survives_new_scheduler_instance(
    tmp_path,
):

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    run_at = datetime.now() + timedelta(
        minutes=10
    )

    first = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    schedule_id = first.create_schedule(
        automation_id="auto-1",
        run_at=run_at,
    )

    second = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = second.get_schedule(
        schedule_id
    )

    assert restored is not None
    assert restored["automation_id"] == "auto-1"
    assert restored["run_at"] == run_at


# ========================================================
# Datetime Restoration
# ========================================================


def test_datetime_is_restored_correctly(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    run_at = datetime(
        2026,
        8,
        20,
        15,
        30,
        45,
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-time",
        run_at=run_at,
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = new_scheduler.get_schedule(
        schedule_id
    )

    assert isinstance(
        restored["run_at"],
        datetime,
    )

    assert restored["run_at"] == run_at


# ========================================================
# Enable / Disable Persistence
# ========================================================


def test_disable_schedule_persists(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-1",
        run_at=datetime.now(),
    )

    assert scheduler.disable_schedule(
        schedule_id
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = new_scheduler.get_schedule(
        schedule_id
    )

    assert restored["enabled"] is False


def test_enable_schedule_persists(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-1",
        run_at=datetime.now(),
    )

    scheduler.disable_schedule(
        schedule_id
    )

    assert scheduler.enable_schedule(
        schedule_id
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = new_scheduler.get_schedule(
        schedule_id
    )

    assert restored["enabled"] is True


# ========================================================
# One-Time Execution Persistence
# ========================================================


def test_one_time_execution_persists(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-1",
        run_at=datetime.now(),
    )

    executed_at = datetime(
        2026,
        8,
        20,
        16,
        0,
    )

    assert scheduler.mark_executed(
        schedule_id,
        executed_at=executed_at,
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = new_scheduler.get_schedule(
        schedule_id
    )

    assert restored["enabled"] is False
    assert restored["run_count"] == 1
    assert restored["last_run"] == executed_at


# ========================================================
# Recurring Execution Persistence
# ========================================================


def test_recurring_execution_persists(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-recurring",
        run_at=datetime.now(),
        recurring=True,
        interval_minutes=30,
    )

    executed_at = datetime(
        2026,
        8,
        20,
        17,
        0,
    )

    assert scheduler.mark_executed(
        schedule_id,
        executed_at=executed_at,
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = new_scheduler.get_schedule(
        schedule_id
    )

    expected_next_run = (
        executed_at
        + timedelta(minutes=30)
    )

    assert restored["enabled"] is True
    assert restored["run_count"] == 1
    assert restored["last_run"] == executed_at
    assert restored["run_at"] == expected_next_run


# ========================================================
# Delete Persistence
# ========================================================


def test_delete_schedule_removes_persistent_data(
    tmp_path,
):

    scheduler, storage = create_scheduler(
        tmp_path
    )

    schedule_id = scheduler.create_schedule(
        automation_id="auto-delete",
        run_at=datetime.now(),
    )

    assert storage.get_schedule(
        schedule_id
    ) is not None

    assert scheduler.delete_schedule(
        schedule_id
    )

    assert storage.get_schedule(
        schedule_id
    ) is None


# ========================================================
# Multiple Schedules
# ========================================================


def test_multiple_schedules_are_restored(
    tmp_path,
):

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    first = scheduler.create_schedule(
        automation_id="auto-1",
        run_at=datetime.now(),
    )

    second = scheduler.create_schedule(
        automation_id="auto-2",
        run_at=datetime.now(),
    )

    restored_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    schedules = (
        restored_scheduler.list_schedules()
    )

    ids = {
        schedule["id"]
        for schedule in schedules
    }

    assert first in ids
    assert second in ids
    assert len(schedules) == 2


# ========================================================
# ID Counter Restoration
# ========================================================


def test_schedule_counter_continues_after_restore(
    tmp_path,
):

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    first = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    first_id = first.create_schedule(
        automation_id="auto-1",
        run_at=datetime.now(),
    )

    second = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    second_id = second.create_schedule(
        automation_id="auto-2",
        run_at=datetime.now(),
    )

    assert first_id == "schedule-1"
    assert second_id == "schedule-2"