import os

import anthropic

from .base import AIProvider


class AnthropicProvider(AIProvider):
    """
    Anthropic implementation of the AI provider.
    """

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key or self.api_key == "your_api_key_here":
            self.client = None
        else:
            self.client = anthropic.Anthropic(
                api_key=self.api_key
            )

    def generate(
        self,
        prompt,
        context=None,
        max_tokens=1024
    ):
        """
        Generate a response using Claude.
        """

        if not prompt or not prompt.strip():
            return "Prompt cannot be empty."

        if self.client is None:
            return (
                "Anthropic AI is not configured. "
                "Please add a valid Anthropic API key."
            )

        model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-sonnet-5"
        )

        if context:
            prompt = (
                "Here is the relevant context from the conversation:\n\n"
                f"{context}\n\n"
                "Use this context when relevant.\n\n"
                f"User request:\n{prompt}"
            )

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            if response.content:
                return response.content[0].text

            return "Claude returned an empty response."

        except anthropic.APIError as error:
            return f"Claude API error: {error}"

        except Exception as error:
            return f"AI request failed: {error}"