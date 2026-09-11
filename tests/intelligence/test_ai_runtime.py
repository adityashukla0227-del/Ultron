"""
Tests for Ultron AI Runtime.

Version: v0.73
"""

from modules.intelligence.ai_intelligence import AIIntelligence
from modules.intelligence.ai_runtime import AIRuntime
from modules.intelligence.intelligence_result import IntelligenceResult


def test_runtime_initializes_with_default_intelligence():
    runtime = AIRuntime()

    assert isinstance(
        runtime._intelligence,
        AIIntelligence,
    )


def test_runtime_accepts_injected_intelligence():
    intelligence = AIIntelligence()

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    assert runtime._intelligence is intelligence


def test_runtime_rejects_invalid_intelligence():
    try:
        AIRuntime(
            intelligence="invalid",
        )
        assert False
    except TypeError as exc:
        assert "AIIntelligence" in str(exc)


def test_runtime_run_returns_intelligence_result():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: "Runtime response",
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        query="Hello Ultron",
    )

    assert isinstance(
        result,
        IntelligenceResult,
    )

    assert result.success is True
    assert result.response == "Runtime response"


def test_runtime_delegates_query_to_intelligence():
    captured = {}

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        captured["context"] = context
        captured["max_tokens"] = max_tokens

        return "Delegated response"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        query="Build Ultron",
        max_tokens=2048,
    )

    assert result.success is True
    assert result.response == "Delegated response"

    assert captured["prompt"] == "Build Ultron"
    assert captured["max_tokens"] == 2048


def test_runtime_forwards_context():
    captured = {}

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["user"] = user
        captured["goal_context"] = goal_context
        captured["ranked_context"] = ranked_context

        return "Runtime context"

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        captured["context"] = context

        return "Context response"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
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

    result = runtime.run(
        query="Continue building Ultron",
        goal_context=goal_context,
        ranked_context=ranked_context,
    )

    assert result.success is True
    assert result.response == "Context response"

    assert captured["user"] == "Continue building Ultron"
    assert captured["goal_context"] == goal_context
    assert captured["ranked_context"] == ranked_context
    assert captured["prompt"] == "Continue building Ultron"
    assert captured["context"] == "Runtime context"


def test_runtime_strips_query_through_intelligence():
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

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        query="   Hello Ultron   ",
    )

    assert result.success is True
    assert captured["prompt"] == "Hello Ultron"


def test_runtime_propagates_intelligence_failure_result():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: None,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        query="Hello Ultron",
    )

    assert isinstance(
        result,
        IntelligenceResult,
    )

    assert result.success is False
    assert "invalid response" in result.error.lower()


def test_runtime_is_available():
    intelligence = AIIntelligence()

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    assert runtime.is_available() is True