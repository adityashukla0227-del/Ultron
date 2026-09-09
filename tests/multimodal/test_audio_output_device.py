"""
Tests for Ultron Audio Output Device.

v0.67 — Audio Output Device Integration
"""

import pytest

from modules.multimodal.audio_output_device import (
    AudioOutputDevice,
    AudioOutputDeviceError,
)


class TestAudioOutputDevice:
    """Test AudioOutputDevice behavior."""

    def create_device(self):
        return AudioOutputDevice(
            device_id="speaker-1",
            name="Test Speaker",
            device_type=AudioOutputDevice.DEVICE_TYPE_SPEAKER,
            available=True,
            is_default=True,
            sample_rates=[16000, 24000, 48000],
            supported_formats=["mp3", "wav"],
            metadata={
                "backend": "test"
            },
        )

    def test_initialization(self):
        device = self.create_device()

        assert device.get_device_id() == "speaker-1"
        assert device.get_name() == "Test Speaker"
        assert (
            device.get_device_type()
            == AudioOutputDevice.DEVICE_TYPE_SPEAKER
        )
        assert device.is_available() is True
        assert device.is_default() is True

    def test_sample_rates(self):
        device = self.create_device()

        assert device.get_sample_rates() == [
            16000,
            24000,
            48000,
        ]

    def test_sample_rate_support(self):
        device = self.create_device()

        assert device.supports_sample_rate(24000) is True
        assert device.supports_sample_rate(8000) is False

    def test_supported_formats(self):
        device = self.create_device()

        assert device.get_supported_formats() == [
            "mp3",
            "wav",
        ]

    def test_format_support(self):
        device = self.create_device()

        assert device.supports_format("MP3") is True
        assert device.supports_format("flac") is False

    def test_availability(self):
        device = self.create_device()

        device.set_available(False)

        assert device.is_available() is False

    def test_default_state(self):
        device = self.create_device()

        device.set_default(False)

        assert device.is_default() is False

    def test_metadata(self):
        device = self.create_device()

        assert (
            device.get_metadata_value("backend")
            == "test"
        )

        device.set_metadata(
            "version",
            "1",
        )

        assert (
            device.get_metadata_value("version")
            == "1"
        )

    def test_metadata_is_defensive(self):
        device = self.create_device()

        metadata = device.get_metadata()

        metadata["backend"] = "changed"

        assert (
            device.get_metadata_value("backend")
            == "test"
        )

    def test_metadata_initialization_is_defensive(self):
        metadata = {
            "backend": "test"
        }

        device = AudioOutputDevice(
            device_id="speaker-1",
            name="Speaker",
            metadata=metadata,
        )

        metadata["backend"] = "changed"

        assert (
            device.get_metadata_value("backend")
            == "test"
        )

    def test_metadata_invalid_key(self):
        device = self.create_device()

        with pytest.raises(AudioOutputDeviceError):
            device.set_metadata(
                "",
                "value",
            )

    def test_invalid_device_id(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="",
                name="Speaker",
            )

    def test_invalid_name(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="",
            )

    def test_invalid_device_type(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="Speaker",
                device_type="invalid",
            )

    def test_invalid_availability(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="Speaker",
                available="yes",
            )

    def test_invalid_default_state(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="Speaker",
                is_default="yes",
            )

    def test_invalid_sample_rates(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="Speaker",
                sample_rates=[16000, -1],
            )

    def test_invalid_formats(self):
        with pytest.raises(AudioOutputDeviceError):
            AudioOutputDevice(
                device_id="speaker",
                name="Speaker",
                supported_formats=["mp3", ""],
            )

    def test_to_dict(self):
        device = self.create_device()

        data = device.to_dict()

        assert data["device_id"] == "speaker-1"
        assert data["name"] == "Test Speaker"
        assert data["available"] is True
        assert data["is_default"] is True

    def test_repr(self):
        device = self.create_device()

        result = repr(device)

        assert "AudioOutputDevice" in result
        assert "speaker-1" in result