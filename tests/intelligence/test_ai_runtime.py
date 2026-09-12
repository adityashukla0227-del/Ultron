from modules.intelligence.ai_runtime import (
    AIRuntime,
)
from modules.intelligence.ai_intelligence import (
    AIIntelligence,
)
from modules.intelligence.intelligence_result import (
    IntelligenceResult,
)


def test_runtime_uses_default_intelligence():
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
        "Hello Ultron"
    )

    assert isinstance(
        result,
        IntelligenceResult,
    )
    assert result.success is True
    assert result.response == "Runtime response"


def test_runtime_forwards_query():
    captured = {}

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        return "Forwarded query"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "Hello Ultron"
    )

    assert result.success is True
    assert captured["prompt"] == "Hello Ultron"


def test_runtime_forwards_max_tokens():
    captured = {}

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["max_tokens"] = max_tokens
        return "Token forwarding"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "Hello Ultron",
        max_tokens=2048,
    )

    assert result.success is True
    assert captured["max_tokens"] == 2048


def test_runtime_forwards_goal_context():
    captured = {}

    goal_context = {
        "goal": "Build Ultron",
        "topic": "AI",
    }

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["goal_context"] = goal_context
        return "Goal context"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=lambda **kwargs: "Goal response",
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "Continue building Ultron",
        goal_context=goal_context,
    )

    assert result.success is True
    assert captured["goal_context"] == goal_context


def test_runtime_forwards_ranked_context():
    captured = {}

    ranked_context = [
        {
            "query": "Previous Ultron discussion",
            "topic": "development",
        }
    ]

    def fake_context_builder(
        user,
        goal_context=None,
        ranked_context=None,
    ):
        captured["ranked_context"] = ranked_context
        return "Ranked context"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=lambda **kwargs: "Ranked response",
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "Continue our discussion",
        ranked_context=ranked_context,
    )

    assert result.success is True
    assert captured["ranked_context"] == ranked_context


def test_runtime_forwards_injected_context():
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
        captured["prompt"] = prompt
        captured["context"] = context
        captured["max_tokens"] = max_tokens
        return "Runtime context response"

    intelligence = AIIntelligence(
        context_builder=fake_context_builder,
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        query="Continue building Ultron",
        goal_context={
            "goal": "Build Ultron",
        },
        ranked_context=[
            {
                "query": "Previous discussion",
            }
        ],
        max_tokens=2048,
        context="Injected runtime context",
    )

    assert result.success is True
    assert result.response == "Runtime context response"

    assert captured["prompt"] == "Continue building Ultron"
    assert captured["context"] == "Injected runtime context"
    assert captured["max_tokens"] == 2048
    assert "builder_called" not in captured


def test_runtime_strips_query():
    captured = {}

    def fake_generator(
        prompt,
        context=None,
        max_tokens=1024,
    ):
        captured["prompt"] = prompt
        return "Stripped query"

    intelligence = AIIntelligence(
        response_generator=fake_generator,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "   Hello Ultron   "
    )

    assert result.success is True
    assert captured["prompt"] == "Hello Ultron"


def test_runtime_propagates_intelligence_failure():
    intelligence = AIIntelligence(
        response_generator=lambda **kwargs: None,
    )

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    result = runtime.run(
        "Hello Ultron"
    )

    assert isinstance(
        result,
        IntelligenceResult,
    )
    assert result.success is False
    assert "invalid response" in result.error.lower()


def test_runtime_propagates_intelligence_exception():
    intelligence = AIIntelligence()

    def failing_generate(
        query,
        goal_context=None,
        ranked_context=None,
        max_tokens=1024,
        context=None,
    ):
        raise RuntimeError(
            "Runtime intelligence failure"
        )

    intelligence.generate = failing_generate

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    try:
        runtime.run(
            "Hello Ultron"
        )
        assert False
    except RuntimeError as exc:
        assert "Runtime intelligence failure" in str(exc)


def test_runtime_is_available():
    intelligence = AIIntelligence()

    runtime = AIRuntime(
        intelligence=intelligence,
    )

    assert runtime.is_available() is True