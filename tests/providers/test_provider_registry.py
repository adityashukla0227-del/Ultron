"""
Tests for the Ultron AI Provider Registry.

Version: v0.94
"""

import pytest

from core.providers.anthropic_provider import AnthropicProvider
from core.providers.base import AIProvider
from core.providers.mock import MockProvider
from core.providers.registry import (
    AIProviderRegistry,
    AIProviderRegistryError,
)


class CustomProvider(AIProvider):
    """Test provider implementation."""

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        return "custom"


def test_registry_starts_empty() -> None:
    registry = AIProviderRegistry()

    assert registry.count() == 0
    assert len(registry) == 0
    assert registry.list_provider_names() == []


def test_register_provider() -> None:
    registry = AIProviderRegistry()

    result = registry.register(
        "mock",
        MockProvider,
    )

    assert result is True
    assert registry.has("mock")
    assert registry.get("mock") is MockProvider


def test_register_provider_normalizes_name() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "  MOCK  ",
        MockProvider,
    )

    assert registry.has("mock")
    assert registry.get("mock") is MockProvider


def test_duplicate_registration_returns_false() -> None:
    registry = AIProviderRegistry()

    assert registry.register(
        "mock",
        MockProvider,
    ) is True

    assert registry.register(
        "mock",
        AnthropicProvider,
    ) is False

    assert registry.get("mock") is MockProvider


def test_unregister_provider() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    assert registry.unregister("mock") is True
    assert registry.has("mock") is False
    assert registry.get("mock") is None


def test_unregister_missing_provider_returns_false() -> None:
    registry = AIProviderRegistry()

    assert registry.unregister("missing") is False


def test_get_missing_provider_returns_none() -> None:
    registry = AIProviderRegistry()

    assert registry.get("missing") is None


def test_list_provider_names() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )
    registry.register(
        "anthropic",
        AnthropicProvider,
    )

    assert registry.list_provider_names() == [
        "mock",
        "anthropic",
    ]


def test_list_providers() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )
    registry.register(
        "anthropic",
        AnthropicProvider,
    )

    assert registry.list_providers() == [
        MockProvider,
        AnthropicProvider,
    ]


def test_create_provider() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    provider = registry.create("mock")

    assert isinstance(provider, MockProvider)
    assert isinstance(provider, AIProvider)
    assert provider.get_name() == "mock"


def test_create_provider_with_kwargs() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "custom",
        CustomProvider,
    )

    provider = registry.create(
        "custom",
        name="custom-instance",
        capabilities={"text_generation"},
    )

    assert isinstance(provider, CustomProvider)
    assert provider.get_name() == "custom-instance"


def test_create_missing_provider_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="not registered",
    ):
        registry.create("missing")


def test_register_invalid_name_type_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="Provider name",
    ):
        registry.register(
            123,
            MockProvider,
        )


def test_register_empty_name_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="non-empty",
    ):
        registry.register(
            "   ",
            MockProvider,
        )


def test_get_invalid_name_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="Provider name",
    ):
        registry.get(123)


def test_has_invalid_name_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="Provider name",
    ):
        registry.has(123)


def test_unregister_invalid_name_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="Provider name",
    ):
        registry.unregister(123)


def test_register_non_class_provider_raises() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="must be a class",
    ):
        registry.register(
            "invalid",
            MockProvider(),
        )


def test_register_non_ai_provider_raises() -> None:
    class NotAProvider:
        pass

    registry = AIProviderRegistry()

    with pytest.raises(
        AIProviderRegistryError,
        match="AIProvider",
    ):
        registry.register(
            "invalid",
            NotAProvider,
        )


def test_constructor_registers_providers() -> None:
    registry = AIProviderRegistry(
        {
            "mock": MockProvider,
            "anthropic": AnthropicProvider,
        }
    )

    assert registry.count() == 2
    assert registry.has("mock")
    assert registry.has("anthropic")


def test_constructor_rejects_invalid_provider() -> None:
    with pytest.raises(
        AIProviderRegistryError,
        match="AIProvider",
    ):
        AIProviderRegistry(
            {
                "invalid": object,
            }
        )


def test_clear_registry() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )
    registry.register(
        "anthropic",
        AnthropicProvider,
    )

    registry.clear()

    assert registry.count() == 0
    assert registry.list_provider_names() == []


def test_count_and_contains() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    assert registry.count() == 1
    assert len(registry) == 1
    assert "mock" in registry
    assert "missing" not in registry


def test_registry_repr() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    representation = repr(registry)

    assert "AIProviderRegistry" in representation
    assert "mock" in representation


def test_list_results_do_not_mutate_registry() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    provider_names = registry.list_provider_names()
    provider_names.append("fake")

    providers = registry.list_providers()
    providers.clear()

    assert registry.count() == 1
    assert registry.has("mock")


def test_provider_instances_are_independent() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    first = registry.create("mock")
    second = registry.create("mock")

    assert first is not second


def test_contains_uses_normalized_name() -> None:
    registry = AIProviderRegistry()

    registry.register(
        "mock",
        MockProvider,
    )

    assert " MOCK " in registry