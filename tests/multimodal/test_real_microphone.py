"""
Ultron Real Microphone Smoke Test

Manual hardware test for MicrophoneCapture.

Version: v0.59
"""

import time

from modules.multimodal.capture.microphone_capture import (
    MicrophoneCapture,
    AudioCaptureError,
)


def main() -> None:
    print("\n🎤 Ultron Real Microphone Smoke Test")
    print("=" * 45)

    capture = MicrophoneCapture()

    print("\n[1] Checking microphone availability...")

    if not capture.is_available():
        print("❌ No microphone input device available.")
        return

    print("✅ Microphone available.")

    print("\n[2] Microphone device information:")

    try:
        device_info = capture.get_device_info()

        for key, value in device_info.items():
            print(f"   {key}: {value}")

    except AudioCaptureError as exc:
        print(f"❌ Failed to get device information: {exc}")
        return

    print("\n[3] Starting recording...")
    print("🎙️ Speak normally for 3 seconds...")

    try:
        capture.start()

        print("🔴 Recording...")

        time.sleep(3)

        print("⏹️ Stopping recording...")

        voice_input = capture.stop()

    except AudioCaptureError as exc:
        print(f"\n❌ Microphone capture failed: {exc}")
        return

    print("\n[4] Capture successful!")
    print("-" * 45)

    print(f"Source       : {voice_input.get_metadata('source')}")
    print(f"Format       : {voice_input.get_format()}")
    print(f"Sample Rate  : {voice_input.get_sample_rate()}")
    print(f"Channels     : {voice_input.get_channels()}")
    print(f"Duration     : {voice_input.get_duration():.2f}s")
    print(f"Audio Bytes  : {len(voice_input.get_audio_data())}")

    print("\n✅ REAL MICROPHONE TEST PASSED")
    print("=" * 45)


if __name__ == "__main__":
    main()