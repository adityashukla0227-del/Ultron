from modules.intelligence.intelligence_result import (
    IntelligenceResult,
)


def test_success_result():
    result = IntelligenceResult.success_result(
        response="Hello from Ultron"
    )

    assert result.success is True
    assert result.response == "Hello from Ultron"
    assert result.intent is None
    assert result.action is None
    assert result.error is None


def test_failure_result():
    result = IntelligenceResult.failure_result(
        error="AI provider unavailable"
    )

    assert result.success is False
    assert result.response is None
    assert result.error == "AI provider unavailable"


def test_result_serialization():
    result = IntelligenceResult.success_result(
        response="Ultron is ready",
        metadata={"provider": "mock"},
    )

    data = result.to_dict()

    assert data["success"] is True
    assert data["response"] == "Ultron is ready"
    assert data["metadata"]["provider"] == "mock"


def test_future_intelligence_fields():
    result = IntelligenceResult.success_result(
        response="Opening the application",
        intent="application_launch",
        action="launch_application",
    )

    assert result.intent == "application_launch"
    assert result.action == "launch_application"


def test_result_is_immutable():
    result = IntelligenceResult.success_result(
        response="Immutable"
    )

    try:
        result.response = "Changed"
        assert False
    except AttributeError:
        pass


def test_invalid_success_type():
    try:
        IntelligenceResult(
            success="true"
        )
        assert False
    except TypeError:
        pass


def test_invalid_metadata_type():
    try:
        IntelligenceResult(
            success=True,
            metadata="invalid"
        )
        assert False
    except TypeError:
        pass


def test_success_and_failure_helpers():
    success = IntelligenceResult.success_result(
        response="OK"
    )
    failure = IntelligenceResult.failure_result(
        error="Failed"
    )

    assert success.is_successful() is True
    assert success.is_failed() is False

    assert failure.is_successful() is False
    assert failure.is_failed() is True