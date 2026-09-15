"""
Tests for Ultron Agent Decision Model
Version: v0.76
"""

import pytest

from modules.intelligence.agent_decision import (
    AgentDecision,
    DecisionType,
)
from modules.intelligence.intent import (
    Intent,
    IntentType,
)


def create_intent():
    return Intent(
        intent_type=IntentType.ACTION,
        query="Calculator kholo",
        confidence=0.95,
    )


def test_agent_decision_creation():
    intent = create_intent()

    decision = AgentDecision(
        decision_type=DecisionType.EXECUTE,
        intent=intent,
        confidence=0.92,
    )

    assert isinstance(decision, AgentDecision)
    assert decision.decision_type is DecisionType.EXECUTE
    assert decision.intent is intent
    assert decision.confidence == 0.92


def test_agent_decision_to_dict():
    intent = create_intent()

    decision = AgentDecision(
        decision_type=DecisionType.EXECUTE,
        intent=intent,
        confidence=0.92,
        metadata={"reason": "action intent"},
    )

    result = decision.to_dict()

    assert result["decision_type"] == "execute"
    assert result["intent"]["intent_type"] == "action"
    assert result["intent"]["query"] == "Calculator kholo"
    assert result["confidence"] == 0.92
    assert result["metadata"]["reason"] == "action intent"


def test_invalid_decision_type_rejected():
    intent = create_intent()

    with pytest.raises(
        TypeError,
        match="decision_type must be a DecisionType",
    ):
        AgentDecision(
            decision_type="execute",
            intent=intent,
            confidence=0.92,
        )


def test_invalid_intent_rejected():
    with pytest.raises(
        TypeError,
        match="intent must be an Intent instance",
    ):
        AgentDecision(
            decision_type=DecisionType.EXECUTE,
            intent="invalid",
            confidence=0.92,
        )


def test_invalid_confidence_type_rejected():
    intent = create_intent()

    with pytest.raises(
        TypeError,
        match="confidence must be a number",
    ):
        AgentDecision(
            decision_type=DecisionType.EXECUTE,
            intent=intent,
            confidence="high",
        )


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1],
)
def test_confidence_range_rejected(
    confidence,
):
    intent = create_intent()

    with pytest.raises(
        ValueError,
        match="confidence must be between",
    ):
        AgentDecision(
            decision_type=DecisionType.EXECUTE,
            intent=intent,
            confidence=confidence,
        )


def test_invalid_metadata_rejected():
    intent = create_intent()

    with pytest.raises(
        TypeError,
        match="metadata must be a dictionary",
    ):
        AgentDecision(
            decision_type=DecisionType.EXECUTE,
            intent=intent,
            confidence=0.92,
            metadata=[],
        )


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
    intent = create_intent()

    decision = AgentDecision(
        decision_type=decision_type,
        intent=intent,
        confidence=0.90,
    )

    assert decision.decision_type is decision_type


def test_decision_model_is_immutable():
    intent = create_intent()

    decision = AgentDecision(
        decision_type=DecisionType.RESPOND,
        intent=intent,
        confidence=0.90,
    )

    with pytest.raises(
        AttributeError,
    ):
        decision.confidence = 0.50