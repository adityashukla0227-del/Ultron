"""
Ultron AI Provider Registry.

Version: v0.94

Central registry for AI provider implementations.

Responsibilities:
- Register provider classes
- Unregister provider classes
- Retrieve provider classes
- Check provider existence
- List registered providers
- Create provider instances

The ProviderRegistry does NOT:
- Generate AI responses
- Execute providers
- Manage API credentials
- Determine provider permissions
- Modify the AIProvider contract
"""

from __future__ import annotations

from typing import Type

from .base import AIProvider


class AIProviderRegistryError(Exception):
    """Raised when provider registry operations fail."""


class AIProviderRegistry:
    """
    Central registry for AIProvider implementations.
    """

    def __init__(
        self,
        providers: dict[str, Type[AIProvider]] | None = None,
    ) -> None:
        self._providers: dict[str, Type[AIProvider]] = {}

        for name, provider_class in (providers or {}).items():
            self.register(name, provider_class)

    @staticmethod
    def _validate_name(name: str) -> str:
        if not isinstance(name, str):
            raise AIProviderRegistryError(
                "Provider name must be a string."
            )

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise AIProviderRegistryError(
                "Provider name must be a non-empty string."
            )

        return normalized_name

    @staticmethod
    def _validate_provider_class(
        provider_class: Type[AIProvider],
    ) -> None:
        if not isinstance(provider_class, type):
            raise AIProviderRegistryError(
                "Provider must be a class."
            )

        if not issubclass(provider_class, AIProvider):
            raise AIProviderRegistryError(
                "Provider must inherit from AIProvider."
            )

    def register(
        self,
        name: str,
        provider_class: Type[AIProvider],
    ) -> bool:
        """
        Register an AI provider class.
        """

        normalized_name = self._validate_name(name)

        self._validate_provider_class(
            provider_class
        )

        if normalized_name in self._providers:
            return False

        self._providers[
            normalized_name
        ] = provider_class

        return True

    def unregister(
        self,
        name: str,
    ) -> bool:
        """
        Unregister an AI provider.
        """

        normalized_name = self._validate_name(name)

        if normalized_name not in self._providers:
            return False

        del self._providers[
            normalized_name
        ]

        return True

    def get(
        self,
        name: str,
    ) -> Type[AIProvider] | None:
        """
        Return a registered provider class.
        """

        normalized_name = self._validate_name(name)

        return self._providers.get(
            normalized_name
        )

    def has(
        self,
        name: str,
    ) -> bool:
        """
        Check whether a provider is registered.
        """

        normalized_name = self._validate_name(name)

        return normalized_name in self._providers

    def list_providers(
        self,
    ) -> list[Type[AIProvider]]:
        """
        Return all registered provider classes.
        """

        return list(
            self._providers.values()
        )

    def list_provider_names(
        self,
    ) -> list[str]:
        """
        Return all registered provider names.
        """

        return list(
            self._providers.keys()
        )

    def create(
        self,
        provider_name: str,
        **kwargs,
    ) -> AIProvider:
        """
        Create an instance of a registered provider.
        """

        provider_class = self.get(
            provider_name
        )

        if provider_class is None:
            raise AIProviderRegistryError(
                f"AI provider '{provider_name}' is not registered."
            )

        provider = provider_class(
            **kwargs
        )

        if not isinstance(
            provider,
            AIProvider,
        ):
            raise AIProviderRegistryError(
                "Registered provider must create "
                "an AIProvider instance."
            )

        return provider

    def clear(self) -> None:
        """
        Remove all registered providers.
        """

        self._providers.clear()

    def count(self) -> int:
        """
        Return the number of registered providers.
        """

        return len(self._providers)

    def __len__(self) -> int:
        return self.count()

    def __contains__(
        self,
        name: str,
    ) -> bool:
        return self.has(name)

    def __repr__(self) -> str:
        return (
            "AIProviderRegistry("
            f"providers="
            f"{self.list_provider_names()}"
            ")"
        )


__all__ = [
    "AIProviderRegistry",
    "AIProviderRegistryError",
]