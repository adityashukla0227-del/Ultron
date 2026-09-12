from modules.intelligence.ai_intelligence import (
    AIIntelligence,
)


def test_intelligence_success():
    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        return f"AI response: {prompt}"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    result = intelligence.generate(
        "Hello Ultron"
    )

    assert result.success is True
    assert result.response == "AI response: Hello Ultron"
    assert result.intent is None
    assert result.action is None
    assert result.error is None


def test_intelligence_uses_context_builder():
    captured = {}

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["user"] = user
        captured["goal_context"] = goal_context
        captured["ranked_context"] = ranked_context
        return "Built AI context"

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        captured["context"] = context
        captured["max_tokens"] = max_tokens
        return "Context-aware response"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=fake_generator,
    )

    goal_context = {
        "goal": "Build Ultron",
        "topic": "AI",
    }

    ranked_context = [
        {
            "query": "Previous Ultron discussion",
            "topic": "development",
        }
    ]

    result = intelligence.generate(
        "What are we building?",
        goal_context=goal_context,
        ranked_context=ranked_context,
        max_tokens=2048,
    )

    assert result.success is True
    assert result.response == "Context-aware response"

    assert captured["user"] == "What are we building?"
    assert captured["goal_context"] == goal_context
    assert captured["ranked_context"] == ranked_context

    assert captured["prompt"] == "What are we building?"
    assert captured["context"] == "Built AI context"
    assert captured["max_tokens"] == 2048


def test_intelligence_uses_injected_context():
    captured = {}

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["builder_called"] = True
        return "Built context"

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        captured["context"] = context
        return "Injected context response"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=fake_generator,
    )

    result = intelligence.generate(
        "Continue building Ultron",
        context="Injected Ultron context",
    )

    assert result.success is True
    assert result.response == "Injected context response"
    assert captured["prompt"] == "Continue building Ultron"
    assert captured["context"] == "Injected Ultron context"
    assert "builder_called" not in captured


def test_intelligence_injected_context_takes_precedence():
    captured = {}

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["builder_called"] = True
        return "Generated context"

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["context"] = context
        return "Precedence response"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=fake_generator,
    )

    result = intelligence.generate(
        "What are we building?",
        goal_context={
            "goal": "Build Ultron",
        },
        ranked_context=[
            {
                "query": "Previous discussion",
            }
        ],
        context="Explicit injected context",
    )

    assert result.success is True
    assert captured["context"] == "Explicit injected context"
    assert "builder_called" not in captured


def test_invalid_injected_context_returns_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "Should not run",
    )

    result = intelligence.generate(
        "Hello Ultron",
        context=123,
    )

    assert result.success is False
    assert "context must be a string" in result.error.lower()


def test_intelligence_strips_query():
    captured = {}

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        return "Clean response"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    result = intelligence.generate(
        "   Hello Ultron   "
    )

    assert result.success is True
    assert captured["prompt"] == "Hello Ultron"


def test_empty_query_returns_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "Should not run",
    )

    result = intelligence.generate("   ")

    assert result.success is False
    assert "cannot be empty" in result.error.lower()


def test_non_string_query_returns_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "Should not run",
    )

    result = intelligence.generate(123)

    assert result.success is False
    assert "must be a string" in result.error.lower()


def test_invalid_ai_response_returns_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: None,
    )

    result = intelligence.generate(
        "Hello Ultron"
    )

    assert result.success is False
    assert "invalid response" in result.error.lower()


def test_empty_ai_response_returns_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "   ",
    )

    result = intelligence.generate(
        "Hello Ultron"
    )

    assert result.success is False
    assert "empty response" in result.error.lower()


def test_ai_engine_exception_returns_failure():
    def failing_generator(**kwargs):
        raise RuntimeError("Provider crashed")

    intelligence = AIIntelligence(
        response_generator=failing_generator,
    )

    result = intelligence.generate(
        "Hello Ultron"
    )

    assert result.success is False
    assert "AI intelligence failed" in result.error
    assert "Provider crashed" in result.error


def test_process_alias():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "Processed",
    )

    result = intelligence.process(
        "Hello Ultron"
    )

    assert result.success is True
    assert result.response == "Processed"


def test_is_available():
    intelligence = AIIntelligence()

    assert intelligence.is_available() is True


def test_invalid_context_builder():
    try:
        AIIntelligence(
            context_builder="invalid",
        )
        assert False
    except TypeError as exc:
        assert "context_builder" in str(exc)


def test_invalid_response_generator():
    try:
        AIIntelligence(
            response_generator="invalid",
        )
        assert False
    except TypeError as exc:
        assert "response_generator" in str(exc)