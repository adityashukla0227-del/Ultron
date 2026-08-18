from pathlib import Path

import pytest

from modules.automation.storage import AutomationStorage


@pytest.fixture
def storage(tmp_path: Path) -> AutomationStorage:
    return AutomationStorage(
        tmp_path / "automations.json"
    )


# ========================================================
# Initialization
# ========================================================


def test_storage_creates_file(tmp_path):
    path = tmp_path / "automations.json"

    storage = AutomationStorage(path)

    assert storage.exists()
    assert storage.path() == str(path)


def test_storage_initial_data(storage):
    data = storage.load_all()

    assert data == {
        "automations": [],
        "schedules": [],
    }


# ========================================================
# Automation Operations
# ========================================================


def test_save_automation(storage):
    automation = {
        "id": "auto-1",
        "name": "Test Automation",
        "action": "hello",
    }

    result = storage.save_automation(automation)

    assert result == automation
    assert storage.get_automation("auto-1") == automation


def test_get_missing_automation(storage):
    assert storage.get_automation("missing") is None


def test_list_automations(storage):
    storage.save_automation(
        {
            "id": "auto-1",
            "name": "First",
            "action": "hello",
        }
    )

    storage.save_automation(
        {
            "id": "auto-2",
            "name": "Second",
            "action": "echo",
        }
    )

    automations = storage.list_automations()

    assert len(automations) == 2
    assert automations[0]["id"] == "auto-1"
    assert automations[1]["id"] == "auto-2"


def test_save_automation_updates_existing(storage):
    storage.save_automation(
        {
            "id": "auto-1",
            "name": "Old Name",
            "action": "hello",
        }
    )

    storage.save_automation(
        {
            "id": "auto-1",
            "name": "New Name",
            "action": "echo",
        }
    )

    automations = storage.list_automations()

    assert len(automations) == 1
    assert automations[0]["name"] == "New Name"
    assert automations[0]["action"] == "echo"


def test_delete_automation(storage):
    storage.save_automation(
        {
            "id": "auto-1",
            "name": "Test",
            "action": "hello",
        }
    )

    assert storage.delete_automation("auto-1") is True
    assert storage.get_automation("auto-1") is None


def test_delete_missing_automation(storage):
    assert storage.delete_automation("missing") is False


# ========================================================
# Schedule Operations
# ========================================================


def test_save_schedule(storage):
    schedule = {
        "id": "schedule-1",
        "automation_id": "auto-1",
        "enabled": True,
        "recurring": False,
    }

    result = storage.save_schedule(schedule)

    assert result == schedule
    assert storage.get_schedule("schedule-1") == schedule


def test_get_missing_schedule(storage):
    assert storage.get_schedule("missing") is None


def test_list_schedules(storage):
    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
            "enabled": True,
        }
    )

    storage.save_schedule(
        {
            "id": "schedule-2",
            "automation_id": "auto-2",
            "enabled": False,
        }
    )

    schedules = storage.list_schedules()

    assert len(schedules) == 2
    assert schedules[0]["id"] == "schedule-1"
    assert schedules[1]["id"] == "schedule-2"


def test_save_schedule_updates_existing(storage):
    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
            "enabled": True,
        }
    )

    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
            "enabled": False,
        }
    )

    schedules = storage.list_schedules()

    assert len(schedules) == 1
    assert schedules[0]["enabled"] is False


def test_delete_schedule(storage):
    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
        }
    )

    assert storage.delete_schedule("schedule-1") is True
    assert storage.get_schedule("schedule-1") is None


def test_delete_missing_schedule(storage):
    assert storage.delete_schedule("missing") is False


# ========================================================
# Bulk Operations
# ========================================================


def test_save_all(storage):
    automations = [
        {
            "id": "auto-1",
            "name": "First",
            "action": "hello",
        },
        {
            "id": "auto-2",
            "name": "Second",
            "action": "echo",
        },
    ]

    schedules = [
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
            "enabled": True,
        },
    ]

    storage.save_all(
        automations,
        schedules,
    )

    data = storage.load_all()

    assert data["automations"] == automations
    assert data["schedules"] == schedules


def test_load_all(storage):
    storage.save_automation(
        {
            "id": "auto-1",
            "name": "Test",
            "action": "hello",
        }
    )

    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
        }
    )

    data = storage.load_all()

    assert len(data["automations"]) == 1
    assert len(data["schedules"]) == 1


def test_clear(storage):
    storage.save_automation(
        {
            "id": "auto-1",
            "name": "Test",
            "action": "hello",
        }
    )

    storage.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
        }
    )

    storage.clear()

    assert storage.list_automations() == []
    assert storage.list_schedules() == []


# ========================================================
# Error Handling
# ========================================================


def test_save_automation_requires_id(storage):
    with pytest.raises(ValueError):
        storage.save_automation(
            {
                "name": "Missing ID",
                "action": "hello",
            }
        )


def test_save_schedule_requires_id(storage):
    with pytest.raises(ValueError):
        storage.save_schedule(
            {
                "automation_id": "auto-1",
            }
        )


def test_invalid_automation_type(storage):
    with pytest.raises(TypeError):
        storage.save_automation("invalid")


def test_invalid_schedule_type(storage):
    with pytest.raises(TypeError):
        storage.save_schedule("invalid")


def test_corrupted_json_is_recovered(storage):
    path = Path(storage.path())

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    assert storage.load_all() == {
        "automations": [],
        "schedules": [],
    }


def test_invalid_root_data_is_recovered(storage):
    path = Path(storage.path())

    path.write_text(
        "[]",
        encoding="utf-8",
    )

    assert storage.load_all() == {
        "automations": [],
        "schedules": [],
    }


# ========================================================
# Persistence
# ========================================================


def test_data_survives_new_storage_instance(tmp_path):
    path = tmp_path / "automations.json"

    first = AutomationStorage(path)

    first.save_automation(
        {
            "id": "auto-1",
            "name": "Persistent Automation",
            "action": "hello",
        }
    )

    first.save_schedule(
        {
            "id": "schedule-1",
            "automation_id": "auto-1",
            "enabled": True,
        }
    )

    second = AutomationStorage(path)

    assert second.get_automation("auto-1") == {
        "id": "auto-1",
        "name": "Persistent Automation",
        "action": "hello",
    }

    assert second.get_schedule("schedule-1") == {
        "id": "schedule-1",
        "automation_id": "auto-1",
        "enabled": True,
    }