"""
Ultron AI Provider Abstraction.

Version: v0.71

Provider-agnostic contract for all Ultron AI providers.

Responsibilities:
- Define provider identity
- Define provider capabilities
- Manage provider configuration
- Manage provider metadata
- Validate provider availability
- Validate AI prompts
- Define the abstract AI generation contract

The AIProvider abstraction does NOT:
- Build AI context
- Determine user intent
- Select tools
- Create execution plans
- Execute agents
- Execute tools

Those responsibilities belong to higher Ultron layers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any


class AIProviderError(Exception):
    """
    Base exception for AI provider errors.
    """


class AIProvider(ABC):
    """
    Base abstraction for all Ultron AI providers.
    """

    def __init__(
        self,
        *,
        name: str,
        capabilities: list[str] | set[str] | None = None,
        configuration: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self._name = self._validate_name(name)

        self._capabilities = (
            self._normalize_string_set(
                capabilities,
                "capabilities",
            )
        )

        self._configuration = (
            self._validate_dictionary(
                configuration,
                "configuration",
            )
        )

        self._metadata = (
            self._validate_dictionary(
                metadata,
                "metadata",
            )
        )

    # ========================================================
    # Validation Helpers
    # ========================================================

    @staticmethod
    def _validate_name(name: Any) -> str:
        if not isinstance(name, str):
            raise AIProviderError(
                "name must be a non-empty string."
            )

        normalized_name = name.strip()

        if not normalized_name:
            raise AIProviderError(
                "name must be a non-empty string."
            )

        return normalized_name

    @staticmethod
    def _normalize_string_set(
        values: list[str] | set[str] | None,
        field_name: str,
    ) -> set[str]:
        if values is None:
            return set()

        if isinstance(values, str):
            raise AIProviderError(
                f"{field_name} must be a collection of strings."
            )

        if not isinstance(
            values,
            (list, set, tuple),
        ):
            raise AIProviderError(
                f"{field_name} must be a collection of strings."
            )

        normalized: set[str] = set()

        for value in values:
            if not isinstance(value, str):
                raise AIProviderError(
                    f"{field_name} must contain only strings."
                )

            normalized_value = value.strip().lower()

            if not normalized_value:
                raise AIProviderError(
                    f"{field_name} cannot contain empty values."
                )

            normalized.add(normalized_value)

        return normalized

    @staticmethod
    def _validate_dictionary(
        value: dict[str, Any] | None,
        field_name: str,
    ) -> dict[str, Any]:
        if value is None:
            return {}

        if not isinstance(value, dict):
            raise AIProviderError(
                f"{field_name} must be a dictionary."
            )

        return deepcopy(value)

    @staticmethod
    def _validate_key(
        key: Any,
        field_name: str,
    ) -> str:
        if not isinstance(key, str):
            raise AIProviderError(
                f"{field_name} must be a non-empty string."
            )

        normalized_key = key.strip()

        if not normalized_key:
            raise AIProviderError(
                f"{field_name} must be a non-empty string."
            )

        return normalized_key

    # ========================================================
    # Identity
    # ========================================================

    def get_name(self) -> str:
        """
        Return the provider name.
        """
        return self._name

    # ========================================================
    # Capabilities
    # ========================================================

    def supports_capability(
        self,
        capability: str,
    ) -> bool:
        """
        Check whether the provider supports a capability.
        """

        if not isinstance(capability, str):
            raise AIProviderError(
                "capability must be a non-empty string."
            )

        normalized_capability = (
            capability.strip().lower()
        )

        if not normalized_capability:
            raise AIProviderError(
                "capability must be a non-empty string."
            )

        return (
            normalized_capability
            in self._capabilities
        )

    def get_capabilities(self) -> set[str]:
        """
        Return a defensive copy of provider capabilities.
        """

        return set(self._capabilities)

    # ========================================================
    # Configuration
    # ========================================================

    def get_configuration(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a provider configuration value.
        """

        normalized_key = self._validate_key(
            key,
            "configuration key",
        )

        return deepcopy(
            self._configuration.get(
                normalized_key,
                default,
            )
        )

    def set_configuration(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a provider configuration value.
        """

        normalized_key = self._validate_key(
            key,
            "configuration key",
        )

        self._configuration[
            normalized_key
        ] = deepcopy(value)

    def get_all_configuration(self) -> dict[str, Any]:
        """
        Return a defensive copy of all configuration.
        """

        return deepcopy(
            self._configuration
        )

    # ========================================================
    # Metadata
    # ========================================================

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Return a provider metadata value.
        """

        normalized_key = self._validate_key(
            key,
            "metadata key",
        )

        return deepcopy(
            self._metadata.get(
                normalized_key,
                default,
            )
        )

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a provider metadata value.
        """

        normalized_key = self._validate_key(
            key,
            "metadata key",
        )

        self._metadata[
            normalized_key
        ] = deepcopy(value)

    def get_all_metadata(self) -> dict[str, Any]:
        """
        Return a defensive copy of all metadata.
        """

        return deepcopy(
            self._metadata
        )

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the provider is currently available.

        Base providers are considered available by default.
        Concrete providers may override this behavior.
        """

        return True

    def validate_availability(self) -> None:
        """
        Validate provider availability.
        """

        if not self.is_available():
            raise AIProviderError(
                f"AI provider '{self.get_name()}' "
                "is not available."
            )

    # ========================================================
    # Prompt Validation
    # ========================================================

    def validate_prompt(
        self,
        prompt: Any,
    ) -> str:
        """
        Validate and normalize an AI prompt.
        """

        if not isinstance(prompt, str):
            raise AIProviderError(
                "prompt must be a string."
            )

        normalized_prompt = prompt.strip()

        if not normalized_prompt:
            raise AIProviderError(
                "prompt cannot be empty."
            )

        return normalized_prompt

    # ========================================================
    # AI Generation Contract
    # ========================================================

    @abstractmethod
    def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate an AI response.

        Args:
            prompt:
                User request.

            context:
                Optional conversation/context information.

            max_tokens:
                Maximum response token limit.

        Returns:
            Generated AI response as a string.
        """

        raise NotImplementedError

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.get_name()!r}, "
            f"capabilities={self.get_capabilities()!r}"
            ")"
        )


__all__ = [
    "AIProvider",
    "AIProviderError",
]