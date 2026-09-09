"""
Tests for Ultron Audio Output Device Manager.

v0.67 — Audio Output Device Integration
"""

import pytest

from modules.multimodal.audio_output_device import (
    AudioOutputDevice,
)
from modules.multimodal.audio_output_device_manager import (
    AudioOutputDeviceManager,
    AudioOutputDeviceManagerError,
)


class TestAudioOutputDeviceManager:
    """Test AudioOutputDeviceManager behavior."""

    def create_device(
        self,
        device_id="speaker-1",
        name="Test Speaker",
        device_type=AudioOutputDevice.DEVICE_TYPE_SPEAKER,
        available=True,
        is_default=False,
    ):
        return AudioOutputDevice(
            device_id=device_id,
            name=name,
            device_type=device_type,
            available=available,
            is_default=is_default,
            sample_rates=[16000, 24000],
            supported_formats=["mp3", "wav"],
        )

    def test_initial_state(self):
        manager = AudioOutputDeviceManager()

        assert manager.count() == 0
        assert manager.get_devices() == []
        assert manager.get_active_device() is None
        assert manager.get_active_device_id() is None
        assert manager.get_default_device() is None

    def test_register_device(self):
        manager = AudioOutputDeviceManager()
        device = self.create_device()

        manager.register_device(device)

        assert manager.count() == 1
        assert manager.has_device("speaker-1") is True
        assert manager.get_device("speaker-1") is device

    def test_register_default_device(self):
        manager = AudioOutputDeviceManager()

        device = self.create_device(
            is_default=True
        )

        manager.register_device(device)

        assert (
            manager.get_active_device()
            is device
        )

    def test_register_duplicate_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device()
        )

        with pytest.raises(
            AudioOutputDeviceManagerError
        ):
            manager.register_device(
                self.create_device()
            )

    def test_unregister_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device()
        )

        manager.unregister_device(
            "speaker-1"
        )

        assert manager.count() == 0
        assert manager.has_device("speaker-1") is False

    def test_unregister_active_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                is_default=True
            )
        )

        manager.unregister_device(
            "speaker-1"
        )

        assert manager.get_active_device() is None

    def test_available_devices(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                device_id="speaker-1",
                available=True,
            )
        )

        manager.register_device(
            self.create_device(
                device_id="speaker-2",
                available=False,
            )
        )

        devices = manager.get_available_devices()

        assert len(devices) == 1
        assert (
            devices[0].get_device_id()
            == "speaker-1"
        )

    def test_set_active_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                device_id="speaker-1"
            )
        )

        manager.register_device(
            self.create_device(
                device_id="headphones-1",
                device_type=AudioOutputDevice.DEVICE_TYPE_HEADPHONES,
            )
        )

        manager.set_active_device(
            "headphones-1"
        )

        assert (
            manager.get_active_device_id()
            == "headphones-1"
        )

    def test_set_active_device_rejects_unavailable(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                available=False
            )
        )

        with pytest.raises(
            AudioOutputDeviceManagerError
        ):
            manager.set_active_device(
                "speaker-1"
            )

    def test_set_default_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                device_id="speaker-1"
            )
        )

        manager.register_device(
            self.create_device(
                device_id="speaker-2"
            )
        )

        manager.set_default_device(
            "speaker-2"
        )

        assert (
            manager.get_default_device()
            .get_device_id()
            == "speaker-2"
        )

        assert (
            manager.get_active_device_id()
            == "speaker-2"
        )

    def test_only_one_default_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                device_id="speaker-1",
                is_default=True,
            )
        )

        manager.register_device(
            self.create_device(
                device_id="speaker-2"
            )
        )

        manager.set_default_device(
            "speaker-2"
        )

        assert (
            manager.get_device("speaker-1").is_default()
            is False
        )

        assert (
            manager.get_device("speaker-2").is_default()
            is True
        )

    def test_clear_active_device(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device(
                is_default=True
            )
        )

        manager.clear_active_device()

        assert manager.get_active_device() is None

    def test_clear_devices(self):
        manager = AudioOutputDeviceManager()

        manager.register_device(
            self.create_device()
        )

        manager.clear_devices()

        assert manager.count() == 0
        assert manager.get_active_device() is None

    def test_manager_metadata(self):
        manager = AudioOutputDeviceManager()

        manager.set_metadata(
            "backend",
            "test",
        )

        assert (
            manager.get_metadata_value("backend")
            == "test"
        )

    def test_invalid_device_type_for_register(self):
        manager = AudioOutputDeviceManager()

        with pytest.raises(
            AudioOutputDeviceManagerError
        ):
            manager.register_device(
                "not-a-device"
            )

    def test_unknown_device(self):
        manager = AudioOutputDeviceManager()

        with pytest.raises(
            AudioOutputDeviceManagerError
        ):
            manager.get_device(
                "missing"
            )

    def test_invalid_device_id(self):
        manager = AudioOutputDeviceManager()

        with pytest.raises(
            AudioOutputDeviceManagerError
        ):
            manager.has_device("")