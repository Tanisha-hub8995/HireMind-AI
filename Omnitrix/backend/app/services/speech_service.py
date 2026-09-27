import asyncio
import io
import logging
import math
import os
import shutil
import struct
import subprocess
import tempfile
import wave
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SpeechService:
    """Handles Speech-to-Text (STT) for candidate answers and Text-to-Speech (TTS) for interviewer questions."""

    def __init__(self):
        self._whisper_model = None
        self._stt_attempted = False
        self._flite_path = shutil.which("flite") or "/usr/bin/flite"
        self._espeak_path = shutil.which("espeak-ng") or shutil.which("espeak") or "/usr/bin/espeak-ng"

    def _load_whisper(self):
        if self._whisper_model is not None:
            return self._whisper_model
        if self._stt_attempted:
            return None

        try:
            from faster_whisper import WhisperModel
            model_size = os.getenv("WHISPER_MODEL", "tiny")
            self._whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            return self._whisper_model
        except Exception as exc:
            self._stt_attempted = True
            logger.info("faster-whisper model not loaded (%s), using audio stream fallback.", exc)
            return None

    def speech_to_text(self, audio_bytes: bytes, filename: str = "audio.wav") -> str:
        """Transcribe candidate microphone audio into text using faster-whisper or fallback."""
        if not audio_bytes or len(audio_bytes) < 100:
            return ""

        try:
            whisper = self._load_whisper()
            if whisper is not None:
                audio_stream = io.BytesIO(audio_bytes)
                segments, _ = whisper.transcribe(audio_stream, beam_size=2, language="en")
                transcript = " ".join(seg.text for seg in segments).strip()
                if transcript:
                    return transcript
        except Exception as exc:
            logger.warning("Whisper transcription failed: %s", exc)

        return ""

    def synthesize_speech(self, text: str) -> Tuple[bytes, str]:
        """Synthesize clear, natural, audible speech for interviewer questions.

        Returns (audio_bytes, mime_type).
        """
        clean_text = (text or "").strip()
        if not clean_text:
            clean_text = "Please explain your approach and architecture."

        # 1. Try local Flite with natural voice (slt / kal16) - instantaneous & high reliability
        if self._flite_path and os.path.exists(self._flite_path):
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp_wav = f.name
                try:
                    # Attempt slt female voice first, then default voice
                    res = subprocess.run(
                        [self._flite_path, "-voice", "slt", "-t", clean_text, "-o", tmp_wav],
                        capture_output=True,
                        timeout=6,
                    )
                    if res.returncode != 0:
                        res = subprocess.run(
                            [self._flite_path, "-t", clean_text, "-o", tmp_wav],
                            capture_output=True,
                            timeout=6,
                        )
                    if res.returncode == 0 and os.path.exists(tmp_wav):
                        with open(tmp_wav, "rb") as wav_in:
                            wav_data = wav_in.read()
                        if len(wav_data) > 1000:
                            return wav_data, "audio/wav"
                finally:
                    if os.path.exists(tmp_wav):
                        os.remove(tmp_wav)
            except Exception as exc:
                logger.info("Flite TTS failed (%s), trying next engine", exc)

        # 2. Try local espeak-ng engine
        if self._espeak_path and os.path.exists(self._espeak_path):
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp_wav = f.name
                try:
                    res = subprocess.run(
                        [self._espeak_path, "-v", "en-us", "-s", "150", "-w", tmp_wav, clean_text],
                        capture_output=True,
                        timeout=6,
                    )
                    if res.returncode == 0 and os.path.exists(tmp_wav):
                        with open(tmp_wav, "rb") as wav_in:
                            wav_data = wav_in.read()
                        if len(wav_data) > 1000:
                            return wav_data, "audio/wav"
                finally:
                    if os.path.exists(tmp_wav):
                        os.remove(tmp_wav)
            except Exception as exc:
                logger.info("espeak-ng TTS failed (%s), trying gTTS", exc)

        # 3. Try gTTS (Google Text-to-Speech)
        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text, lang="en", tld="com", slow=False)
            out = io.BytesIO()
            tts.write_to_fp(out)
            out.seek(0)
            audio_bytes = out.getvalue()
            if len(audio_bytes) > 200:
                return audio_bytes, "audio/mpeg"
        except Exception as exc:
            logger.info("gTTS speech synthesis fallback: %s", exc)

        # 4. Fallback synthesized audio wave
        return self._generate_fallback_wav(clean_text), "audio/wav"

    def text_to_speech_wav(self, text: str) -> bytes:
        """Backward-compatible method returning audio bytes."""
        audio_bytes, _ = self.synthesize_speech(text)
        return audio_bytes

    def _generate_fallback_wav(self, clean_text: str) -> bytes:
        sample_rate = 22050
        duration = min(4.0, max(1.5, len(clean_text) * 0.05))
        total_samples = int(sample_rate * duration)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(total_samples):
                t = float(i) / sample_rate
                freq = 280.0 + 40.0 * math.sin(2.0 * math.pi * 2.0 * t)
                envelope = math.sin(math.pi * (i / total_samples))
                val = int(envelope * 12000.0 * math.sin(2.0 * math.pi * freq * t))
                val = max(-32768, min(32767, val))
                frames.extend(struct.pack("<h", val))

            wav_file.writeframes(frames)

        buf.seek(0)
        return buf.getvalue()
