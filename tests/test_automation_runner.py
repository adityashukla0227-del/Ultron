"""
Ultron Automation Runner Tests
Version: v0.34
"""

from datetime import datetime, timedelta

import pytest

from modules.automation.engine import (
    AutomationEngine,
)

from modules.automation.scheduler import (
    AutomationScheduler,
)

from modules.automation.runner import (
    AutomationRunner,
)


# ============================================================
# Helpers
# ============================================================

def create_test_system():
    """
    Create a fresh engine, scheduler and runner.
    """

    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello from scheduled Ultron",
    )

    automation_id = engine.register_automation(
        name="Hello Automation",
        action="hello",
    )

    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine=engine,
        scheduler=scheduler,
    )

    return (
        engine,
        scheduler,
        runner,
        automation_id,
    )


# ============================================================
# Basic Runner Tests
# ============================================================

def test_runner_initialization():
    engine = AutomationEngine()
    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    assert runner.engine is engine
    assert runner.scheduler is scheduler


def test_no_due_schedules():
    engine = AutomationEngine()
    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    assert runner.has_due_schedules() is False


# ============================================================
# Due Schedule Tests
# ============================================================

def test_has_due_schedule():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    assert runner.has_due_schedules() is True

    assert (
        scheduler.get_schedule(
            schedule_id
        )["enabled"]
        is True
    )


def test_future_schedule_not_due():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    scheduler.create_schedule(
        automation_id,
        datetime.now() + timedelta(
            minutes=10
        ),
    )

    assert runner.has_due_schedules() is False


# ============================================================
# Single Schedule Execution
# ============================================================

def test_run_schedule():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    result = runner.run_schedule(
        schedule_id
    )

    assert result == (
        "Hello from scheduled Ultron"
    )


def test_run_schedule_disables_one_time():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    runner.run_schedule(
        schedule_id
    )

    schedule = scheduler.get_schedule(
        schedule_id
    )

    assert schedule["enabled"] is False
    assert schedule["run_count"] == 1


# ============================================================
# Run Due Tests
# ============================================================

def test_run_due():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    results = runner.run_due()

    assert len(results) == 1

    result = results[0]

    assert result["schedule_id"] == schedule_id
    assert result["automation_id"] == automation_id
    assert result["success"] is True
    assert result["result"] == (
        "Hello from scheduled Ultron"
    )


def test_run_due_multiple_schedules():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    first = engine.register_automation(
        "First",
        "hello",
    )

    second = engine.register_automation(
        "Second",
        "hello",
    )

    scheduler = AutomationScheduler()

    scheduler.create_schedule(
        first,
        datetime.now() - timedelta(
            minutes=2
        ),
    )

    scheduler.create_schedule(
        second,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    results = runner.run_due()

    assert len(results) == 2

    assert all(
        item["success"]
        for item in results
    )


# ============================================================
# Disabled Schedule Tests
# ============================================================

def test_disabled_schedule_not_due():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    scheduler.disable_schedule(
        schedule_id
    )

    assert runner.has_due_schedules() is False


def test_run_disabled_schedule_fails():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    scheduler.disable_schedule(
        schedule_id
    )

    with pytest.raises(Exception):
        runner.run_schedule(
            schedule_id
        )


# ============================================================
# Missing Schedule Tests
# ============================================================

def test_missing_schedule():
    engine = AutomationEngine()
    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    with pytest.raises(Exception):
        runner.run_schedule(
            "missing-schedule"
        )


# ============================================================
# Recurring Schedule Tests
# ============================================================

def test_recurring_schedule():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
        recurring=True,
        interval_minutes=60,
    )

    result = runner.run_schedule(
        schedule_id
    )

    assert result == (
        "Hello from scheduled Ultron"
    )

    schedule = scheduler.get_schedule(
        schedule_id
    )

    assert schedule["enabled"] is True
    assert schedule["recurring"] is True
    assert schedule["run_count"] == 1


def test_recurring_schedule_runs_again():
    (
        engine,
        scheduler,
        runner,
        automation_id,
    ) = create_test_system()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
        recurring=True,
        interval_minutes=60,
    )

    runner.run_schedule(
        schedule_id
    )

    schedule = scheduler.get_schedule(
        schedule_id
    )

    schedule["run_at"] = (
        datetime.now()
        - timedelta(minutes=1)
    )

    results = runner.run_due()

    assert len(results) == 1
    assert results[0]["success"] is True

    schedule = scheduler.get_schedule(
        schedule_id
    )

    assert schedule["run_count"] == 2
    assert schedule["enabled"] is True


# ============================================================
# Failed Action Test
# ============================================================

def test_failed_automation():
    engine = AutomationEngine()

    def failing_action():
        raise RuntimeError(
            "Intentional test failure"
        )

    engine.register_action(
        "fail",
        failing_action,
    )

    automation_id = engine.register_automation(
        "Fail Automation",
        "fail",
    )

    scheduler = AutomationScheduler()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now() - timedelta(
            minutes=1
        ),
    )

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    results = runner.run_due()

    assert len(results) == 1

    result = results[0]

    assert result["success"] is False
    assert "error" in result
    assert schedule_id == result[
        "schedule_id"
    ]