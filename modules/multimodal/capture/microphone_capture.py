"""
Ultron Microphone Capture

Provides the concrete microphone-based AudioCapture implementation.

Version: v0.59
"""

from __future__ import annotations

from io import BytesIO
import threading
import wave
from typing import Any, Dict

import sounddevice as sd

from modules.multimodal.audio_capture import AudioCapture, AudioCaptureError
from modules.multimodal.voice_input import VoiceInput


class MicrophoneCapture(AudioCapture):
    """
    Concrete AudioCapture implementation using a system microphone.

    Responsibilities:
        - Detect microphone availability
        - Start microphone recording
        - Collect raw PCM audio
        - Convert captured PCM audio to WAV
        - Return the recording as VoiceInput

    This class does NOT perform speech-to-text or runtime execution.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 16000,
        channels: int = 1,
        device: int | str | None = None,
        metadata: Dict[str, Any] | None = None,
        backend: Any | None = None,
    ) -> None:
        super().__init__(
            sample_rate=sample_rate,
            channels=channels,
            metadata=metadata,
        )

        if isinstance(device, int) and device < 0:
            raise ValueError("device must be non-negative")

        if device is not None and not isinstance(device, (int, str)):
            raise ValueError("device must be an integer, string, or None")

        self._device = device
        self._backend = backend or sd

        self._stream: Any | None = None
        self._audio_buffer = bytearray()
        self._captured_frames = 0
        self._capture_error: Exception | None = None

        self._lock = threading.Lock()

    def start(self) -> None:
        """
        Start microphone recording.

        Raises:
            AudioCaptureError: If the microphone cannot be started.
        """
        if self.is_recording():
            return

        self._reset_capture_buffer()

        try:
            self._stream = self._backend.RawInputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="int16",
                device=self._device,
                callback=self._callback,
            )

            self._stream.start()

        except Exception as exc:
            self._stream = None
            raise AudioCaptureError(
                f"Failed to start microphone capture: {exc}"
            ) from exc

    def stop(self) -> VoiceInput:
        """
        Stop microphone recording and return the captured audio.

        Returns:
            VoiceInput: Captured audio encoded as WAV.

        Raises:
            AudioCaptureError: If capture fails or no audio was captured.
        """
        if not self.is_recording():
            raise AudioCaptureError(
                "Microphone capture is not currently recording"
            )

        stream = self._stream

        try:
            stream.stop()
            stream.close()
        except Exception as exc:
            raise AudioCaptureError(
                f"Failed to stop microphone capture: {exc}"
            ) from exc
        finally:
            self._stream = None

        if self._capture_error is not None:
            error = self._capture_error
            self._capture_error = None
            raise AudioCaptureError(
                f"Microphone capture failed: {error}"
            ) from error

        with self._lock:
            pcm_data = bytes(self._audio_buffer)
            captured_frames = self._captured_frames

        if not pcm_data or captured_frames <= 0:
            raise AudioCaptureError(
                "Microphone capture produced no audio"
            )

        wav_data = self._create_wav(pcm_data)

        duration = captured_frames / self._sample_rate

        capture_metadata = self.get_metadata()
        capture_metadata.update(
            {
                "source": "microphone",
                "device": self._device,
                "sample_width": 2,
                "encoding": "PCM",
            }
        )

        voice_input = VoiceInput(
            wav_data,
            source="microphone",
            audio_format="wav",
            sample_rate=self._sample_rate,
            channels=self._channels,
            duration=duration,
            metadata=capture_metadata,
        )

        self._set_last_capture(voice_input)

        return voice_input

    def is_recording(self) -> bool:
        """Return whether microphone capture is currently active."""
        return self._stream is not None

    def is_available(self) -> bool:
        """
        Return whether a usable microphone is available.

        The configured device is checked when provided; otherwise the
        default input device is queried.
        """
        try:
            info = self._backend.query_devices(
                self._device,
                "input",
            )

            if not info:
                return False

            return info.get("max_input_channels", 0) > 0

        except Exception:
            return False

    def get_device_info(self) -> Dict[str, Any]:
        """
        Return information about the configured/default microphone.

        Raises:
            AudioCaptureError: If device information cannot be retrieved.
        """
        try:
            info = self._backend.query_devices(
                self._device,
                "input",
            )

            if not info:
                raise AudioCaptureError(
                    "No microphone device information available"
                )

            return dict(info)

        except AudioCaptureError:
            raise

        except Exception as exc:
            raise AudioCaptureError(
                f"Failed to query microphone device: {exc}"
            ) from exc

    def get_device(self) -> int | str | None:
        """Return the configured microphone device."""
        return self._device

    def set_device(self, device: int | str | None) -> None:
        """
        Set the microphone device.

        The device cannot be changed while recording.
        """
        if self.is_recording():
            raise AudioCaptureError(
                "Cannot change microphone device while recording"
            )

        if isinstance(device, int) and device < 0:
            raise ValueError("device must be non-negative")

        if device is not None and not isinstance(device, (int, str)):
            raise ValueError("device must be an integer, string, or None")

        self._device = device

    def reset(self) -> None:
        """
        Reset the current capture state.

        The microphone must not be actively recording.
        """
        if self.is_recording():
            raise AudioCaptureError(
                "Cannot reset microphone capture while recording"
            )

        self._reset_capture_buffer()
        self.reset_last_capture()

    def _callback(
        self,
        indata: bytes,
        frames: int,
        time: Any,
        status: Any,
    ) -> None:
        """
        Receive raw PCM audio frames from sounddevice.
        """
        if status:
            self._capture_error = RuntimeError(str(status))

        if not indata or frames <= 0:
            return

        with self._lock:
            self._audio_buffer.extend(indata)
            self._captured_frames += frames

    def _create_wav(self, pcm_data: bytes) -> bytes:
        """
        Convert raw PCM int16 audio into a WAV container.
        """
        output = BytesIO()

        try:
            with wave.open(output, "wb") as wav_file:
                wav_file.setnchannels(self._channels)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self._sample_rate)
                wav_file.writeframes(pcm_data)

            return output.getvalue()

        except Exception as exc:
            raise AudioCaptureError(
                f"Failed to create WAV audio: {exc}"
            ) from exc

    def _reset_capture_buffer(self) -> None:
        """Clear the current in-memory capture buffer."""
        with self._lock:
            self._audio_buffer.clear()
            self._captured_frames = 0

        self._capture_error = None