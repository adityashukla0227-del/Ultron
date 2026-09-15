"""
Tests for Ultron Agent Decision Layer
Version: v0.76
"""

import pytest

from modules.intelligence.agent_decision import (
    AgentDecision,
    DecisionType,
)
from modules.intelligence.agent_decision_layer import (
    AgentDecisionLayer,
)
from modules.intelligence.intent import (
    Intent,
    IntentType,
)


def create_intent(
    intent_type=IntentType.ACTION,
    query="Calculator kholo",
    confidence=0.95,
):
    return Intent(
        intent_type=intent_type,
        query=query,
        confidence=confidence,
    )


def mock_response_generator(
    prompt,
    context=None,
    max_tokens=256,
):
    return (
        '{"decision_type": "execute", '
        '"confidence": 0.92, '
        '"metadata": {}}'
    )


def test_decide_returns_structured_decision():
    layer = AgentDecisionLayer(
        response_generator=mock_response_generator,
    )

    intent = create_intent()

    result = layer.decide(intent)

    assert isinstance(result, AgentDecision)
    assert result.decision_type is DecisionType.EXECUTE
    assert result.intent is intent
    assert result.confidence == 0.92


def test_process_alias():
    layer = AgentDecisionLayer(
        response_generator=mock_response_generator,
    )

    intent = create_intent()

    result = layer.process(intent)

    assert isinstance(result, AgentDecision)
    assert result.decision_type is DecisionType.EXECUTE


def test_invalid_intent_rejected():
    layer = AgentDecisionLayer(
        response_generator=mock_response_generator,
    )

    with pytest.raises(
        TypeError,
        match="intent must be an Intent instance",
    ):
        layer.decide("invalid")


def test_response_generator_must_be_callable():
    with pytest.raises(
        TypeError,
        match="response_generator must be callable",
    ):
        AgentDecisionLayer(
            response_generator="invalid",
        )


def test_empty_response_rejected():
    def empty_response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return ""

    layer = AgentDecisionLayer(
        response_generator=empty_response_generator,
    )

    with pytest.raises(
        ValueError,
        match="AI response cannot be empty",
    ):
        layer.decide(
            create_intent()
        )


def test_invalid_json_response_rejected():
    def invalid_response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return "not valid json"

    layer = AgentDecisionLayer(
        response_generator=invalid_response_generator,
    )

    with pytest.raises(
        ValueError,
        match="valid JSON",
    ):
        layer.decide(
            create_intent()
        )


def test_unsupported_decision_rejected():
    def invalid_decision_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"decision_type": "select_tool", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        )

    layer = AgentDecisionLayer(
        response_generator=invalid_decision_generator,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported decision type",
    ):
        layer.decide(
            create_intent()
        )


def test_invalid_confidence_rejected():
    def invalid_confidence_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"decision_type": "execute", '
            '"confidence": 1.5, '
            '"metadata": {}}'
        )

    layer = AgentDecisionLayer(
        response_generator=invalid_confidence_generator,
    )

    with pytest.raises(
        ValueError,
        match="confidence must be between",
    ):
        layer.decide(
            create_intent()
        )


def test_non_dictionary_metadata_rejected():
    def invalid_metadata_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"decision_type": "execute", '
            '"confidence": 0.95, '
            '"metadata": []}'
        )

    layer = AgentDecisionLayer(
        response_generator=invalid_metadata_generator,
    )

    with pytest.raises(
        ValueError,
        match="metadata must be a dictionary",
    ):
        layer.decide(
            create_intent()
        )


def test_build_prompt_contains_decision_boundary():
    prompt = AgentDecisionLayer.build_prompt(
        create_intent()
    )

    assert "respond" in prompt
    assert "execute" in prompt
    assert "plan" in prompt
    assert "clarify" in prompt
    assert "continue" in prompt
    assert "unknown" in prompt

    assert "Do not select a specific tool." in prompt
    assert "Do not create an execution plan." in prompt
    assert "Do not execute anything." in prompt


@pytest.mark.parametrize(
    "decision_type",
    [
        DecisionType.RESPOND,
        DecisionType.EXECUTE,
        DecisionType.PLAN,
        DecisionType.CLARIFY,
        DecisionType.CONTINUE,
        DecisionType.UNKNOWN,
    ],
)
def test_supported_decision_types(
    decision_type,
):
    responses = {
        decision_type.value: (
            '{"decision_type": "'
            + decision_type.value
            + '", '
            '"confidence": 0.90, '
            '"metadata": {}}'
        )
    }

    def response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return responses[decision_type.value]

    layer = AgentDecisionLayer(
        response_generator=response_generator,
    )

    result = layer.decide(
        create_intent()
    )

    assert result.decision_type is decision_type
    assert 0.0 <= result.confidence <= 1.0


def test_metadata_is_preserved():
    def response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"decision_type": "plan", '
            '"confidence": 0.88, '
            '"metadata": '
            '{"reason": "multi_step_task"}}'
        )

    layer = AgentDecisionLayer(
        response_generator=response_generator,
    )

    result = layer.decide(
        create_intent(
            intent_type=IntentType.CREATION,
            query="Ek website bana do",
        )
    )

    assert result.decision_type is DecisionType.PLAN
    assert result.metadata["reason"] == "multi_step_task"


def test_prompt_contains_intent_data():
    intent = create_intent(
        intent_type=IntentType.CREATION,
        query="Ek website bana do",
    )

    prompt = AgentDecisionLayer.build_prompt(
        intent
    )

    assert "creation" in prompt
    assert "Ek website bana do" in prompt
    assert "0.95" in prompt