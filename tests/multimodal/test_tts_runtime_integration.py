"""
Tests for Runtime TTS Integration.

Ultron v0.63 — Runtime TTS Integration
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from modules.multimodal.input_result import (
    MultimodalInputResult,
)
from modules.multimodal.tts_provider import (
    TTSProvider,
)
from modules.multimodal.tts_runtime_integration import (
    TTSRuntimeIntegration,
    TTSRuntimeIntegrationError,
)


class TestTTSRuntimeIntegrationInitialization:
    """Test runtime TTS integration initialization."""

    def test_requires_tts_provider(self):
        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            TTSRuntimeIntegration(
                provider=None
            )

    def test_requires_tts_provider_instance(self):
        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            TTSRuntimeIntegration(
                provider=MagicMock()
            )

    def test_initializes_successfully(self):
        provider = MagicMock(
            spec=TTSProvider
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        assert (
            integration.get_provider()
            is provider
        )

    def test_repr_contains_provider_name(self):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        assert "test-tts" in repr(
            integration
        )


class TestTTSRuntimeIntegrationAvailability:
    """Test provider availability delegation."""

    def test_is_available_delegates_to_provider(
        self,
    ):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.is_available.return_value = (
            True
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        assert integration.is_available() is True

        provider.is_available.assert_called_once()


class TestTTSRuntimeIntegrationValidation:
    """Test runtime response validation."""

    def create_integration(self):
        provider = MagicMock(
            spec=TTSProvider
        )

        return TTSRuntimeIntegration(
            provider=provider
        )

    def test_accepts_valid_text(self):
        integration = self.create_integration()

        integration.validate_text(
            "Hello from Ultron"
        )

    def test_rejects_empty_text(self):
        integration = self.create_integration()

        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            integration.validate_text("")

    def test_rejects_whitespace_text(self):
        integration = self.create_integration()

        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            integration.validate_text("   ")

    def test_rejects_none_text(self):
        integration = self.create_integration()

        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            integration.validate_text(None)

    def test_rejects_non_string_text(self):
        integration = self.create_integration()

        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            integration.validate_text(123)


class TestTTSRuntimeIntegrationSynthesis:
    """Test runtime TTS synthesis."""

    @staticmethod
    def create_integration():
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        result = MultimodalInputResult(
            input_id="tts-input",
            input_type="text",
        )

        result.complete(
            data=b"generated-audio"
        )

        provider.synthesize.return_value = (
            result
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        return integration, provider

    def test_synthesize_returns_result(self):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

    def test_synthesize_returns_provider_result(
        self,
    ):
        integration, provider = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert result is (
            provider.synthesize.return_value
        )

    def test_synthesize_delegates_text_to_provider(
        self,
    ):
        integration, provider = (
            self.create_integration()
        )

        text = "Hello from Ultron"

        integration.synthesize(text)

        provider.synthesize.assert_called_once_with(
            text
        )

    def test_synthesize_preserves_audio(self):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert result.get_data() == (
            b"generated-audio"
        )

    def test_synthesis_result_contains_integration_metadata(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert (
            result.get_metadata(
                "integration"
            )
            == "tts-runtime-integration"
        )

    def test_synthesis_result_contains_provider_metadata(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert (
            result.get_metadata(
                "provider"
            )
            == "test-tts"
        )

    def test_synthesis_result_contains_source_text(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello from Ultron"
        )

        assert (
            result.get_metadata(
                "source_text"
            )
            == "Hello from Ultron"
        )

    def test_synthesis_supports_runtime_context_id(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello",
            runtime_context_id="context-123",
        )

        assert (
            result.get_metadata(
                "runtime_context_id"
            )
            == "context-123"
        )

    def test_synthesis_supports_execution_id(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello",
            execution_id="execution-123",
        )

        assert (
            result.get_metadata(
                "execution_id"
            )
            == "execution-123"
        )

    def test_synthesis_supports_custom_metadata(
        self,
    ):
        integration, _ = (
            self.create_integration()
        )

        result = integration.synthesize(
            "Hello",
            metadata={
                "response_type": "voice",
            },
        )

        assert (
            result.get_metadata(
                "response_type"
            )
            == "voice"
        )

    def test_empty_text_does_not_call_provider(
        self,
    ):
        integration, provider = (
            self.create_integration()
        )

        with pytest.raises(
            TTSRuntimeIntegrationError
        ):
            integration.synthesize("")

        provider.synthesize.assert_not_called()


class TestTTSRuntimeIntegrationSafeSynthesis:
    """Test safe runtime TTS synthesis."""

    def test_safe_synthesis_returns_failed_result_on_error(
        self,
    ):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        provider.synthesize.side_effect = (
            RuntimeError(
                "provider failure"
            )
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        result = integration.synthesize_safe(
            "Hello"
        )

        assert isinstance(
            result,
            MultimodalInputResult,
        )

        assert result.status == "failed"
        assert result.success is False

    def test_safe_synthesis_preserves_error(
        self,
    ):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        provider.synthesize.side_effect = (
            RuntimeError(
                "provider failure"
            )
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        result = integration.synthesize_safe(
            "Hello"
        )

        assert "provider failure" in str(
            result.error
        )

    def test_safe_synthesis_adds_integration_metadata(
        self,
    ):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        provider.synthesize.side_effect = (
            RuntimeError(
                "provider failure"
            )
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        result = integration.synthesize_safe(
            "Hello"
        )

        assert (
            result.get_metadata(
                "integration"
            )
            == "tts-runtime-integration"
        )

    def test_safe_synthesis_does_not_raise_provider_error(
        self,
    ):
        provider = MagicMock(
            spec=TTSProvider
        )

        provider.get_name.return_value = (
            "test-tts"
        )

        provider.synthesize.side_effect = (
            RuntimeError(
                "provider failure"
            )
        )

        integration = TTSRuntimeIntegration(
            provider=provider
        )

        result = integration.synthesize_safe(
            "Hello"
        )

        assert result.is_failed()