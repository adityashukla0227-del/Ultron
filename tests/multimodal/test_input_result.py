"""
Tests for Ultron Multimodal Input Result.

v0.51 — Multimodal Input Foundation
"""

from datetime import datetime

import pytest

from modules.multimodal.input_result import (
    MultimodalInputResult,
    MultimodalInputResultError,
)


# ========================================================
# Initialization
# ========================================================


def test_result_initializes_with_defaults():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    assert result.input_id == "input-1"
    assert result.status == "created"
    assert result.data is None
    assert result.confidence is None
    assert result.error is None
    assert isinstance(result.created_at, datetime)
    assert result.completed_at is None


def test_result_accepts_initial_values():
    result = MultimodalInputResult(
        input_id="input-1",
        status="processing",
        data="hello",
        confidence=0.95,
        metadata={"source": "test"},
    )

    assert result.input_id == "input-1"
    assert result.status == "processing"
    assert result.data == "hello"
    assert result.confidence == 0.95
    assert result.get_metadata("source") == "test"


def test_result_normalizes_status():
    result = MultimodalInputResult(
        input_id="input-1",
        status="  PROCESSING  ",
    )

    assert result.status == "processing"


@pytest.mark.parametrize(
    "input_id",
    [
        "",
        "   ",
        None,
        123,
    ],
)
def test_invalid_input_id(input_id):
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id=input_id
        )


@pytest.mark.parametrize(
    "status",
    [
        "invalid",
        "",
        "unknown",
    ],
)
def test_invalid_status(status):
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id="input-1",
            status=status,
        )


@pytest.mark.parametrize(
    "confidence",
    [
        -0.1,
        1.1,
        -1,
        2,
        "0.5",
        True,
        False,
    ],
)
def test_invalid_confidence(confidence):
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id="input-1",
            confidence=confidence,
        )


def test_valid_confidence_boundaries():
    low = MultimodalInputResult(
        input_id="input-1",
        confidence=0.0,
    )

    high = MultimodalInputResult(
        input_id="input-2",
        confidence=1.0,
    )

    assert low.confidence == 0.0
    assert high.confidence == 1.0


def test_invalid_error_type():
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id="input-1",
            error=123,
        )


def test_empty_error_rejected():
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id="input-1",
            error="   ",
        )


def test_invalid_metadata():
    with pytest.raises(
        MultimodalInputResultError
    ):
        MultimodalInputResult(
            input_id="input-1",
            metadata=[],
        )


# ========================================================
# Status Helpers
# ========================================================


def test_status_helpers():
    created = MultimodalInputResult(
        input_id="input-1"
    )

    assert created.is_created()
    assert not created.is_processing()
    assert not created.is_completed()
    assert not created.is_failed()
    assert not created.is_skipped()
    assert not created.is_terminal()


def test_processing_status_helper():
    result = MultimodalInputResult(
        input_id="input-1",
        status="processing",
    )

    assert result.is_processing()
    assert not result.is_terminal()


def test_completed_status_helper():
    result = MultimodalInputResult(
        input_id="input-1",
        status="completed",
    )

    assert result.is_completed()
    assert result.is_terminal()
    assert result.is_successful()


def test_failed_status_helper():
    result = MultimodalInputResult(
        input_id="input-1",
        status="failed",
        error="processing failed",
    )

    assert result.is_failed()
    assert result.is_terminal()
    assert result.is_unsuccessful()


def test_skipped_status_helper():
    result = MultimodalInputResult(
        input_id="input-1",
        status="skipped",
    )

    assert result.is_skipped()
    assert result.is_terminal()


# ========================================================
# Lifecycle
# ========================================================


def test_start_processing():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.start_processing()

    assert result.status == "processing"
    assert result.is_processing()


def test_start_processing_from_processing():
    result = MultimodalInputResult(
        input_id="input-1",
        status="processing",
    )

    result.start_processing()

    assert result.status == "processing"


@pytest.mark.parametrize(
    "status",
    [
        "completed",
        "failed",
        "skipped",
    ],
)
def test_terminal_result_cannot_start_processing(status):
    result = MultimodalInputResult(
        input_id="input-1",
        status=status,
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.start_processing()


def test_complete_result():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.start_processing()
    result.complete(
        "hello",
        confidence=0.92,
    )

    assert result.status == "completed"
    assert result.data == "hello"
    assert result.confidence == 0.92
    assert result.error is None
    assert result.completed_at is not None
    assert result.is_terminal()


def test_complete_without_confidence():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.complete(
        {"text": "hello"}
    )

    assert result.status == "completed"
    assert result.data == {"text": "hello"}
    assert result.completed_at is not None


def test_complete_clears_previous_error():
    result = MultimodalInputResult(
        input_id="input-1",
        error="temporary error",
    )

    result.complete("success")

    assert result.status == "completed"
    assert result.error is None


def test_failed_result():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.start_processing()
    result.fail("microphone unavailable")

    assert result.status == "failed"
    assert result.error == "microphone unavailable"
    assert result.completed_at is not None
    assert result.is_failed()


def test_skip_result():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.skip("unsupported modality")

    assert result.status == "skipped"
    assert result.error == "unsupported modality"
    assert result.completed_at is not None


def test_skip_without_reason():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.skip()

    assert result.status == "skipped"
    assert result.error is None


def test_terminal_result_cannot_complete():
    result = MultimodalInputResult(
        input_id="input-1",
        status="completed",
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.complete("again")


def test_terminal_result_cannot_fail():
    result = MultimodalInputResult(
        input_id="input-1",
        status="failed",
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.fail("again")


def test_terminal_result_cannot_skip():
    result = MultimodalInputResult(
        input_id="input-1",
        status="skipped",
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.skip("again")


def test_fail_requires_non_empty_error():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.fail("   ")


def test_fail_requires_string_error():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.fail(123)


# ========================================================
# Data
# ========================================================


def test_get_data_returns_data():
    result = MultimodalInputResult(
        input_id="input-1",
        data={"text": "hello"},
    )

    assert result.get_data() == {
        "text": "hello"
    }


def test_get_data_returns_defensive_copy():
    result = MultimodalInputResult(
        input_id="input-1",
        data={"nested": {"value": 1}},
    )

    data = result.get_data()
    data["nested"]["value"] = 99

    assert result.data["nested"]["value"] == 1


def test_set_data():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.set_data("hello")

    assert result.data == "hello"
    assert result.get_data() == "hello"


# ========================================================
# Confidence
# ========================================================


def test_set_confidence():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.set_confidence(0.87)

    assert result.confidence == 0.87
    assert result.has_confidence()


def test_clear_confidence():
    result = MultimodalInputResult(
        input_id="input-1",
        confidence=0.8,
    )

    result.set_confidence(None)

    assert result.confidence is None
    assert not result.has_confidence()


@pytest.mark.parametrize(
    "confidence",
    [
        -0.1,
        1.1,
        "high",
        True,
    ],
)
def test_set_invalid_confidence(confidence):
    result = MultimodalInputResult(
        input_id="input-1"
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.set_confidence(confidence)


# ========================================================
# Error
# ========================================================


def test_has_error():
    result = MultimodalInputResult(
        input_id="input-1",
        error="failed",
    )

    assert result.has_error()


def test_get_error():
    result = MultimodalInputResult(
        input_id="input-1",
        error="failed",
    )

    assert result.get_error() == "failed"


def test_get_error_default():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    assert result.get_error("none") == "none"


# ========================================================
# Metadata
# ========================================================


def test_set_metadata():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.set_metadata(
        "language",
        "en",
    )

    assert result.get_metadata("language") == "en"


def test_get_metadata_default():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    assert result.get_metadata(
        "missing",
        "default",
    ) == "default"


def test_get_all_metadata_returns_copy():
    result = MultimodalInputResult(
        input_id="input-1",
        metadata={
            "nested": {
                "value": 1
            }
        },
    )

    metadata = result.get_all_metadata()
    metadata["nested"]["value"] = 99

    assert (
        result.metadata["nested"]["value"]
        == 1
    )


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        123,
    ],
)
def test_invalid_metadata_key(key):
    result = MultimodalInputResult(
        input_id="input-1"
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.set_metadata(
            key,
            "value",
        )


@pytest.mark.parametrize(
    "key",
    [
        "",
        "   ",
        123,
    ],
)
def test_invalid_get_metadata_key(key):
    result = MultimodalInputResult(
        input_id="input-1"
    )

    with pytest.raises(
        MultimodalInputResultError
    ):
        result.get_metadata(key)


# ========================================================
# Serialization
# ========================================================


def test_to_dict():
    result = MultimodalInputResult(
        input_id="input-1",
        status="completed",
        data={"text": "hello"},
        confidence=0.95,
        metadata={"language": "en"},
    )

    result_dict = result.to_dict()

    assert result_dict["input_id"] == "input-1"
    assert result_dict["status"] == "completed"
    assert result_dict["data"] == {
        "text": "hello"
    }
    assert result_dict["confidence"] == 0.95
    assert result_dict["error"] is None
    assert result_dict["metadata"] == {
        "language": "en"
    }
    assert isinstance(
        result_dict["created_at"],
        str,
    )
    assert result_dict["completed_at"] is None


def test_to_dict_completed_at():
    result = MultimodalInputResult(
        input_id="input-1"
    )

    result.complete("hello")

    result_dict = result.to_dict()

    assert isinstance(
        result_dict["completed_at"],
        str,
    )


def test_to_dict_returns_defensive_data():
    payload = {
        "nested": {
            "value": 1
        }
    }

    result = MultimodalInputResult(
        input_id="input-1",
        data=payload,
    )

    serialized = result.to_dict()
    serialized["data"]["nested"]["value"] = 99

    assert result.data["nested"]["value"] == 1


# ========================================================
# Representation
# ========================================================


def test_repr():
    result = MultimodalInputResult(
        input_id="input-1",
        status="completed",
        confidence=0.9,
    )

    representation = repr(result)

    assert "MultimodalInputResult" in representation
    assert "input-1" in representation
    assert "completed" in representation
    assert "0.9" in representation
