from .base import AIProvider


class MockProvider(AIProvider):
    """
    Mock AI provider for development and testing.
    """

    def generate(
        self,
        prompt,
        context=None,
        max_tokens=1024
    ):
        """
        Return a simulated AI response without using an API.
        """

        if not prompt or not prompt.strip():
            return "Mock AI: Prompt cannot be empty."

        return (
            "Mock AI response 🤖\n"
            f"Prompt received: {prompt}"
        )