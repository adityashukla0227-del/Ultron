"""
Ultron Automation Persistence Integration Tests
Version: v0.36

Verifies that automation persistence works correctly
across manager, storage, scheduler, runner, and worker.
"""

from datetime import datetime, timedelta

from modules.automation.engine import AutomationEngine
from modules.automation.manager import AutomationManager
from modules.automation.runner import AutomationRunner
from modules.automation.scheduler import AutomationScheduler
from modules.automation.storage import AutomationStorage
from modules.automation.worker import AutomationWorker


# ========================================================
# Full Persistence Flow
# ========================================================


def test_full_automation_persistence_flow(tmp_path):
    """
    Verify the complete automation persistence lifecycle.

    Flow:

    Manager
        ↓
    Storage
        ↓
    Scheduler
        ↓
    Runner
        ↓
    Worker
        ↓
    New instances
        ↓
    Restore and execute
    """

    storage_path = (
        tmp_path / "automations.json"
    )

    storage = AutomationStorage(
        storage_path
    )

    # ----------------------------------------------------
    # First application instance
    # ----------------------------------------------------

    engine = AutomationEngine()

    manager = AutomationManager(
        engine=engine,
        storage=storage,
    )

    manager.register_action(
        "hello",
        lambda: "Persistence works",
    )

    automation_id = manager.create_automation(
        name="Persistent Automation",
        action="hello",
    )

    scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    schedule_id = scheduler.create_schedule(
        automation_id=automation_id,
        run_at=datetime.now(),
    )

    # Verify both objects exist in storage.

    assert storage.get_automation(
        automation_id
    ) is not None

    assert storage.get_schedule(
        schedule_id
    ) is not None

    # ----------------------------------------------------
    # Simulate application restart
    # ----------------------------------------------------

    new_engine = AutomationEngine()

    new_manager = AutomationManager(
        engine=new_engine,
        storage=storage,
    )

    # Action handlers are runtime objects and therefore
    # must be registered again after restart.

    new_manager.register_action(
        "hello",
        lambda: "Persistence works",
    )

    restored_automation = (
        new_manager.get_automation(
            automation_id
        )
    )

    assert restored_automation is not None

    assert (
        restored_automation["name"]
        == "Persistent Automation"
    )

    new_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored_schedule = (
        new_scheduler.get_schedule(
            schedule_id
        )
    )

    assert restored_schedule is not None

    assert (
        restored_schedule["automation_id"]
        == automation_id
    )

    # ----------------------------------------------------
    # Runner execution after restart
    # ----------------------------------------------------

    runner = AutomationRunner(
        engine=new_engine,
        scheduler=new_scheduler,
    )

    results = runner.run_due(
        now=datetime.now()
    )

    assert len(results) == 1

    result = results[0]

    assert result["schedule_id"] == schedule_id
    assert result["automation_id"] == automation_id
    assert result["success"] is True
    assert result["result"] == "Persistence works"

    # ----------------------------------------------------
    # Verify execution state persisted
    # ----------------------------------------------------

    persisted_schedule = (
        storage.get_schedule(
            schedule_id
        )
    )

    assert persisted_schedule is not None

    assert (
        persisted_schedule["enabled"]
        is False
    )

    assert (
        persisted_schedule["run_count"]
        == 1
    )

    assert (
        persisted_schedule["last_run"]
        is not None
    )


# ========================================================
# Recurring Persistence Flow
# ========================================================


def test_recurring_schedule_persistence_flow(
    tmp_path,
):
    """
    Verify that a recurring schedule keeps its
    next execution time after persistence.
    """

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    engine = AutomationEngine()

    manager = AutomationManager(
        engine=engine,
        storage=storage,
    )

    manager.register_action(
        "heartbeat",
        lambda: "Heartbeat",
    )

    automation_id = manager.create_automation(
        name="Recurring Automation",
        action="heartbeat",
    )

    scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    initial_run = datetime(
        2026,
        8,
        18,
        23,
        0,
    )

    schedule_id = scheduler.create_schedule(
        automation_id=automation_id,
        run_at=initial_run,
        recurring=True,
        interval_minutes=30,
    )

    # ----------------------------------------------------
    # Execute recurring schedule
    # ----------------------------------------------------

    runner = AutomationRunner(
        engine=engine,
        scheduler=scheduler,
    )

    executed_at = initial_run

    results = runner.run_due(
        now=executed_at
    )

    assert len(results) == 1
    assert results[0]["success"] is True

    expected_next_run = (
        executed_at
        + timedelta(minutes=30)
    )

    schedule = scheduler.get_schedule(
        schedule_id
    )

    assert schedule is not None

    assert (
        schedule["run_at"]
        == expected_next_run
    )

    assert schedule["enabled"] is True

    # ----------------------------------------------------
    # Simulate restart
    # ----------------------------------------------------

    restored_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    restored = (
        restored_scheduler.get_schedule(
            schedule_id
        )
    )

    assert restored is not None

    assert (
        restored["run_at"]
        == expected_next_run
    )

    assert restored["run_count"] == 1


# ========================================================
# Worker Persistence Flow
# ========================================================


def test_worker_executes_restored_schedule(
    tmp_path,
):
    """
    Verify that the background worker can execute a
    schedule restored from persistent storage.
    """

    storage = AutomationStorage(
        tmp_path / "automations.json"
    )

    engine = AutomationEngine()

    manager = AutomationManager(
        engine=engine,
        storage=storage,
    )

    manager.register_action(
        "worker_test",
        lambda: "Worker persistence works",
    )

    automation_id = manager.create_automation(
        name="Worker Persistent Automation",
        action="worker_test",
    )

    scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    scheduler.create_schedule(
        automation_id=automation_id,
        run_at=datetime.now(),
    )

    # ----------------------------------------------------
    # Restore everything
    # ----------------------------------------------------

    restored_engine = AutomationEngine()

    restored_manager = AutomationManager(
        engine=restored_engine,
        storage=storage,
    )

    restored_manager.register_action(
        "worker_test",
        lambda: "Worker persistence works",
    )

    restored_scheduler = AutomationScheduler(
        storage=storage,
        persist=True,
    )

    runner = AutomationRunner(
        engine=restored_engine,
        scheduler=restored_scheduler,
    )

    worker = AutomationWorker(
        runner=runner,
        interval_seconds=60,
    )

    # ----------------------------------------------------
    # Execute one worker cycle
    # ----------------------------------------------------

    results = worker.run_once()

    assert len(results) == 1

    assert results[0]["success"] is True

    assert (
        results[0]["result"]
        == "Worker persistence works"
    )

    assert worker.last_results

    assert worker.last_error is None