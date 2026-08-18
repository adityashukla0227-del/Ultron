"""
Ultron Automation Storage
Version: v0.35

Persistent storage layer for automation definitions and schedules.

Responsibilities:
- Save automation data
- Load automation data
- Save schedule data
- Load schedule data
- Update stored data
- Delete stored data
- Handle missing/corrupted storage safely
- Windows-safe persistent writes

The storage layer intentionally does not execute automations.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class AutomationStorage:
    """Persistent JSON storage for Ultron automation data."""

    def __init__(
        self,
        file_path: str | Path = "data/automations.json",
    ) -> None:

        self.file_path = Path(file_path)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._ensure_storage()

    # ========================================================
    # Internal Helpers
    # ========================================================

    def _default_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Return the default storage structure."""

        return {
            "automations": [],
            "schedules": [],
        }

    def _ensure_storage(self) -> None:
        """Create storage file when it does not exist."""

        if not self.file_path.exists():
            self._write(
                self._default_data()
            )

    def _read(self) -> Dict[str, Any]:
        """Read storage data safely."""

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

        except (
            FileNotFoundError,
            json.JSONDecodeError,
            OSError,
        ):
            data = self._default_data()

        if not isinstance(data, dict):
            data = self._default_data()

        if not isinstance(
            data.get("automations"),
            list,
        ):
            data["automations"] = []

        if not isinstance(
            data.get("schedules"),
            list,
        ):
            data["schedules"] = []

        return data

    def _write(self, data: Dict[str, Any]) -> None:
        """
        Write storage data safely.

        Uses a unique temporary file and atomic replacement
        where possible. Falls back to a direct write on
        Windows when another process temporarily locks the
        destination file.
        """

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path: Optional[Path] = None

        try:
            # Create a unique temporary file in the same
            # directory so replacement remains on the same
            # filesystem.
            fd, temporary_name = tempfile.mkstemp(
                prefix=f"{self.file_path.stem}_",
                suffix=".tmp",
                dir=str(self.file_path.parent),
            )

            temporary_path = Path(
                temporary_name
            )

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    data,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )
                file.flush()
                os.fsync(file.fileno())

            try:
                os.replace(
                    temporary_path,
                    self.file_path,
                )

                temporary_path = None

            except PermissionError:
                """
                Windows can temporarily deny replacement if
                the destination file is held by another process.

                Fall back to writing the destination directly
                instead of allowing automation persistence to
                fail completely.
                """

                with self.file_path.open(
                    "w",
                    encoding="utf-8",
                ) as file:
                    json.dump(
                        data,
                        file,
                        indent=2,
                        ensure_ascii=False,
                    )
                    file.flush()
                    os.fsync(file.fileno())

        finally:
            if (
                temporary_path is not None
                and temporary_path.exists()
            ):
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    # ========================================================
    # Automation Operations
    # ========================================================

    def save_automation(
        self,
        automation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Save a new or existing automation."""

        if not isinstance(automation, dict):
            raise TypeError(
                "automation must be a dictionary."
            )

        if "id" not in automation:
            raise ValueError(
                "automation must contain an 'id'."
            )

        data = self._read()

        data["automations"] = [
            item
            for item in data["automations"]
            if item.get("id") != automation["id"]
        ]

        data["automations"].append(
            dict(automation)
        )

        self._write(data)

        return dict(automation)

    def get_automation(
        self,
        automation_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return an automation by ID."""

        data = self._read()

        for automation in data["automations"]:
            if automation.get("id") == automation_id:
                return dict(automation)

        return None

    def list_automations(
        self,
    ) -> List[Dict[str, Any]]:
        """Return all stored automations."""

        data = self._read()

        return [
            dict(item)
            for item in data["automations"]
        ]

    def delete_automation(
        self,
        automation_id: str,
    ) -> bool:
        """Delete an automation by ID."""

        data = self._read()

        original_count = len(
            data["automations"]
        )

        data["automations"] = [
            item
            for item in data["automations"]
            if item.get("id") != automation_id
        ]

        deleted = (
            len(data["automations"])
            != original_count
        )

        if deleted:
            self._write(data)

        return deleted

    # ========================================================
    # Schedule Operations
    # ========================================================

    def save_schedule(
        self,
        schedule: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Save a new or existing schedule."""

        if not isinstance(schedule, dict):
            raise TypeError(
                "schedule must be a dictionary."
            )

        if "id" not in schedule:
            raise ValueError(
                "schedule must contain an 'id'."
            )

        data = self._read()

        data["schedules"] = [
            item
            for item in data["schedules"]
            if item.get("id") != schedule["id"]
        ]

        data["schedules"].append(
            dict(schedule)
        )

        self._write(data)

        return dict(schedule)

    def get_schedule(
        self,
        schedule_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Return a schedule by ID."""

        data = self._read()

        for schedule in data["schedules"]:
            if schedule.get("id") == schedule_id:
                return dict(schedule)

        return None

    def list_schedules(
        self,
    ) -> List[Dict[str, Any]]:
        """Return all stored schedules."""

        data = self._read()

        return [
            dict(item)
            for item in data["schedules"]
        ]

    def delete_schedule(
        self,
        schedule_id: str,
    ) -> bool:
        """Delete a schedule by ID."""

        data = self._read()

        original_count = len(
            data["schedules"]
        )

        data["schedules"] = [
            item
            for item in data["schedules"]
            if item.get("id") != schedule_id
        ]

        deleted = (
            len(data["schedules"])
            != original_count
        )

        if deleted:
            self._write(data)

        return deleted

    # ========================================================
    # Bulk Operations
    # ========================================================

    def save_all(
        self,
        automations: List[Dict[str, Any]],
        schedules: List[Dict[str, Any]],
    ) -> None:
        """Replace the complete storage dataset."""

        data = {
            "automations": [
                dict(item)
                for item in automations
            ],
            "schedules": [
                dict(item)
                for item in schedules
            ],
        }

        self._write(data)

    def load_all(
        self,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Load the complete storage dataset."""

        data = self._read()

        return {
            "automations": [
                dict(item)
                for item in data["automations"]
            ],
            "schedules": [
                dict(item)
                for item in data["schedules"]
            ],
        }

    # ========================================================
    # Utility
    # ========================================================

    def clear(self) -> None:
        """Remove all stored automation data."""

        self._write(
            self._default_data()
        )

    def exists(self) -> bool:
        """Return whether the storage file exists."""

        return self.file_path.exists()

    def path(self) -> str:
        """Return the storage file path."""

        return str(self.file_path)