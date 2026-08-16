import os

from core.providers.mock import MockProvider
from core.providers.anthropic_provider import AnthropicProvider


def get_ai_provider():
    """
    Return the configured AI provider.
    """

    mode = os.getenv("AI_MODE", "mock").lower().strip()

    if mode == "anthropic":
        return AnthropicProvider()

    return MockProvider()


def generate_ai_response(
    prompt,
    context=None,
    max_tokens=1024
):
    """
    Generate an AI response using the configured provider.
    """

    provider = get_ai_provider()

    return provider.generate(
        prompt=prompt,
        context=context,
        max_tokens=max_tokens
    )