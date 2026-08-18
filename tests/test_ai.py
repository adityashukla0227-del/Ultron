from core.ai_engine import (
    generate_ai_response,
    get_ai_provider,
)


def test_mock_ai_response():
    response = generate_ai_response(
        "Hello Ultron"
    )

    assert response
    assert "Mock AI response" in response


def test_mock_provider_selection(monkeypatch):
    monkeypatch.setenv(
        "AI_MODE",
        "mock"
    )

    provider = get_ai_provider()

    assert provider.__class__.__name__ == "MockProvider"


def test_anthropic_provider_selection(monkeypatch):
    monkeypatch.setenv(
        "AI_MODE",
        "anthropic"
    )

    provider = get_ai_provider()

    assert provider.__class__.__name__ == "AnthropicProvider"


def test_empty_prompt():
    response = generate_ai_response("")

    assert response
    assert "Prompt cannot be empty" in response


def test_prompt_with_context():
    response = generate_ai_response(
        "What are we working on?",
        context="Current project: Ultron AI assistant"
    )

    assert response
    assert "Mock AI response" in response
    assert "What are we working on?" in response


def test_mock_provider_with_context(monkeypatch):
    monkeypatch.setenv(
        "AI_MODE",
        "mock"
    )

    provider = get_ai_provider()

    response = provider.generate(
        prompt="Explain AI",
        context="User is building Ultron"
    )

    assert response
    assert "Mock AI response" in response
    assert "Explain AI" in response


def test_anthropic_without_api_key(monkeypatch):
    monkeypatch.delenv(
        "ANTHROPIC_API_KEY",
        raising=False
    )

    monkeypatch.setenv(
        "AI_MODE",
        "anthropic"
    )

    provider = get_ai_provider()

    response = provider.generate(
        prompt="Hello Ultron"
    )

    assert response
    assert "not configured" in response.lower()


def test_anthropic_placeholder_api_key(monkeypatch):
    monkeypatch.setenv(
        "ANTHROPIC_API_KEY",
        "your_api_key_here"
    )

    monkeypatch.setenv(
        "AI_MODE",
        "anthropic"
    )

    provider = get_ai_provider()

    response = provider.generate(
        prompt="Hello Ultron"
    )

    assert response
    assert "not configured" in response.lower()