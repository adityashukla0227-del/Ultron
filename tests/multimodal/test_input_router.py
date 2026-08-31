"""
Ultron Multimodal Input Router Tests.

v0.51 — Multimodal Input Foundation
"""

from __future__ import annotations

import pytest

from modules.multimodal.input import (
    MultimodalInput,
    MultimodalInputError,
)
from modules.multimodal.input_result import (
    InputResult,
    InputResultError,
)
from modules.multimodal.input_router import (
    InputRouter,
    InputRouterError,
)
from modules.multimodal.input_type import InputType


# ========================================================
# Helpers
# ========================================================


def create_input(
    input_type: InputType = InputType.TEXT,
    data="hello",
):
    return MultimodalInput(
        input_type=input_type,
        data=data,
        source="test",
    )


def create_result(
    input_type: InputType = InputType.TEXT,
):
    return InputResult(
        input_id="input-1",
        input_type=input_type,
        success=True,
        data="processed",
    )


# ========================================================
# Initialization
# ========================================================


def test_router_can_be_created():
    router = InputRouter()

    assert isinstance(router, InputRouter)


def test_router_has_empty_handlers():
    router = InputRouter()

    assert router.get_registered_types() == []


def test_router_initializes_with_handlers():
    router = InputRouter(
        handlers={
            InputType.TEXT: lambda value: value,
        }
    )

    assert InputType.TEXT in router.get_registered_types()


# ========================================================
# Handler Registration
# ========================================================


def test_register_handler():
    router = InputRouter()

    handler = lambda value: value

    router.register_handler(
        InputType.TEXT,
        handler,
    )

    assert router.has_handler(InputType.TEXT)


def test_register_multiple_handlers():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    router.register_handler(
        InputType.VOICE,
        lambda value: value,
    )

    router.register_handler(
        InputType.VISION,
        lambda value: value,
    )

    assert router.has_handler(InputType.TEXT)
    assert router.has_handler(InputType.VOICE)
    assert router.has_handler(InputType.VISION)


def test_register_handler_replaces_existing_handler():
    router = InputRouter()

    first = lambda value: "first"
    second = lambda value: "second"

    router.register_handler(
        InputType.TEXT,
        first,
    )

    router.register_handler(
        InputType.TEXT,
        second,
    )

    result = router.route(
        create_input(
            InputType.TEXT
        )
    )

    assert result.success is True
    assert result.data == "second"


def test_register_handler_rejects_invalid_type():
    router = InputRouter()

    with pytest.raises(InputRouterError):
        router.register_handler(
            "invalid",
            lambda value: value,
        )


def test_register_handler_rejects_unknown_type():
    router = InputRouter()

    with pytest.raises(InputRouterError):
        router.register_handler(
            InputType.UNKNOWN,
            lambda value: value,
        )


def test_register_handler_rejects_non_callable():
    router = InputRouter()

    with pytest.raises(InputRouterError):
        router.register_handler(
            InputType.TEXT,
            "not callable",
        )


# ========================================================
# Handler Lookup
# ========================================================


def test_get_handler_returns_registered_handler():
    router = InputRouter()

    handler = lambda value: value

    router.register_handler(
        InputType.TEXT,
        handler,
    )

    assert router.get_handler(
        InputType.TEXT
    ) is handler


def test_get_handler_returns_none_for_missing_handler():
    router = InputRouter()

    assert router.get_handler(
        InputType.TEXT
    ) is None


def test_has_handler_returns_false_for_missing_handler():
    router = InputRouter()

    assert router.has_handler(
        InputType.TEXT
    ) is False


def test_has_handler_returns_true_for_registered_handler():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    assert router.has_handler(
        InputType.TEXT
    ) is True


# ========================================================
# Handler Removal
# ========================================================


def test_unregister_handler():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    removed = router.unregister_handler(
        InputType.TEXT
    )

    assert removed is True
    assert router.has_handler(
        InputType.TEXT
    ) is False


def test_unregister_missing_handler_returns_false():
    router = InputRouter()

    assert router.unregister_handler(
        InputType.TEXT
    ) is False


# ========================================================
# Registered Types
# ========================================================


def test_get_registered_types():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    router.register_handler(
        InputType.VOICE,
        lambda value: value,
    )

    registered = router.get_registered_types()

    assert InputType.TEXT in registered
    assert InputType.VOICE in registered


def test_registered_types_are_defensive():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    registered = router.get_registered_types()

    registered.clear()

    assert router.has_handler(
        InputType.TEXT
    )


# ========================================================
# Routing
# ========================================================


def test_route_text_input():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: f"processed:{value}",
    )

    result = router.route(
        create_input(
            InputType.TEXT,
            "hello",
        )
    )

    assert isinstance(
        result,
        InputResult,
    )

    assert result.success is True
    assert result.data == "processed:hello"


def test_route_voice_input():
    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        lambda value: "voice processed",
    )

    result = router.route(
        create_input(
            InputType.VOICE,
            b"audio",
        )
    )

    assert result.success is True
    assert result.data == "voice processed"


def test_route_vision_input():
    router = InputRouter()

    router.register_handler(
        InputType.VISION,
        lambda value: "vision processed",
    )

    result = router.route(
        create_input(
            InputType.VISION,
            "image-data",
        )
    )

    assert result.success is True
    assert result.data == "vision processed"


def test_route_gesture_input():
    router = InputRouter()

    router.register_handler(
        InputType.GESTURE,
        lambda value: "gesture processed",
    )

    result = router.route(
        create_input(
            InputType.GESTURE,
            {"gesture": "wave"},
        )
    )

    assert result.success is True
    assert result.data == "gesture processed"


def test_route_passes_input_data_to_handler():
    router = InputRouter()

    received = []

    def handler(data):
        received.append(data)
        return "ok"

    router.register_handler(
        InputType.TEXT,
        handler,
    )

    input_data = create_input(
        InputType.TEXT,
        "hello",
    )

    router.route(input_data)

    assert received == ["hello"]


def test_route_returns_input_id():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: "ok",
    )

    input_data = create_input(
        InputType.TEXT
    )

    result = router.route(
        input_data
    )

    assert result.input_id == input_data.id


def test_route_returns_input_type():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: "ok",
    )

    result = router.route(
        create_input(InputType.TEXT)
    )

    assert result.input_type is InputType.TEXT


# ========================================================
# Missing Handler
# ========================================================


def test_route_without_handler_returns_failure():
    router = InputRouter()

    result = router.route(
        create_input(InputType.TEXT)
    )

    assert isinstance(
        result,
        InputResult,
    )

    assert result.success is False


def test_route_without_handler_contains_error():
    router = InputRouter()

    result = router.route(
        create_input(InputType.TEXT)
    )

    assert result.success is False
    assert result.error is not None


# ========================================================
# Handler Exceptions
# ========================================================


def test_handler_exception_returns_failure():
    router = InputRouter()

    def handler(value):
        raise RuntimeError("handler failed")

    router.register_handler(
        InputType.TEXT,
        handler,
    )

    result = router.route(
        create_input(InputType.TEXT)
    )

    assert result.success is False
    assert result.error is not None


def test_handler_exception_does_not_escape_router():
    router = InputRouter()

    def handler(value):
        raise ValueError("boom")

    router.register_handler(
        InputType.TEXT,
        handler,
    )

    result = router.route(
        create_input(InputType.TEXT)
    )

    assert isinstance(
        result,
        InputResult,
    )

    assert result.success is False


# ========================================================
# Input Validation
# ========================================================


def test_route_requires_multimodal_input():
    router = InputRouter()

    with pytest.raises(InputRouterError):
        router.route("invalid input")


def test_route_rejects_none():
    router = InputRouter()

    with pytest.raises(InputRouterError):
        router.route(None)


# ========================================================
# Routing Isolation
# ========================================================


def test_text_handler_does_not_handle_voice():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: "text",
    )

    result = router.route(
        create_input(
            InputType.VOICE
        )
    )

    assert result.success is False


def test_voice_handler_does_not_handle_vision():
    router = InputRouter()

    router.register_handler(
        InputType.VOICE,
        lambda value: "voice",
    )

    result = router.route(
        create_input(
            InputType.VISION
        )
    )

    assert result.success is False


# ========================================================
# Clear
# ========================================================


def test_clear_handlers():
    router = InputRouter()

    router.register_handler(
        InputType.TEXT,
        lambda value: value,
    )

    router.register_handler(
        InputType.VOICE,
        lambda value: value,
    )

    router.clear_handlers()

    assert router.get_registered_types() == []


def test_clear_handlers_removes_all_handlers():
    router = InputRouter()

    for input_type in (
        InputType.TEXT,
        InputType.VOICE,
        InputType.VISION,
        InputType.GESTURE,
    ):
        router.register_handler(
            input_type,
            lambda value: value,
        )

    router.clear_handlers()

    for input_type in (
        InputType.TEXT,
        InputType.VOICE,
        InputType.VISION,
        InputType.GESTURE,
    ):
        assert router.has_handler(
            input_type
        ) is False


# ========================================================
# Representation
# ========================================================


def test_router_repr():
    router = InputRouter()

    representation = repr(router)

    assert "InputRouter" in representation


# ========================================================
# Exported Symbols
# ========================================================


def test_router_error_is_exported():
    from modules.multimodal.input_router import __all__

    assert "InputRouter" in __all__
    assert "InputRouterError" in __all__