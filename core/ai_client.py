import os

from dotenv import load_dotenv
import anthropic


# Load environment variables from .env
load_dotenv()


def get_anthropic_client():
    """
    Create and return an Anthropic client.

    Returns:
        anthropic.Anthropic | None:
            Anthropic client when API key is available,
            otherwise None.
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        return None

    return anthropic.Anthropic(
        api_key=api_key
    )


def is_ai_available():
    """
    Check whether a real Anthropic API key is configured.
    """

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        return False

    if api_key == "your_api_key_here":
        return False

    return True


def get_ai_status():
    """
    Return the current AI integration status.
    """

    if is_ai_available():
        return "available"

    return "not_configured"


def send_to_claude(
    prompt,
    context=None,
    model=None,
    max_tokens=1024
):
    """
    Send a request to Claude with optional conversation context.

    Args:
        prompt (str):
            User prompt/message.

        context (str | None):
            Relevant conversation context to provide to Claude.

        model (str | None):
            Claude model to use.

        max_tokens (int):
            Maximum number of tokens in the response.

    Returns:
        str:
            Claude's response, or an error/status message.
    """

    client = get_anthropic_client()

    if client is None:
        return "AI is not configured. Please add a valid Anthropic API key."

    if not prompt or not prompt.strip():
        return "Prompt cannot be empty."

    if model is None:
        model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-sonnet-5"
        )

    # --------------------------------------------------------
    # Context Injection
    # --------------------------------------------------------

    if context:
        prompt = (
            "Here is the relevant context from the conversation:\n\n"
            f"{context}\n\n"
            "Use this context when it is relevant to the "
            "user's request.\n\n"
            f"User request:\n{prompt}"
        )

    try:

        response = client.messages.create(
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