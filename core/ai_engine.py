"""
Ultron AI Engine.

Version: v0.72

Coordinates AI provider selection and response generation.

Responsibilities:
- Resolve the configured AI provider
- Maintain supported provider registry
- Preserve provider abstraction
- Delegate generation to the selected provider
- Preserve backward-compatible AI Engine behavior

The AI Engine does NOT:
- Build intelligence results
- Determine intent
- Select tools
- Create execution plans
- Execute agents
"""

from __future__ import annotations

import os

from core.providers.anthropic_provider import AnthropicProvider
from core.providers.base import AIProvider, AIProviderError
from core.providers.mock import MockProvider


SUPPORTED_PROVIDERS: dict[str, type[AIProvider]] = {
    "mock": MockProvider,
    "anthropic": AnthropicProvider,
}


def get_ai_provider() -> AIProvider:
    """
    Return the configured AI provider.

    Supported providers:
    - mock
    - anthropic

    Unknown or empty provider modes fall back to MockProvider
    to preserve backward-compatible AI Engine behavior.
    """

    mode = (
        os.getenv(
            "AI_MODE",
            "mock",
        )
        .strip()
        .lower()
    )

    provider_class = SUPPORTED_PROVIDERS.get(
        mode,
        MockProvider,
    )

    provider = provider_class()

    if not isinstance(provider, AIProvider):
        raise TypeError(
            "Configured AI provider must implement AIProvider."
        )

    return provider


def generate_ai_response(
    prompt: str,
    context: str | None = None,
    max_tokens: int = 1024,
) -> str:
    """
    Generate an AI response using the configured provider.

    Provider-level validation errors are converted into
    backward-compatible response strings for callers of
    the existing AI Engine API.
    """

    provider = get_ai_provider()

    if not isinstance(provider, AIProvider):
        raise TypeError(
            "Configured AI provider must implement AIProvider."
        )

    try:
        return provider.generate(
            prompt=prompt,
            context=context,
            max_tokens=max_tokens,
        )

    except AIProviderError as error:
        return str(error).capitalize()


__all__ = [
    "SUPPORTED_PROVIDERS",
    "get_ai_provider",
    "generate_ai_response",
]