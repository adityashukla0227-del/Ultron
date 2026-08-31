"""
Ultron Multimodal Input Router.

v0.51 — Multimodal Input Foundation

Routes standardized multimodal inputs to registered
handlers based on their input type.

Responsibilities:
- Register input handlers.
- Remove input handlers.
- Resolve handlers by input type.
- Route MultimodalInput instances.
- Return standardized MultimodalInputResult objects.
- Keep routing separate from modality processing.

Architecture:

    User / Device
          |
          v
    MultimodalInput
          |
          v
     InputRouter
      /   |   |   \
     /    |   |    \
  Text  Voice Vision Gesture
   |      |     |      |
 Handler Handler Handler Handler
          |
          v
 MultimodalInputResult
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict

from modules.multimodal.input import (
    MultimodalInput,
)
from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.input_type import (
    InputType,
)


class InputRouterError(Exception):
    """Base exception for input router errors."""


class InputHandlerNotFoundError(InputRouterError):
    """Raised when no handler exists for an input type."""


class InputHandlerAlreadyRegisteredError(InputRouterError):
    """Raised when a handler is already registered."""


class InputRouter:
    """
    Routes multimodal inputs to registered handlers.

    The router does not understand how text, voice, vision,
    or gesture data is processed. It only selects and invokes
    the appropriate registered handler.

    A handler receives the normalized input data:

        multimodal_input.data

    and may return:

        - MultimodalInputResult
        - Any other value, which will be wrapped automatically
          into a successful MultimodalInputResult.
    """

    def __init__(
        self,
        *,
        handlers: Dict[
            str | InputType,
            Callable[
                [Any],
                Any,
            ],
        ]
        | None = None,
    ) -> None:
        """
        Initialize the input router.

        Parameters:
            handlers:
                Optional mapping of input types to handlers.
        """

        self._handlers: Dict[
            InputType,
            Callable[
                [Any],
                Any,
            ],
        ] = {}

        if handlers is not None:
            if not isinstance(
                handlers,
                dict,
            ):
                raise InputRouterError(
                    "handlers must be a dictionary or None."
                )

            for input_type, handler in handlers.items():
                self.register_handler(
                    input_type,
                    handler,
                )

    # ========================================================
    # Handler Registration
    # ========================================================

    def register_handler(
        self,
        input_type: str | InputType,
        handler: Callable[
            [Any],
            Any,
        ],
    ) -> None:
        """
        Register a handler for an input type.

        Registering an existing input type replaces its
        previously registered handler.
        """

        normalized_type = self._normalize_input_type(
            input_type
        )

        if normalized_type is InputType.UNKNOWN:
            raise InputRouterError(
                "UNKNOWN input type cannot have a handler."
            )

        if not callable(handler):
            raise InputRouterError(
                "handler must be callable."
            )

        self._handlers[normalized_type] = handler

    def unregister_handler(
        self,
        input_type: str | InputType,
    ) -> bool:
        """
        Remove a handler for an input type.

        Returns:
            True when a handler was removed.
            False when no handler was registered.
        """

        normalized_type = self._normalize_input_type(
            input_type
        )

        if normalized_type is InputType.UNKNOWN:
            return False

        if normalized_type not in self._handlers:
            return False

        del self._handlers[normalized_type]

        return True

    def replace_handler(
        self,
        input_type: str | InputType,
        handler: Callable[
            [Any],
            Any,
        ],
    ) -> None:
        """
        Replace or register a handler for an input type.
        """

        normalized_type = self._normalize_input_type(
            input_type
        )

        if normalized_type is InputType.UNKNOWN:
            raise InputRouterError(
                "UNKNOWN input type cannot have a handler."
            )

        if not callable(handler):
            raise InputRouterError(
                "handler must be callable."
            )

        self._handlers[normalized_type] = handler

    # ========================================================
    # Handler Lookup
    # ========================================================

    def has_handler(
        self,
        input_type: str | InputType,
    ) -> bool:
        """
        Return True when a handler is registered.
        """

        normalized_type = self._normalize_input_type(
            input_type
        )

        if normalized_type is InputType.UNKNOWN:
            return False

        return normalized_type in self._handlers

    def get_handler(
        self,
        input_type: str | InputType,
    ) -> Callable[
        [Any],
        Any,
    ] | None:
        """
        Return the registered handler.

        Returns:
            The registered handler when available.
            None when no handler is registered.

        Raises:
            InputHandlerNotFoundError:
                When the input type is UNKNOWN.
        """

        normalized_type = self._normalize_input_type(
            input_type
        )

        if normalized_type is InputType.UNKNOWN:
            raise InputHandlerNotFoundError(
                "No handler exists for UNKNOWN input type."
            )

        return self._handlers.get(
            normalized_type
        )

    def get_registered_types(self) -> list[str]:
        """
        Return registered input type names.
        """

        return [
            input_type.value
            for input_type in self._handlers
        ]

    def get_handler_count(self) -> int:
        """Return the number of registered handlers."""

        return len(
            self._handlers
        )

    # ========================================================
    # Routing
    # ========================================================

    def route(
        self,
        multimodal_input: MultimodalInput,
    ) -> MultimodalInputResult:
        """
        Route a multimodal input to its registered handler.

        The handler receives multimodal_input.data.

        Handler failures are converted into a failed
        MultimodalInputResult instead of escaping directly.
        """

        if not isinstance(
            multimodal_input,
            MultimodalInput,
        ):
            raise InputRouterError(
                "route() requires a MultimodalInput instance."
            )

        input_id = multimodal_input.id

        handler = self.get_handler(
            multimodal_input.input_type
        )

        if handler is None:
            return MultimodalInputResult(
                input_id=input_id,
                input_type=multimodal_input.input_type,
                status="failed",
                error=(
                    f"No handler registered for "
                    f"{multimodal_input.input_type.value}."
                ),
            )

        result = MultimodalInputResult(
            input_id=input_id,
            input_type=multimodal_input.input_type,
            status="processing",
        )

        try:
            handler_result = handler(
                multimodal_input.data
            )

            if isinstance(
                handler_result,
                MultimodalInputResult,
            ):
                return handler_result

            result.complete(
                handler_result
            )

            return result

        except Exception as exc:
            result.fail(
                str(exc)
            )

            return result

    def route_or_raise(
        self,
        multimodal_input: MultimodalInput,
    ) -> MultimodalInputResult:
        """
        Route an input and raise handler errors.

        Unlike route(), this method allows processing
        exceptions to propagate.
        """

        if not isinstance(
            multimodal_input,
            MultimodalInput,
        ):
            raise InputRouterError(
                "route_or_raise() requires a "
                "MultimodalInput instance."
            )

        handler = self.get_handler(
            multimodal_input.input_type
        )

        if handler is None:
            raise InputHandlerNotFoundError(
                f"No handler registered for "
                f"{multimodal_input.input_type.value}."
            )

        handler_result = handler(
            multimodal_input.data
        )

        if isinstance(
            handler_result,
            MultimodalInputResult,
        ):
            return handler_result

        result = MultimodalInputResult(
            input_id=multimodal_input.id,
            input_type=multimodal_input.input_type,
            status="processing",
        )

        result.complete(
            handler_result
        )

        return result

    # ========================================================
    # Batch Routing
    # ========================================================

    def route_many(
        self,
        inputs: list[MultimodalInput],
    ) -> list[MultimodalInputResult]:
        """
        Route multiple multimodal inputs.

        Each input is processed independently.
        """

        if not isinstance(
            inputs,
            list,
        ):
            raise InputRouterError(
                "inputs must be a list."
            )

        results: list[
            MultimodalInputResult
        ] = []

        for multimodal_input in inputs:
            results.append(
                self.route(
                    multimodal_input
                )
            )

        return results

    # ========================================================
    # Router State
    # ========================================================

    def clear_handlers(self) -> None:
        """Remove all registered handlers."""

        self._handlers.clear()

    def get_handlers(self) -> Dict[
        InputType,
        Callable[
            [Any],
            Any,
        ],
    ]:
        """
        Return a defensive copy of the handler registry.
        """

        return deepcopy(
            self._handlers
        )

    # ========================================================
    # Input Type Helpers
    # ========================================================

    @staticmethod
    def _normalize_input_type(
        input_type: str | InputType,
    ) -> InputType:
        """
        Normalize an input type into InputType.
        """

        try:
            return InputType.from_value(
                input_type
            )
        except (
            ValueError,
            TypeError,
        ) as exc:
            raise InputRouterError(
                f"Invalid input type: {input_type!r}"
            ) from exc

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        registered = [
            input_type.value
            for input_type in self._handlers
        ]

        return (
            "InputRouter("
            f"handlers={registered!r}"
            ")"
        )


__all__ = [
    "InputRouter",
    "InputRouterError",
    "InputHandlerNotFoundError",
    "InputHandlerAlreadyRegisteredError",
]