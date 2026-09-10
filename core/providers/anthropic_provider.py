"""
Ultron Anthropic AI Provider.

Version: v0.71

Concrete Anthropic implementation built on top of the
provider-agnostic AIProvider abstraction.

Provider-specific Anthropic API logic remains isolated
inside this module.
"""

from __future__ import annotations

import os
from typing import Any

import anthropic

from .base import AIProvider


class AnthropicProvider(AIProvider):
    """
    Anthropic implementation of the AI provider.

    Responsibilities:
    - Manage Anthropic client configuration
    - Expose provider capabilities
    - Validate provider availability
    - Generate AI responses using Claude
    - Preserve existing Anthropic behavior
    """

    DEFAULT_MODEL = "claude-sonnet-5"

    DEFAULT_CAPABILITIES = {
        "text_generation",
        "chat",
        "context_generation",
    }

    def __init__(
        self,
        *,
        client: Any = None,
        name: str = "anthropic",
        model: str | None = None,
        capabilities: set[str] | None = None,
        configuration: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.api_key = os.getenv(
            "ANTHROPIC_API_KEY"
        )

        if client is not None:
            self.client = client

        elif (
            not self.api_key
            or self.api_key == "your_api_key_here"
        ):
            self.client = None

        else:
            self.client = anthropic.Anthropic(
                api_key=self.api_key
            )

        configured_model = (
            model
            if model is not None
            else os.getenv(
                "ANTHROPIC_MODEL",
                self.DEFAULT_MODEL,
            )
        )

        provider_configuration = dict(
            configuration or {}
        )

        provider_configuration.setdefault(
            "model",
            configured_model,
        )

        super().__init__(
            name=name,
            capabilities=(
                capabilities
                if capabilities is not None
                else self.DEFAULT_CAPABILITIES
            ),
            configuration=provider_configuration,
            metadata=metadata,
        )

    # ========================================================
    # Availability
    # ========================================================

    def is_available(self) -> bool:
        """
        Return whether the Anthropic provider is configured.
        """

        return self.client is not None

    # ========================================================
    # Generation
    # ========================================================

    def generate(
        self,
        prompt: str,
        context: str | None = None,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate a response using Claude.
        """

        validated_prompt = self.validate_prompt(
            prompt
        )

        if self.client is None:
            return (
                "Anthropic AI is not configured. "
                "Please add a valid Anthropic API key."
            )

        model = self.get_configuration(
            "model",
            self.DEFAULT_MODEL,
        )

        if context:
            validated_prompt = (
                "Here is the relevant context "
                "from the conversation:\n\n"
                f"{context}\n\n"
                "Use this context when relevant.\n\n"
                f"User request:\n{validated_prompt}"
            )

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": validated_prompt,
                    }
                ],
            )

            if response.content:
                return response.content[0].text

            return "Claude returned an empty response."

        except anthropic.APIError as error:
            return f"Claude API error: {error}"

        except Exception as error:
            return f"AI request failed: {error}"


__all__ = [
    "AnthropicProvider",
]