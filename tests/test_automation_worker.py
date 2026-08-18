"""
Ultron Automation Worker Tests
Version: v0.34
"""

from datetime import datetime, timedelta

import time

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

from modules.automation.worker import (
    AutomationWorker,
)


# ============================================================
# Helpers
# ============================================================

def create_worker(
    interval_seconds=0.05,
):
    """
    Create a fresh automation system.
    """

    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Worker Test Success",
    )

    automation_id = engine.register_automation(
        "Worker Automation",
        "hello",
    )

    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    worker = AutomationWorker(
        runner,
        interval_seconds=interval_seconds,
    )

    return (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    )


# ============================================================
# Initialization
# ============================================================

def test_worker_initialization():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    assert worker.runner is runner
    assert worker.interval_seconds == 0.05
    assert worker.running is False


def test_invalid_interval():

    engine = AutomationEngine()
    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    with pytest.raises(ValueError):

        AutomationWorker(
            runner,
            interval_seconds=0,
        )


# ============================================================
# run_once
# ============================================================

def test_run_once_without_due_schedule():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    results = worker.run_once()

    assert results == []
    assert worker.last_results == []
    assert worker.last_error is None


def test_run_once_executes_due_schedule():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now()
        - timedelta(minutes=1),
    )

    results = worker.run_once()

    assert len(results) == 1

    result = results[0]

    assert result["schedule_id"] == schedule_id
    assert result["automation_id"] == automation_id
    assert result["success"] is True
    assert result["result"] == (
        "Worker Test Success"
    )


def test_run_once_updates_last_results():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    scheduler.create_schedule(
        automation_id,
        datetime.now()
        - timedelta(minutes=1),
    )

    results = worker.run_once()

    assert worker.last_results == results


# ============================================================
# Status
# ============================================================

def test_initial_status():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    status = worker.status()

    assert status["running"] is False
    assert status["interval_seconds"] == 0.05
    assert status["last_results"] == []
    assert status["last_error"] is None


def test_status_after_execution():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    scheduler.create_schedule(
        automation_id,
        datetime.now()
        - timedelta(minutes=1),
    )

    worker.run_once()

    status = worker.status()

    assert status["running"] is False
    assert len(
        status["last_results"]
    ) == 1


# ============================================================
# Start / Stop
# ============================================================

def test_start_worker():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    assert worker.start() is True

    try:

        assert worker.running is True

    finally:

        worker.stop()


def test_start_worker_twice():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    assert worker.start() is True

    try:

        assert worker.start() is False

    finally:

        worker.stop()


def test_stop_worker():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    worker.start()

    assert worker.running is True

    assert worker.stop() is True

    assert worker.running is False


def test_stop_when_not_running():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    assert worker.stop() is False


# ============================================================
# Background Execution
# ============================================================

def test_background_worker_executes_schedule():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker(
        interval_seconds=0.02
    )

    scheduler.create_schedule(
        automation_id,
        datetime.now()
        - timedelta(minutes=1),
    )

    worker.start()

    try:

        time.sleep(0.08)

        assert len(
            worker.last_results
        ) == 1

        assert (
            worker.last_results[0]["success"]
            is True
        )

    finally:

        worker.stop()


def test_background_worker_stops_cleanly():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    worker.start()

    assert worker.running is True

    worker.stop()

    assert worker.running is False


# ============================================================
# Recurring Automation
# ============================================================

def test_recurring_automation_runs():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker(
        interval_seconds=0.02
    )

    schedule_id = scheduler.create_schedule(
        automation_id,
        datetime.now()
        - timedelta(minutes=1),
        recurring=True,
        interval_minutes=60,
    )

    worker.start()

    try:

        time.sleep(0.08)

        schedule = scheduler.get_schedule(
            schedule_id
        )

        assert schedule["run_count"] >= 1
        assert schedule["enabled"] is True

    finally:

        worker.stop()


# ============================================================
# Error Handling
# ============================================================

def test_worker_handles_runner_error():

    engine = AutomationEngine()

    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    def broken_run_due():

        raise RuntimeError(
            "Worker test error"
        )

    runner.run_due = broken_run_due

    worker = AutomationWorker(
        runner,
        interval_seconds=0.05,
    )

    results = worker.run_once()

    assert results == []

    assert worker.last_error == (
        "Worker test error"
    )


def test_worker_status_contains_error():

    engine = AutomationEngine()

    scheduler = AutomationScheduler()

    runner = AutomationRunner(
        engine,
        scheduler,
    )

    def broken_run_due():

        raise RuntimeError(
            "Status error"
        )

    runner.run_due = broken_run_due

    worker = AutomationWorker(
        runner,
        interval_seconds=0.05,
    )

    worker.run_once()

    status = worker.status()

    assert status["last_error"] == (
        "Status error"
    )


# ============================================================
# Context Manager
# ============================================================

def test_context_manager():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    with worker as active_worker:

        assert active_worker is worker
        assert worker.running is True

    assert worker.running is False


def test_context_manager_stops_after_exception():

    (
        engine,
        scheduler,
        runner,
        worker,
        automation_id,
    ) = create_worker()

    with pytest.raises(RuntimeError):

        with worker:

            assert worker.running is True

            raise RuntimeError(
                "Context test"
            )

    assert worker.running is False