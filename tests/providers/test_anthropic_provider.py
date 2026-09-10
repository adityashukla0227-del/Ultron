"""
Tests for the Ultron Anthropic AI Provider.

Version: v0.71
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.providers.anthropic_provider import (
    AnthropicProvider,
)
from core.providers.base import (
    AIProvider,
)


def create_mock_client(
    response_text="Claude test response",
    content=True,
):
    client = MagicMock()

    response = SimpleNamespace(
        content=(
            [
                SimpleNamespace(
                    text=response_text
                )
            ]
            if content
            else []
        )
    )

    client.messages.create.return_value = response

    return client


class TestAnthropicProviderInitialization:
    """Test provider initialization and configuration."""

    def test_provider_initializes_without_api_key(
        self,
        monkeypatch,
    ):
        monkeypatch.delenv(
            "ANTHROPIC_API_KEY",
            raising=False,
        )

        provider = AnthropicProvider()

        assert provider.get_name() == "anthropic"
        assert provider.is_available() is False

    def test_provider_is_ai_provider(self):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert isinstance(
            provider,
            AIProvider,
        )

    def test_provider_uses_default_model(
        self,
    ):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert (
            provider.get_configuration("model")
            == AnthropicProvider.DEFAULT_MODEL
        )

    def test_provider_accepts_custom_model(self):
        provider = AnthropicProvider(
            client=MagicMock(),
            model="custom-model",
        )

        assert (
            provider.get_configuration("model")
            == "custom-model"
        )

    def test_provider_accepts_custom_name(self):
        provider = AnthropicProvider(
            client=MagicMock(),
            name="custom-anthropic",
        )

        assert (
            provider.get_name()
            == "custom-anthropic"
        )

    def test_provider_has_default_capabilities(
        self,
    ):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert provider.get_capabilities() == {
            "text_generation",
            "chat",
            "context_generation",
        }

    def test_provider_supports_text_generation(
        self,
    ):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert provider.supports_capability(
            "text_generation"
        )

    def test_provider_supports_chat(self):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert provider.supports_capability(
            "chat"
        )

    def test_provider_supports_context_generation(
        self,
    ):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert provider.supports_capability(
            "context_generation"
        )

    def test_provider_is_available_with_client(
        self,
    ):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        assert provider.is_available() is True


class TestAnthropicProviderConfiguration:
    """Test provider configuration and metadata."""

    def test_provider_accepts_configuration(self):
        provider = AnthropicProvider(
            client=MagicMock(),
            configuration={
                "temperature": 0.5,
            },
        )

        assert (
            provider.get_configuration(
                "temperature"
            )
            == 0.5
        )

        assert (
            provider.get_configuration("model")
            == AnthropicProvider.DEFAULT_MODEL
        )

    def test_provider_accepts_metadata(self):
        provider = AnthropicProvider(
            client=MagicMock(),
            metadata={
                "environment": "test",
                "version": "0.71",
            },
        )

        assert (
            provider.get_metadata(
                "environment"
            )
            == "test"
        )

        assert (
            provider.get_metadata("version")
            == "0.71"
        )

    def test_provider_configuration_is_defensive(
        self,
    ):
        configuration = {
            "nested": {
                "enabled": True,
            }
        }

        provider = AnthropicProvider(
            client=MagicMock(),
            configuration=configuration,
        )

        configuration["nested"]["enabled"] = False

        assert provider.get_configuration(
            "nested"
        ) == {
            "enabled": True,
        }


class TestAnthropicProviderGeneration:
    """Test Anthropic generation behavior."""

    def test_generate_returns_response_text(self):
        client = create_mock_client(
            response_text="Hello from Claude"
        )

        provider = AnthropicProvider(
            client=client
        )

        result = provider.generate(
            "Hello Ultron"
        )

        assert result == "Hello from Claude"

    def test_generate_calls_messages_create(
        self,
    ):
        client = create_mock_client(
            response_text="Generated response"
        )

        provider = AnthropicProvider(
            client=client
        )

        provider.generate(
            "Hello Ultron"
        )

        client.messages.create.assert_called_once()

        call_kwargs = (
            client.messages.create.call_args.kwargs
        )

        assert (
            call_kwargs["model"]
            == AnthropicProvider.DEFAULT_MODEL
        )

        assert call_kwargs["max_tokens"] == 1024

        assert call_kwargs["messages"] == [
            {
                "role": "user",
                "content": "Hello Ultron",
            }
        ]

    def test_generate_uses_custom_model(self):
        client = create_mock_client()

        provider = AnthropicProvider(
            client=client,
            model="custom-model",
        )

        provider.generate(
            "Hello"
        )

        call_kwargs = (
            client.messages.create.call_args.kwargs
        )

        assert (
            call_kwargs["model"]
            == "custom-model"
        )

    def test_generate_uses_custom_max_tokens(
        self,
    ):
        client = create_mock_client()

        provider = AnthropicProvider(
            client=client
        )

        provider.generate(
            "Hello",
            max_tokens=256,
        )

        call_kwargs = (
            client.messages.create.call_args.kwargs
        )

        assert (
            call_kwargs["max_tokens"]
            == 256
        )

    def test_generate_includes_context(self):
        client = create_mock_client()

        provider = AnthropicProvider(
            client=client
        )

        provider.generate(
            prompt="What should I do?",
            context="User prefers concise answers.",
        )

        call_kwargs = (
            client.messages.create.call_args.kwargs
        )

        sent_prompt = (
            call_kwargs["messages"][0]["content"]
        )

        assert (
            "User prefers concise answers."
            in sent_prompt
        )

        assert (
            "What should I do?"
            in sent_prompt
        )

        assert (
            "Use this context when relevant."
            in sent_prompt
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
        client = create_mock_client()

        provider = AnthropicProvider(
            client=client
        )

        with pytest.raises(Exception):
            provider.generate(
                invalid_prompt
            )

        client.messages.create.assert_not_called()

    def test_generate_when_provider_unavailable(
        self,
        monkeypatch,
    ):
        monkeypatch.delenv(
            "ANTHROPIC_API_KEY",
            raising=False,
        )

        provider = AnthropicProvider()

        result = provider.generate(
            "Hello Ultron"
        )

        assert result == (
            "Anthropic AI is not configured. "
            "Please add a valid Anthropic API key."
        )

    def test_generate_empty_response(self):
        client = create_mock_client(
            content=False
        )

        provider = AnthropicProvider(
            client=client
        )

        result = provider.generate(
            "Hello"
        )

        assert (
            result
            == "Claude returned an empty response."
        )

    def test_generate_handles_api_error(self):
        client = MagicMock()

        error = Exception(
            "simulated API failure"
        )

        client.messages.create.side_effect = (
            error
        )

        provider = AnthropicProvider(
            client=client
        )

        result = provider.generate(
            "Hello"
        )

        assert (
            "AI request failed:"
            in result
        )

    def test_generate_does_not_make_real_api_call(
        self,
    ):
        client = create_mock_client()

        provider = AnthropicProvider(
            client=client
        )

        provider.generate(
            "Test request"
        )

        assert (
            client.messages.create.call_count
            == 1
        )


class TestAnthropicProviderRepresentation:
    """Test provider representation."""

    def test_repr_contains_provider_name(self):
        provider = AnthropicProvider(
            client=MagicMock()
        )

        representation = repr(provider)

        assert "AnthropicProvider" in representation
        assert "anthropic" in representation