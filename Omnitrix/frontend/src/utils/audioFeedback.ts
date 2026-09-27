// Audio feedback engine for microphone chimes and high-reliability speech playback

class AudioFeedbackEngine {
  private ctx: AudioContext | null = null;

  private getContext(): AudioContext {
    if (!this.ctx || this.ctx.state === 'closed') {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      this.ctx = new AudioCtx();
    }
    if (this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
    return this.ctx;
  }

  // Pleasant chime when mic turns ON (Siri / Google Assistant style)
  playMicOnChime() {
    try {
      const ctx = this.getContext();
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(523.25, now); // C5
      osc.frequency.exponentialRampToValueAtTime(783.99, now + 0.12); // G5

      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {
      console.warn('Audio chime failed:', e);
    }
  }

  // Gentle chime when mic turns OFF
  playMicOffChime() {
    try {
      const ctx = this.getContext();
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(783.99, now); // G5
      osc.frequency.exponentialRampToValueAtTime(523.25, now + 0.12); // C5

      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.3);
    } catch (e) {
      console.warn('Audio chime failed:', e);
    }
  }

  // Play natural voice speaking
  speak(text: string, onStart?: () => void, onEnd?: () => void) {
    if (!text || !text.trim()) return;

    if (onStart) onStart();

    // 1. Try backend TTS endpoint directly
    try {
      const cleanText = text.replace(/[*#•_-]/g, ' ').replace(/\s+/g, ' ').trim();
      const audioUrl = `http://localhost:8000/interviews/tts?text=${encodeURIComponent(cleanText)}`;
      const audio = new Audio(audioUrl);
      audio.volume = 1.0;
      
      let fallbackTriggered = false;
      const timer = setTimeout(() => {
        if (!fallbackTriggered) {
          fallbackTriggered = true;
          this.speakFallback(cleanText, onStart, onEnd);
        }
      }, 1000);

      audio.onplay = () => {
        clearTimeout(timer);
        if (onStart) onStart();
      };

      audio.onended = () => {
        if (onEnd) onEnd();
      };

      audio.onerror = () => {
        if (!fallbackTriggered) {
          fallbackTriggered = true;
          clearTimeout(timer);
          this.speakFallback(cleanText, onStart, onEnd);
        }
      };

      audio.play().catch(() => {
        if (!fallbackTriggered) {
          fallbackTriggered = true;
          clearTimeout(timer);
          this.speakFallback(cleanText, onStart, onEnd);
        }
      });
    } catch {
      this.speakFallback(text, onStart, onEnd);
    }
  }

  speakFallback(text: string, onStart?: () => void, onEnd?: () => void) {
    if (!('speechSynthesis' in window)) {
      if (onEnd) onEnd();
      return;
    }
    try {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();

      const utt = new SpeechSynthesisUtterance(text);
      utt.rate = 1.0;
      utt.volume = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const voice = voices.find(v => v.lang === 'en-US' || v.lang.startsWith('en')) || voices[0];
      if (voice) utt.voice = voice;

      utt.onstart = () => { if (onStart) onStart(); };
      utt.onend = () => { if (onEnd) onEnd(); };
      utt.onerror = () => { if (onEnd) onEnd(); };

      window.speechSynthesis.speak(utt);
    } catch {
      if (onEnd) onEnd();
    }
  }

  stop() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }
}

export const audioFeedback = new AudioFeedbackEngine();
