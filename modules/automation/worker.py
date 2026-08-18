"""
Ultron Automation Worker
Version: v0.34

Runs the automation runner periodically in a background thread.

The worker is intentionally separated from the scheduler and runner:

Scheduler -> decides WHEN
Runner    -> decides WHAT to execute
Worker    -> decides WHEN to CHECK
"""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

from modules.automation.runner import AutomationRunner


class AutomationWorker:
    """
    Background worker for scheduled automations.

    The worker can also be used manually through run_once()
    without starting a background thread.
    """

    def __init__(
        self,
        runner: AutomationRunner,
        interval_seconds: float = 60.0,
    ) -> None:

        if interval_seconds <= 0:
            raise ValueError(
                "interval_seconds must be greater than 0."
            )

        self.runner = runner

        self.interval_seconds = float(
            interval_seconds
        )

        self._stop_event = threading.Event()

        self._thread: Optional[
            threading.Thread
        ] = None

        self._lock = threading.Lock()

        self._running = False

        self._last_results: List[
            Dict[str, Any]
        ] = []

        self._last_error: Optional[str] = None

    # ========================================================
    # Properties
    # ========================================================

    @property
    def running(self) -> bool:
        """
        Return whether the worker is currently running.
        """

        with self._lock:
            return self._running

    @property
    def last_results(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return the latest successful execution results.

        Empty scheduler cycles do not erase the previous
        successful results.
        """

        with self._lock:
            return list(
                self._last_results
            )

    @property
    def last_error(self) -> Optional[str]:
        """
        Return the latest worker error.
        """

        with self._lock:
            return self._last_error

    # ========================================================
    # Single Cycle
    # ========================================================

    def run_once(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Execute one scheduler check.

        This method does not start a background thread.

        Returns:
            List of execution results.
        """

        try:

            results = self.runner.run_due()

            with self._lock:

                # Only replace the stored results when
                # an automation was actually executed.
                #
                # This prevents a later empty scheduler
                # cycle from erasing the previous result.
                if results:
                    self._last_results = list(
                        results
                    )

                self._last_error = None

            return results

        except Exception as exc:

            with self._lock:
                self._last_error = str(exc)

            return []

    # ========================================================
    # Background Loop
    # ========================================================

    def _run_loop(self) -> None:
        """
        Internal background worker loop.
        """

        while not self._stop_event.is_set():

            self.run_once()

            self._stop_event.wait(
                self.interval_seconds
            )

        with self._lock:
            self._running = False

    # ========================================================
    # Start
    # ========================================================

    def start(self) -> bool:
        """
        Start the background worker.

        Returns:
            True  -> worker started
            False -> worker was already running
        """

        with self._lock:

            if self._running:
                return False

            self._stop_event.clear()

            self._thread = threading.Thread(
                target=self._run_loop,
                name="UltronAutomationWorker",
                daemon=True,
            )

            self._running = True

            self._thread.start()

            return True

    # ========================================================
    # Stop
    # ========================================================

    def stop(
        self,
        timeout: Optional[float] = 5.0,
    ) -> bool:
        """
        Stop the background worker.

        Returns:
            True  -> worker stopped
            False -> worker was not running
        """

        with self._lock:

            if not self._running:
                return False

            self._stop_event.set()

            thread = self._thread

        if thread is not None:

            thread.join(
                timeout=timeout
            )

        with self._lock:

            self._running = False
            self._thread = None

        return True

    # ========================================================
    # Status
    # ========================================================

    def status(self) -> Dict[str, Any]:
        """
        Return worker status information.
        """

        with self._lock:

            return {
                "running": self._running,
                "interval_seconds": (
                    self.interval_seconds
                ),
                "last_results": list(
                    self._last_results
                ),
                "last_error": self._last_error,
            }

    # ========================================================
    # Context Manager
    # ========================================================

    def __enter__(self):
        """
        Start worker when entering context.
        """

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        """
        Stop worker when leaving context.
        """

        self.stop()