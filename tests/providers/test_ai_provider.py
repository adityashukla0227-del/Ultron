"""
Tests for the Ultron AIProvider abstraction.

Version: v0.71
"""

from __future__ import annotations

import pytest

from core.providers.base import (
    AIProvider,
    AIProviderError,
)


class ConcreteAIProvider(AIProvider):
    """
    Minimal concrete provider used to test the abstract contract.
    """

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.pop("name", "test-provider"),
            capabilities=kwargs.pop(
                "capabilities",
                {"text_generation", "chat"},
            ),
            configuration=kwargs.pop(
                "configuration",
                {"model": "test-model"},
            ),
            metadata=kwargs.pop(
                "metadata",
                {"environment": "test"},
            ),
        )

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        return f"generated: {prompt}"


def test_ai_provider_is_abstract():
    with pytest.raises(TypeError):
        AIProvider(
            name="test-provider"
        )


def test_ai_provider_initialization():
    provider = ConcreteAIProvider(
        name=" Test Provider ",
        capabilities=[
            "Text_Generation",
            "CHAT",
        ],
        configuration={
            "model": "test-model",
        },
        metadata={
            "environment": "test",
        },
    )

    assert provider.get_name() == "Test Provider"
    assert provider.get_capabilities() == {
        "text_generation",
        "chat",
    }


@pytest.mark.parametrize(
    "invalid_name",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_ai_provider_rejects_invalid_name(
    invalid_name,
):
    with pytest.raises(AIProviderError):
        ConcreteAIProvider(
            name=invalid_name
        )


def test_ai_provider_rejects_invalid_capabilities():
    with pytest.raises(AIProviderError):
        ConcreteAIProvider(
            capabilities="chat"
        )

    with pytest.raises(AIProviderError):
        ConcreteAIProvider(
            capabilities=["chat", 123]
        )


def test_ai_provider_rejects_empty_capability():
    with pytest.raises(AIProviderError):
        ConcreteAIProvider(
            capabilities=["chat", "   "]
        )


def test_ai_provider_capabilities_are_defensive():
    capabilities = [
        "chat",
        "text_generation",
    ]

    provider = ConcreteAIProvider(
        capabilities=capabilities
    )

    capabilities.append("vision")

    assert provider.get_capabilities() == {
        "chat",
        "text_generation",
    }

    returned = provider.get_capabilities()
    returned.add("vision")

    assert provider.get_capabilities() == {
        "chat",
        "text_generation",
    }


def test_ai_provider_supports_capability():
    provider = ConcreteAIProvider(
        capabilities={
            "chat",
            "text_generation",
        }
    )

    assert provider.supports_capability("chat")
    assert provider.supports_capability(
        "CHAT"
    )
    assert not provider.supports_capability(
        "vision"
    )


@pytest.mark.parametrize(
    "invalid_capability",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_ai_provider_rejects_invalid_capability_query(
    invalid_capability,
):
    provider = ConcreteAIProvider()

    with pytest.raises(AIProviderError):
        provider.supports_capability(
            invalid_capability
        )


def test_ai_provider_configuration():
    provider = ConcreteAIProvider(
        configuration={
            "model": "test-model",
            "nested": {
                "enabled": True,
            },
        }
    )

    assert provider.get_configuration(
        "model"
    ) == "test-model"

    assert provider.get_configuration(
        "missing",
        "fallback",
    ) == "fallback"


def test_ai_provider_configuration_is_defensive():
    configuration = {
        "nested": {
            "value": 10,
        }
    }

    provider = ConcreteAIProvider(
        configuration=configuration
    )

    configuration["nested"]["value"] = 20

    assert provider.get_configuration(
        "nested"
    ) == {
        "value": 10,
    }

    returned = provider.get_configuration(
        "nested"
    )

    returned["value"] = 30

    assert provider.get_configuration(
        "nested"
    ) == {
        "value": 10,
    }


def test_ai_provider_set_configuration():
    provider = ConcreteAIProvider()

    provider.set_configuration(
        "temperature",
        0.7,
    )

    assert provider.get_configuration(
        "temperature"
    ) == 0.7


def test_ai_provider_set_configuration_is_defensive():
    provider = ConcreteAIProvider()

    value = {
        "enabled": True,
    }

    provider.set_configuration(
        "settings",
        value,
    )

    value["enabled"] = False

    assert provider.get_configuration(
        "settings"
    ) == {
        "enabled": True,
    }


def test_ai_provider_all_configuration_is_defensive():
    provider = ConcreteAIProvider()

    configuration = (
        provider.get_all_configuration()
    )

    configuration["model"] = "changed"

    assert provider.get_configuration(
        "model"
    ) == "test-model"


@pytest.mark.parametrize(
    "invalid_key",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_ai_provider_rejects_invalid_configuration_key(
    invalid_key,
):
    provider = ConcreteAIProvider()

    with pytest.raises(AIProviderError):
        provider.get_configuration(
            invalid_key
        )


def test_ai_provider_metadata():
    provider = ConcreteAIProvider(
        metadata={
            "environment": "test",
            "version": "0.71",
        }
    )

    assert provider.get_metadata(
        "environment"
    ) == "test"

    assert provider.get_metadata(
        "missing",
        "fallback",
    ) == "fallback"


def test_ai_provider_metadata_is_defensive():
    provider = ConcreteAIProvider(
        metadata={
            "nested": {
                "enabled": True,
            }
        }
    )

    metadata = provider.get_metadata(
        "nested"
    )

    metadata["enabled"] = False

    assert provider.get_metadata(
        "nested"
    ) == {
        "enabled": True,
    }


def test_ai_provider_set_metadata():
    provider = ConcreteAIProvider()

    provider.set_metadata(
        "version",
        "0.71",
    )

    assert provider.get_metadata(
        "version"
    ) == "0.71"


def test_ai_provider_all_metadata_is_defensive():
    provider = ConcreteAIProvider()

    metadata = provider.get_all_metadata()

    metadata["environment"] = "production"

    assert provider.get_metadata(
        "environment"
    ) == "test"


def test_ai_provider_available_by_default():
    provider = ConcreteAIProvider()

    assert provider.is_available()
    provider.validate_availability()


def test_ai_provider_validate_prompt():
    provider = ConcreteAIProvider()

    assert provider.validate_prompt(
        "  Hello Ultron  "
    ) == "Hello Ultron"


@pytest.mark.parametrize(
    "invalid_prompt",
    [
        None,
        "",
        "   ",
        123,
    ],
)
def test_ai_provider_rejects_invalid_prompt(
    invalid_prompt,
):
    provider = ConcreteAIProvider()

    with pytest.raises(AIProviderError):
        provider.validate_prompt(
            invalid_prompt
        )


def test_ai_provider_generate_contract():
    provider = ConcreteAIProvider()

    result = provider.generate(
        prompt="Hello"
    )

    assert result == "generated: Hello"


def test_ai_provider_repr():
    provider = ConcreteAIProvider(
        name="test-provider",
        capabilities={
            "chat",
            "text_generation",
        },
    )

    representation = repr(provider)

    assert "ConcreteAIProvider" in representation
    assert "test-provider" in representation
    assert "chat" in representation