"""
Tests for Ultron Voice Processing Strategy.

v0.55 — Voice Processing Intelligence Foundation
"""

from __future__ import annotations

import pytest

from modules.multimodal.input_result import MultimodalInputResult
from modules.multimodal.input_type import InputType
from modules.multimodal.voice_input import VoiceInput
from modules.multimodal.voice_processing_strategy import (
    VoiceProcessingStrategy,
    VoiceProcessingStrategyError,
)


class DummyVoiceProcessingStrategy(VoiceProcessingStrategy):
    """Concrete test implementation of VoiceProcessingStrategy."""

    def process(
        self,
        voice_input: VoiceInput,
    ) -> MultimodalInputResult:
        self._validate_voice_input(voice_input)

        result = MultimodalInputResult(
            input_id=voice_input.get_id(),
            input_type=InputType.VOICE,
            status="completed",
        )

        result.set_data(
            {
                "strategy": self.get_name(),
                "mode": self.get_mode(),
            }
        )

        return result


@pytest.fixture
def strategy():
    """Return a default test strategy."""

    return DummyVoiceProcessingStrategy(
        name="Test Strategy",
    )


@pytest.fixture
def voice_input():
    """Return a valid VoiceInput instance."""

    return VoiceInput(
        b"test-audio",
        audio_format="wav",
    )


# ----------------------------------------------------------------------
# Initialization
# ----------------------------------------------------------------------


def test_strategy_initializes_with_name():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
    )

    assert strategy.get_name() == "Test Strategy"


def test_strategy_initializes_with_default_mode():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
    )

    assert strategy.get_mode() == "default"


def test_strategy_initializes_with_custom_mode():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        mode="transcription",
    )

    assert strategy.get_mode() == "transcription"


def test_strategy_strips_name():
    strategy = DummyVoiceProcessingStrategy(
        name="  Test Strategy  ",
    )

    assert strategy.get_name() == "Test Strategy"


def test_strategy_strips_mode():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        mode="  transcription  ",
    )

    assert strategy.get_mode() == "transcription"


def test_strategy_rejects_non_string_name():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name=123,
        )


def test_strategy_rejects_empty_name():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="",
        )


def test_strategy_rejects_whitespace_name():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="   ",
        )


def test_strategy_rejects_non_string_mode():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="Test Strategy",
            mode=123,
        )


def test_strategy_rejects_empty_mode():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="Test Strategy",
            mode="",
        )


def test_strategy_rejects_whitespace_mode():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="Test Strategy",
            mode="   ",
        )


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------


def test_strategy_accepts_configuration():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        configuration={
            "language": "en",
            "timeout": 30,
        },
    )

    assert strategy.get_configuration("language") == "en"
    assert strategy.get_configuration("timeout") == 30


def test_strategy_rejects_non_dictionary_configuration():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="Test Strategy",
            configuration="invalid",
        )


def test_strategy_configuration_is_defensive():
    configuration = {
        "language": "en",
    }

    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        configuration=configuration,
    )

    configuration["language"] = "fr"

    assert strategy.get_configuration("language") == "en"


def test_strategy_sets_configuration(strategy):
    strategy.set_configuration(
        "language",
        "en",
    )

    assert strategy.get_configuration("language") == "en"


def test_strategy_replaces_configuration(strategy):
    strategy.set_configuration(
        "language",
        "en",
    )

    strategy.set_configuration(
        "language",
        "fr",
    )

    assert strategy.get_configuration("language") == "fr"


def test_strategy_get_configuration_returns_default(strategy):
    assert strategy.get_configuration(
        "missing",
        "fallback",
    ) == "fallback"


def test_strategy_rejects_invalid_configuration_key(strategy):
    with pytest.raises(VoiceProcessingStrategyError):
        strategy.set_configuration(
            "",
            "value",
        )


def test_strategy_rejects_non_string_configuration_key(strategy):
    with pytest.raises(VoiceProcessingStrategyError):
        strategy.set_configuration(
            123,
            "value",
        )


def test_strategy_returns_defensive_configuration_copy(strategy):
    strategy.set_configuration(
        "language",
        "en",
    )

    configuration = strategy.get_all_configuration()

    configuration["language"] = "fr"

    assert strategy.get_configuration("language") == "en"


# ----------------------------------------------------------------------
# Metadata
# ----------------------------------------------------------------------


def test_strategy_accepts_metadata():
    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        metadata={
            "provider": "test",
        },
    )

    assert strategy.get_metadata("provider") == "test"


def test_strategy_rejects_non_dictionary_metadata():
    with pytest.raises(VoiceProcessingStrategyError):
        DummyVoiceProcessingStrategy(
            name="Test Strategy",
            metadata="invalid",
        )


def test_strategy_metadata_is_defensive():
    metadata = {
        "provider": "test",
    }

    strategy = DummyVoiceProcessingStrategy(
        name="Test Strategy",
        metadata=metadata,
    )

    metadata["provider"] = "changed"

    assert strategy.get_metadata("provider") == "test"


def test_strategy_sets_metadata(strategy):
    strategy.set_metadata(
        "provider",
        "test",
    )

    assert strategy.get_metadata("provider") == "test"


def test_strategy_get_metadata_returns_default(strategy):
    assert strategy.get_metadata(
        "missing",
        "fallback",
    ) == "fallback"


def test_strategy_rejects_invalid_metadata_key(strategy):
    with pytest.raises(VoiceProcessingStrategyError):
        strategy.set_metadata(
            "",
            "value",
        )


def test_strategy_rejects_non_string_metadata_key(strategy):
    with pytest.raises(VoiceProcessingStrategyError):
        strategy.set_metadata(
            123,
            "value",
        )


def test_strategy_returns_defensive_metadata_copy(strategy):
    strategy.set_metadata(
        "provider",
        "test",
    )

    metadata = strategy.get_all_metadata()

    metadata["provider"] = "changed"

    assert strategy.get_metadata("provider") == "test"


# ----------------------------------------------------------------------
# Voice Input Validation
# ----------------------------------------------------------------------


def test_strategy_validates_voice_input(
    strategy,
    voice_input,
):
    result = strategy.process(voice_input)

    assert isinstance(
        result,
        MultimodalInputResult,
    )


def test_strategy_rejects_invalid_voice_input_type(
    strategy,
):
    with pytest.raises(VoiceProcessingStrategyError):
        strategy.process("invalid")


def test_strategy_accepts_empty_audio_input(
    strategy,
):
    voice_input = VoiceInput(
        b"",
        audio_format="wav",
    )

    result = strategy.process(voice_input)

    assert isinstance(
        result,
        MultimodalInputResult,
    )


# ----------------------------------------------------------------------
# Processing Contract
# ----------------------------------------------------------------------


def test_strategy_process_returns_standard_result(
    strategy,
    voice_input,
):
    result = strategy.process(voice_input)

    assert isinstance(
        result,
        MultimodalInputResult,
    )


def test_strategy_process_preserves_input_id(
    strategy,
    voice_input,
):
    result = strategy.process(voice_input)

    assert result.input_id == voice_input.get_id()


def test_strategy_process_returns_completed_result(
    strategy,
    voice_input,
):
    result = strategy.process(voice_input)

    assert result.is_completed()


def test_strategy_process_contains_strategy_metadata(
    strategy,
    voice_input,
):
    result = strategy.process(voice_input)

    data = result.get_data()

    assert data["strategy"] == "Test Strategy"
    assert data["mode"] == "default"


# ----------------------------------------------------------------------
# Representation
# ----------------------------------------------------------------------


def test_strategy_repr_contains_class_name(strategy):
    representation = repr(strategy)

    assert "DummyVoiceProcessingStrategy" in representation


def test_strategy_repr_contains_name(strategy):
    representation = repr(strategy)

    assert "Test Strategy" in representation


def test_strategy_repr_contains_mode(strategy):
    representation = repr(strategy)

    assert "default" in representation


# ----------------------------------------------------------------------
# Abstraction
# ----------------------------------------------------------------------


def test_base_strategy_cannot_be_instantiated():
    with pytest.raises(TypeError):
        VoiceProcessingStrategy(
            name="Base Strategy",
        )


def test_strategy_configuration_is_independent_between_instances():
    first = DummyVoiceProcessingStrategy(
        name="First",
        configuration={
            "language": "en",
        },
    )

    second = DummyVoiceProcessingStrategy(
        name="Second",
        configuration={
            "language": "fr",
        },
    )

    first.set_configuration(
        "timeout",
        30,
    )

    assert second.get_configuration("timeout") is None


def test_strategy_metadata_is_independent_between_instances():
    first = DummyVoiceProcessingStrategy(
        name="First",
        metadata={
            "provider": "one",
        },
    )

    second = DummyVoiceProcessingStrategy(
        name="Second",
        metadata={
            "provider": "two",
        },
    )

    first.set_metadata(
        "version",
        "1",
    )

    assert second.get_metadata("version") is None


def test_strategy_deep_copies_nested_configuration():
    configuration = {
        "provider": {
            "name": "test",
        }
    }

    strategy = DummyVoiceProcessingStrategy(
        name="Test",
        configuration=configuration,
    )

    configuration["provider"]["name"] = "changed"

    assert (
        strategy.get_configuration("provider")["name"]
        == "test"
    )


def test_strategy_deep_copies_nested_metadata():
    metadata = {
        "provider": {
            "name": "test",
        }
    }

    strategy = DummyVoiceProcessingStrategy(
        name="Test",
        metadata=metadata,
    )

    metadata["provider"]["name"] = "changed"

    assert (
        strategy.get_metadata("provider")["name"]
        == "test"
    )