"""
Tests for the Ultron Mock AI Provider.

Version: v0.71
"""

from __future__ import annotations

import pytest

from core.providers.base import AIProvider
from core.providers.mock import MockProvider


class TestMockProviderInitialization:
    """Test MockProvider initialization and configuration."""

    def test_provider_initializes_successfully(self):
        provider = MockProvider()

        assert provider.get_name() == "mock"

    def test_provider_is_ai_provider(self):
        provider = MockProvider()

        assert isinstance(provider, AIProvider)

    def test_provider_has_default_capabilities(self):
        provider = MockProvider()

        assert provider.get_capabilities() == {
            "text_generation",
            "chat",
        }

    def test_provider_supports_text_generation(self):
        provider = MockProvider()

        assert provider.supports_capability(
            "text_generation"
        )

    def test_provider_supports_chat(self):
        provider = MockProvider()

        assert provider.supports_capability("chat")

    def test_provider_does_not_support_unknown_capability(self):
        provider = MockProvider()

        assert not provider.supports_capability(
            "vision"
        )

    def test_provider_is_available(self):
        provider = MockProvider()

        assert provider.is_available() is True


class TestMockProviderConfiguration:
    """Test MockProvider configuration and metadata."""

    def test_provider_accepts_custom_name(self):
        provider = MockProvider(
            name="custom-mock"
        )

        assert provider.get_name() == "custom-mock"

    def test_provider_accepts_custom_capabilities(self):
        provider = MockProvider(
            capabilities={
                "chat",
                "text_generation",
                "reasoning",
            }
        )

        assert provider.get_capabilities() == {
            "chat",
            "text_generation",
            "reasoning",
        }

    def test_provider_accepts_configuration(self):
        provider = MockProvider(
            configuration={
                "model": "mock-model",
                "temperature": 0.7,
            }
        )

        assert (
            provider.get_configuration("model")
            == "mock-model"
        )

        assert (
            provider.get_configuration(
                "temperature"
            )
            == 0.7
        )

    def test_provider_accepts_metadata(self):
        provider = MockProvider(
            metadata={
                "environment": "test",
                "version": "0.71",
            }
        )

        assert (
            provider.get_metadata("environment")
            == "test"
        )

        assert (
            provider.get_metadata("version")
            == "0.71"
        )


class TestMockProviderGeneration:
    """Test MockProvider generation behavior."""

    def test_generate_returns_string(self):
        provider = MockProvider()

        result = provider.generate(
            "Hello Ultron"
        )

        assert isinstance(result, str)

    def test_generate_includes_prompt(self):
        provider = MockProvider()

        result = provider.generate(
            "Hello Ultron"
        )

        assert (
            "Prompt received: Hello Ultron"
            in result
        )

    def test_generate_strips_prompt_whitespace(self):
        provider = MockProvider()

        result = provider.generate(
            "   Hello Ultron   "
        )

        assert (
            "Prompt received: Hello Ultron"
            in result
        )

    def test_generate_preserves_existing_behavior(self):
        provider = MockProvider()

        result = provider.generate(
            "Build an AI assistant"
        )

        assert result == (
            "Mock AI response 🤖\n"
            "Prompt received: Build an AI assistant"
        )

    @pytest.mark.parametrize(
        "invalid_prompt",
        [
            None,
            "",
            "   ",
            123,
        ],
    )
    def test_generate_rejects_invalid_prompt(
        self,
        invalid_prompt,
    ):
        provider = MockProvider()

        with pytest.raises(Exception):
            provider.generate(
                invalid_prompt
            )

    def test_generate_accepts_context(self):
        provider = MockProvider()

        result = provider.generate(
            prompt="Hello",
            context="Previous conversation",
        )

        assert isinstance(result, str)

    def test_generate_accepts_max_tokens(self):
        provider = MockProvider()

        result = provider.generate(
            prompt="Hello",
            max_tokens=256,
        )

        assert isinstance(result, str)


class TestMockProviderRepresentation:
    """Test provider representation."""

    def test_repr_contains_provider_name(self):
        provider = MockProvider()

        representation = repr(provider)

        assert "MockProvider" in representation
        assert "mock" in representation