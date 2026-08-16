from abc import ABC, abstractmethod


class AIProvider(ABC):
    """
    Base interface for all AI providers.
    """

    @abstractmethod
    def generate(
        self,
        prompt,
        context=None,
        max_tokens=1024
    ):
        """
        Generate an AI response.

        Args:
            prompt (str):
                User request.

            context (str | None):
                Optional conversation context.

            max_tokens (int):
                Maximum response tokens.

        Returns:
            str:
                Generated AI response.
        """
        raise NotImplementedError