"""
Ultron Mock AI Provider.

Version: v0.71

Development and testing implementation of the
AIProvider abstraction.

This provider performs no external API calls.
"""

from __future__ import annotations

from .base import AIProvider


class MockProvider(AIProvider):
    """
    Mock AI provider for development and testing.
    """

    DEFAULT_CAPABILITIES = {
        "text_generation",
        "chat",
    }

    def __init__(
        self,
        *,
        name: str = "mock",
        capabilities: set[str] | None = None,
        configuration: dict | None = None,
        metadata: dict | None = None,
    ) -> None:
        super().__init__(
            name=name,
            capabilities=(
                capabilities
                if capabilities is not None
                else self.DEFAULT_CAPABILITIES
            ),
            configuration=configuration,
            metadata=metadata,
        )

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """
        Return a simulated AI response.
        """

        self.validate_availability()

        validated_prompt = self.validate_prompt(
            prompt
        )

        return (
            "Mock AI response 🤖\n"
            f"Prompt received: {validated_prompt}"
        )


__all__ = [
    "MockProvider",
]