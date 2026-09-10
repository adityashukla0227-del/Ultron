"""
Tests for the Ultron AI Engine.

Version: v0.71
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.ai_engine import (
    generate_ai_response,
    get_ai_provider,
)
from core.providers.anthropic_provider import (
    AnthropicProvider,
)
from core.providers.base import AIProvider
from core.providers.mock import MockProvider


class TestAIProviderSelection:
    """Test configured AI provider selection."""

    def test_default_provider_is_mock(
        self,
        monkeypatch,
    ):
        monkeypatch.delenv(
            "AI_MODE",
            raising=False,
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            MockProvider,
        )

    def test_mock_mode_returns_mock_provider(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "mock",
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            MockProvider,
        )

    def test_mock_mode_is_case_insensitive(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "  MOCK  ",
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            MockProvider,
        )

    def test_anthropic_mode_returns_anthropic_provider(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "anthropic",
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            AnthropicProvider,
        )

    def test_anthropic_mode_is_case_insensitive(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "  ANTHROPIC  ",
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            AnthropicProvider,
        )

    @pytest.mark.parametrize(
        "mode",
        [
            "unknown",
            "openai",
            "gemini",
            "",
            "invalid",
        ],
    )
    def test_unknown_mode_falls_back_to_mock(
        self,
        monkeypatch,
        mode,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            mode,
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            MockProvider,
        )

    def test_selected_provider_implements_ai_provider(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "mock",
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            AIProvider,
        )


class TestAIGeneration:
    """Test AI response generation delegation."""

    def test_generate_ai_response_uses_mock_provider(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "mock",
        )

        result = generate_ai_response(
            prompt="Hello Ultron"
        )

        assert result == (
            "Mock AI response 🤖\n"
            "Prompt received: Hello Ultron"
        )

    def test_generate_ai_response_forwards_prompt(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        provider.generate.return_value = (
            "generated response"
        )

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: provider,
        )

        result = generate_ai_response(
            prompt="Build Ultron"
        )

        assert result == "generated response"

        provider.generate.assert_called_once_with(
            prompt="Build Ultron",
            context=None,
            max_tokens=1024,
        )

    def test_generate_ai_response_forwards_context(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        provider.generate.return_value = (
            "context response"
        )

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: provider,
        )

        result = generate_ai_response(
            prompt="Continue",
            context="Previous conversation",
        )

        assert result == "context response"

        provider.generate.assert_called_once_with(
            prompt="Continue",
            context="Previous conversation",
            max_tokens=1024,
        )

    def test_generate_ai_response_forwards_max_tokens(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        provider.generate.return_value = (
            "limited response"
        )

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: provider,
        )

        result = generate_ai_response(
            prompt="Hello",
            max_tokens=256,
        )

        assert result == "limited response"

        provider.generate.assert_called_once_with(
            prompt="Hello",
            context=None,
            max_tokens=256,
        )

    def test_generate_ai_response_forwards_all_arguments(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        provider.generate.return_value = (
            "complete response"
        )

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: provider,
        )

        result = generate_ai_response(
            prompt="Build an AI agent",
            context="User wants modular architecture",
            max_tokens=512,
        )

        assert result == "complete response"

        provider.generate.assert_called_once_with(
            prompt="Build an AI agent",
            context="User wants modular architecture",
            max_tokens=512,
        )

    def test_generate_ai_response_returns_provider_result(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        expected = "provider generated result"

        provider.generate.return_value = expected

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: provider,
        )

        result = generate_ai_response(
            prompt="Hello"
        )

        assert result is expected

    def test_generate_ai_response_rejects_invalid_provider(
        self,
        monkeypatch,
    ):
        invalid_provider = object()

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            lambda: invalid_provider,
        )

        with pytest.raises(TypeError):
            generate_ai_response(
                prompt="Hello"
            )

    def test_generate_ai_response_does_not_create_direct_ai_client(
        self,
        monkeypatch,
    ):
        provider = MagicMock(
            spec=AIProvider
        )

        provider.generate.return_value = (
            "mocked response"
        )

        get_provider = MagicMock(
            return_value=provider
        )

        monkeypatch.setattr(
            "core.ai_engine.get_ai_provider",
            get_provider,
        )

        result = generate_ai_response(
            prompt="Hello"
        )

        assert result == "mocked response"
        get_provider.assert_called_once()
        provider.generate.assert_called_once()


class TestAIEngineIntegration:
    """Test AI engine provider selection integration."""

    def test_anthropic_selection_does_not_require_api_call(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "anthropic",
        )
        monkeypatch.delenv(
            "ANTHROPIC_API_KEY",
            raising=False,
        )

        provider = get_ai_provider()

        assert isinstance(
            provider,
            AnthropicProvider,
        )

        assert provider.is_available() is False

    def test_mock_provider_can_generate_through_engine(
        self,
        monkeypatch,
    ):
        monkeypatch.setenv(
            "AI_MODE",
            "mock",
        )

        result = generate_ai_response(
            prompt="Test engine"
        )

        assert isinstance(
            result,
            str,
        )
        assert (
            "Prompt received: Test engine"
            in result
        )