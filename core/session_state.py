"""
Ultron Session State
Feature #8 — Session Goals & State

This module manages the active session state
without replacing the existing conversation context.
"""

from datetime import datetime


# ============================================================
# SESSION STATE
# ============================================================

_session_state = {
    "goal": None,
    "status": "idle",
    "context": {},
    "started_at": None,
    "updated_at": None,
    # Conversation-state compatibility fields.
    # These are shared with core.conversation so there is
    # only one source of truth for session information.
    "topic": None,
    "entity": None,
    "intent": None,
    "technology": None,
    "pending_question": None,
}


# ============================================================
# SESSION START
# ============================================================

def start_session(goal=None):
    """
    Start a new Ultron session.

    A new session resets the session-specific context
    while preserving the module itself.
    """

    now = datetime.now().isoformat(timespec="seconds")

    _session_state["goal"] = goal
    _session_state["status"] = "active"
    _session_state["context"] = {}
    _session_state["started_at"] = now
    _session_state["updated_at"] = now
    _session_state["topic"] = None
    _session_state["entity"] = None
    _session_state["intent"] = None
    _session_state["technology"] = None
    _session_state["pending_question"] = None

    return get_session_state()


# ============================================================
# SESSION STATE
# ============================================================

def get_session_state():
    """
    Return a safe copy of the current session state.

    A copy is returned so callers cannot accidentally
    modify the internal session state directly.
    """

    return {
        "goal": _session_state["goal"],
        "status": _session_state["status"],
        "context": _session_state["context"].copy(),
        "started_at": _session_state["started_at"],
        "updated_at": _session_state["updated_at"],
        "topic": _session_state["topic"],
        "entity": _session_state["entity"],
        "intent": _session_state["intent"],
        "technology": _session_state["technology"],
        "pending_question": _session_state["pending_question"],
    }


# ============================================================
# GENERIC STATE UPDATE
# ============================================================

def update_session_state(key, value):
    """
    Update a valid session-state field.

    Returns:
        True  -> update successful
        False -> invalid key
    """

    if key not in _session_state:
        return False

    if key == "context":
        if not isinstance(value, dict):
            return False

        _session_state["context"] = value.copy()

    else:
        _session_state[key] = value

    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# GOAL MANAGEMENT
# ============================================================

def set_goal(goal):
    """
    Set or update the current session goal.
    """

    if goal is None:
        return False

    goal = str(goal).strip()

    if not goal:
        return False

    _session_state["goal"] = goal
    _session_state["status"] = "active"
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


def get_goal():
    """
    Return the current session goal.
    """

    return _session_state["goal"]


def clear_goal():
    """
    Clear the current session goal.

    The session itself remains available,
    but its active goal is removed.
    """

    _session_state["goal"] = None

    if not _session_state["context"]:
        _session_state["status"] = "idle"

    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# SESSION STATUS
# ============================================================

def get_session_status():
    """
    Return the current session status.
    """

    return _session_state["status"]


def set_session_status(status):
    """
    Set the current session status.
    """

    if status is None:
        return False

    status = str(status).strip().lower()

    allowed_statuses = [
        "idle",
        "active",
        "paused",
        "completed",
    ]

    if status not in allowed_statuses:
        return False

    _session_state["status"] = status
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# CONTEXT MANAGEMENT
# ============================================================

def update_context(key, value):
    """
    Add or update contextual information
    for the current session.
    """

    if key is None:
        return False

    key = str(key).strip()

    if not key:
        return False

    _session_state["context"][key] = value
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


def get_context(key=None):
    """
    Return session context.

    If key is provided, return only that value.
    Otherwise return the complete context.
    """

    if key is None:
        return _session_state["context"].copy()

    return _session_state["context"].get(key)


def remove_context(key):
    """
    Remove a specific context value.
    """

    if key not in _session_state["context"]:
        return False

    del _session_state["context"][key]

    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


def clear_context():
    """
    Clear all session context.
    """

    _session_state["context"] = {}
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# SESSION TIMESTAMPS
# ============================================================

def get_started_at():
    """
    Return the session start timestamp.
    """

    return _session_state["started_at"]


def get_updated_at():
    """
    Return the last session update timestamp.
    """

    return _session_state["updated_at"]


# ============================================================
# SESSION ACTIVE CHECK
# ============================================================

def is_session_active():
    """
    Check whether the current session is active.
    """

    return _session_state["status"] == "active"


# ============================================================
# SESSION PAUSE / RESUME
# ============================================================

def pause_session():
    """
    Pause the current session.
    """

    if _session_state["status"] != "active":
        return False

    _session_state["status"] = "paused"
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


def resume_session():
    """
    Resume a paused session.
    """

    if _session_state["status"] != "paused":
        return False

    _session_state["status"] = "active"
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# SESSION COMPLETE
# ============================================================

def complete_session():
    """
    Mark the current session as completed.
    """

    _session_state["status"] = "completed"
    _session_state["updated_at"] = datetime.now().isoformat(
        timespec="seconds"
    )

    return True


# ============================================================
# CLEAR SESSION
# ============================================================

def clear_session():
    """
    Reset the complete session state.
    """

    _session_state["goal"] = None
    _session_state["status"] = "idle"
    _session_state["context"] = {}
    _session_state["started_at"] = None
    _session_state["updated_at"] = None
    _session_state["topic"] = None
    _session_state["entity"] = None
    _session_state["intent"] = None
    _session_state["technology"] = None
    _session_state["pending_question"] = None

    return True


# ============================================================
# SESSION SUMMARY
# ============================================================

def get_session_summary():
    """
    Return a compact summary of the current session.
    """

    return {
        "goal": _session_state["goal"],
        "status": _session_state["status"],
        "context_keys": list(
            _session_state["context"].keys()
        ),
        "started_at": _session_state["started_at"],
        "updated_at": _session_state["updated_at"],
    }


# ============================================================
# DEBUG DISPLAY
# ============================================================

def print_session_state():
    """
    Print the current session state.
    """

    state = get_session_state()

    print("\n===== SESSION STATE =====")
    print(f"Goal: {state['goal']}")
    print(f"Status: {state['status']}")
    print(f"Context: {state['context']}")
    print(f"Started At: {state['started_at']}")
    print(f"Updated At: {state['updated_at']}")
    print("=========================")