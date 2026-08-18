"""
Ultron Automation System Tests
Version: v0.34
"""

import pytest

from modules.automation.actions import (
    ActionRegistry,
    create_default_action_registry,
)

from modules.automation.engine import (
    AutomationEngine,
    AutomationExecutionError,
    AutomationValidationError,
)

from modules.automation.manager import (
    AutomationManager,
)


# ============================================================
# Action Registry Tests
# ============================================================

def test_action_registry_register():
    registry = ActionRegistry()

    result = registry.register(
        "hello",
        lambda: "Hello",
    )

    assert result is True
    assert registry.exists("hello")


def test_action_registry_get():
    registry = ActionRegistry()

    handler = lambda: "Hello"

    registry.register(
        "hello",
        handler,
    )

    assert registry.get("hello") is handler


def test_action_registry_remove():
    registry = ActionRegistry()

    registry.register(
        "hello",
        lambda: "Hello",
    )

    assert registry.remove("hello") is True
    assert registry.exists("hello") is False


def test_action_registry_execute():
    registry = ActionRegistry()

    registry.register(
        "echo",
        lambda message: message,
    )

    result = registry.execute(
        "echo",
        message="Ultron",
    )

    assert result == "Ultron"


def test_default_action_registry():
    registry = create_default_action_registry()

    assert registry.exists("hello")
    assert registry.exists("echo")

    assert (
        registry.execute("hello")
        == "Hello from Ultron Automation!"
    )

    assert (
        registry.execute(
            "echo",
            message="Ultron v0.34",
        )
        == "Ultron v0.34"
    )


# ============================================================
# Automation Engine Tests
# ============================================================

def test_engine_register_action():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    assert engine.get_action("hello") is not None
    assert "hello" in engine.list_actions()


def test_engine_register_automation():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = engine.register_automation(
        name="Test Automation",
        action="hello",
    )

    automation = engine.get_automation(
        automation_id
    )

    assert automation is not None
    assert automation["name"] == "Test Automation"
    assert automation["action"] == "hello"
    assert automation["enabled"] is True


def test_engine_execute_automation():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello from Ultron",
    )

    automation_id = engine.register_automation(
        name="Hello Automation",
        action="hello",
    )

    result = engine.execute(
        automation_id
    )

    assert result == "Hello from Ultron"

    automation = engine.get_automation(
        automation_id
    )

    assert automation["last_run"] is not None
    assert automation["last_result"] == (
        "Hello from Ultron"
    )


def test_engine_execute_with_parameters():
    engine = AutomationEngine()

    engine.register_action(
        "echo",
        lambda message: message,
    )

    automation_id = engine.register_automation(
        name="Echo Automation",
        action="echo",
        parameters={
            "message": "Ultron v0.34",
        },
    )

    result = engine.execute(
        automation_id
    )

    assert result == "Ultron v0.34"


def test_engine_disable_automation():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = engine.register_automation(
        name="Test",
        action="hello",
    )

    assert engine.disable_automation(
        automation_id
    ) is True

    automation = engine.get_automation(
        automation_id
    )

    assert automation["enabled"] is False

    with pytest.raises(
        AutomationExecutionError
    ):
        engine.execute(automation_id)


def test_engine_enable_automation():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = engine.register_automation(
        name="Test",
        action="hello",
    )

    engine.disable_automation(
        automation_id
    )

    assert engine.enable_automation(
        automation_id
    ) is True

    assert engine.execute(
        automation_id
    ) == "Hello"


def test_engine_invalid_action():
    engine = AutomationEngine()

    with pytest.raises(
        AutomationValidationError
    ):
        engine.register_automation(
            name="Invalid Automation",
            action="unknown_action",
        )


def test_engine_missing_automation():
    engine = AutomationEngine()

    with pytest.raises(
        AutomationExecutionError
    ):
        engine.execute(
            "invalid-automation-id"
        )


def test_engine_delete_automation():
    engine = AutomationEngine()

    engine.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = engine.register_automation(
        name="Delete Test",
        action="hello",
    )

    assert engine.delete_automation(
        automation_id
    ) is True

    assert engine.get_automation(
        automation_id
    ) is None


# ============================================================
# Automation Manager Tests
# ============================================================

def test_manager_create_and_run():
    manager = AutomationManager()

    manager.register_action(
        "hello",
        lambda: "Manager working",
    )

    automation_id = manager.create_automation(
        name="Manager Test",
        action="hello",
    )

    assert manager.run(
        automation_id
    ) == "Manager working"


def test_manager_status():
    manager = AutomationManager()

    manager.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = manager.create_automation(
        name="Status Test",
        action="hello",
    )

    assert (
        manager.status(automation_id)
        == "enabled"
    )

    manager.disable(
        automation_id
    )

    assert (
        manager.status(automation_id)
        == "disabled"
    )

    manager.enable(
        automation_id
    )

    assert (
        manager.status(automation_id)
        == "enabled"
    )


def test_manager_delete():
    manager = AutomationManager()

    manager.register_action(
        "hello",
        lambda: "Hello",
    )

    automation_id = manager.create_automation(
        name="Delete Test",
        action="hello",
    )

    assert manager.delete(
        automation_id
    ) is True

    assert manager.get_automation(
        automation_id
    ) is None


def test_manager_list_automations():
    manager = AutomationManager()

    manager.register_action(
        "hello",
        lambda: "Hello",
    )

    first = manager.create_automation(
        name="First",
        action="hello",
    )

    second = manager.create_automation(
        name="Second",
        action="hello",
    )

    automations = manager.list_automations()

    ids = [
        automation["id"]
        for automation in automations
    ]

    assert first in ids
    assert second in ids
    assert len(automations) == 2