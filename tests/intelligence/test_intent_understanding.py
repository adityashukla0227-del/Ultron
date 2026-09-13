"""
Tests for Ultron Intent Understanding
Version: v0.75
"""

import pytest

from modules.intelligence.intent import Intent, IntentType
from modules.intelligence.intent_understanding import IntentUnderstanding


def mock_response_generator(
    prompt,
    context=None,
    max_tokens=256,
):
    return (
        '{"intent_type": "action", '
        '"confidence": 0.95, '
        '"metadata": {}}'
    )


def test_understand_returns_structured_intent():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    result = understanding.understand(
        "CalcPro open karo"
    )

    assert isinstance(result, Intent)
    assert result.intent_type is IntentType.ACTION
    assert result.query == "CalcPro open karo"
    assert result.confidence == 0.95
    assert result.metadata["context_used"] is False


def test_understand_strips_query():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    result = understanding.understand(
        "  CalcPro open karo  "
    )

    assert result.query == "CalcPro open karo"


def test_context_is_detected():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    result = understanding.understand(
        "Mere previous project ko continue karo",
        context="Previous project: CalcPro",
    )

    assert result.metadata["context_used"] is True


def test_empty_query_rejected():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    with pytest.raises(ValueError):
        understanding.understand("")


def test_whitespace_query_rejected():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    with pytest.raises(ValueError):
        understanding.understand("   ")


def test_invalid_query_type_rejected():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    with pytest.raises(TypeError):
        understanding.understand(123)


def test_process_alias():
    understanding = IntentUnderstanding(
        response_generator=mock_response_generator,
    )

    result = understanding.process(
        "Ultron ka status batao"
    )

    assert isinstance(result, Intent)
    assert result.query == "Ultron ka status batao"
    assert result.intent_type is IntentType.ACTION


def test_invalid_json_response_rejected():
    def invalid_response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return "not valid json"

    understanding = IntentUnderstanding(
        response_generator=invalid_response_generator,
    )

    with pytest.raises(
        ValueError,
        match="valid JSON",
    ):
        understanding.understand(
            "Ultron ka status batao"
        )


def test_unsupported_intent_rejected():
    def invalid_intent_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"intent_type": "tool_selection", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        )

    understanding = IntentUnderstanding(
        response_generator=invalid_intent_generator,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported intent type",
    ):
        understanding.understand(
            "CalcPro open karo"
        )


def test_invalid_confidence_rejected():
    def invalid_confidence_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"intent_type": "action", '
            '"confidence": 1.5, '
            '"metadata": {}}'
        )

    understanding = IntentUnderstanding(
        response_generator=invalid_confidence_generator,
    )

    with pytest.raises(
        ValueError,
        match="confidence must be between",
    ):
        understanding.understand(
            "CalcPro open karo"
        )


def test_non_dictionary_metadata_rejected():
    def invalid_metadata_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return (
            '{"intent_type": "action", '
            '"confidence": 0.95, '
            '"metadata": []}'
        )

    understanding = IntentUnderstanding(
        response_generator=invalid_metadata_generator,
    )

    with pytest.raises(
        ValueError,
        match="metadata must be a dictionary",
    ):
        understanding.understand(
            "CalcPro open karo"
        )


def test_response_generator_must_be_callable():
    with pytest.raises(
        TypeError,
        match="response_generator must be callable",
    ):
        IntentUnderstanding(
            response_generator="invalid",
        )


def test_build_prompt_contains_intent_boundary():
    prompt = IntentUnderstanding.build_prompt(
        query="CalcPro open karo",
    )

    assert "information" in prompt
    assert "action" in prompt
    assert "creation" in prompt
    assert "continuation" in prompt
    assert "explanation" in prompt
    assert "conversation" in prompt
    assert "unknown" in prompt

    assert "Do not select tools." in prompt
    assert "Do not create plans." in prompt
    assert "Do not execute anything." in prompt


@pytest.mark.parametrize(
    "query, expected_intent",
    [
        (
            "Ultron ka status batao",
            IntentType.INFORMATION,
        ),
        (
            "CalcPro open karo",
            IntentType.ACTION,
        ),
        (
            "Ek website bana do",
            IntentType.CREATION,
        ),
        (
            "Mera previous project continue karo",
            IntentType.CONTINUATION,
        ),
        (
            "Is code ko explain karo",
            IntentType.EXPLANATION,
        ),
        (
            "Kaise ho Ultron?",
            IntentType.CONVERSATION,
        ),
        (
            "asdf qwerty xyz",
            IntentType.UNKNOWN,
        ),
    ],
)
def test_supported_intent_categories(
    query,
    expected_intent,
):
    responses = {
        IntentType.INFORMATION.value: (
            '{"intent_type": "information", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.ACTION.value: (
            '{"intent_type": "action", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.CREATION.value: (
            '{"intent_type": "creation", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.CONTINUATION.value: (
            '{"intent_type": "continuation", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.EXPLANATION.value: (
            '{"intent_type": "explanation", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.CONVERSATION.value: (
            '{"intent_type": "conversation", '
            '"confidence": 0.95, '
            '"metadata": {}}'
        ),
        IntentType.UNKNOWN.value: (
            '{"intent_type": "unknown", '
            '"confidence": 0.20, '
            '"metadata": {}}'
        ),
    }

    def response_generator(
        prompt,
        context=None,
        max_tokens=256,
    ):
        return responses[expected_intent.value]

    understanding = IntentUnderstanding(
        response_generator=response_generator,
    )

    result = understanding.understand(query)

    assert result.intent_type is expected_intent
    assert 0.0 <= result.confidence <= 1.0