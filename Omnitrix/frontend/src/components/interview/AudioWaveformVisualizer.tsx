import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Mic, Volume2, Activity } from 'lucide-react';

interface AudioWaveformVisualizerProps {
  isRecording: boolean;
  transcript?: string;
}

export const AudioWaveformVisualizer: React.FC<AudioWaveformVisualizerProps> = ({
  isRecording,
  transcript
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animFrameIdRef = useRef<number | null>(null);
  const [decibels, setDecibels] = useState<number>(42);

  useEffect(() => {
    if (!isRecording) {
      if (animFrameIdRef.current) {
        cancelAnimationFrame(animFrameIdRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
        streamRef.current = null;
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
        audioContextRef.current = null;
      }
      return;
    }

    let isMounted = true;

    // Connect to real microphone audio input for live wave visualization
    const initAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (!isMounted) {
          stream.getTracks().forEach(t => t.stop());
          return;
        }
        streamRef.current = stream;

        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioCtx();
        audioContextRef.current = ctx;

        const analyser = ctx.createAnalyser();
        analyser.fftSize = 64;
        analyserRef.current = analyser;

        const source = ctx.createMediaStreamSource(stream);
        source.connect(analyser);
        sourceRef.current = source;

        const canvas = canvasRef.current;
        if (!canvas) return;
        const cCtx = canvas.getContext('2d');
        if (!cCtx) return;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
          if (!isMounted) return;
          animFrameIdRef.current = requestAnimationFrame(draw);

          analyser.getByteFrequencyData(dataArray);

          // Calculate average decibel
          let sum = 0;
          for (let i = 0; i < bufferLength; i++) {
            sum += dataArray[i];
          }
          const avg = sum / bufferLength;
          setDecibels(Math.round(35 + (avg / 255) * 45));

          const width = canvas.width;
          const height = canvas.height;
          cCtx.clearRect(0, 0, width, height);

          // Draw wavy flowing frequency bars
          const barWidth = (width / bufferLength) * 1.5;
          let x = 0;

          // Gradient
          const gradient = cCtx.createLinearGradient(0, height, 0, 0);
          gradient.addColorStop(0, '#00f2fe');
          gradient.addColorStop(0.5, '#6366f1');
          gradient.addColorStop(1, '#10b981');

          cCtx.fillStyle = gradient;

          for (let i = 0; i < bufferLength; i++) {
            // Apply smoothing curve
            const value = dataArray[i];
            const percent = value / 255;
            const barHeight = Math.max(6, percent * height * 0.95);

            // Centered wave symmetry
            const y = (height - barHeight) / 2;

            // Draw rounded bar
            cCtx.beginPath();
            cCtx.roundRect(x, y, barWidth - 2, barHeight, 4);
            cCtx.fill();

            x += barWidth;
          }
        };

        draw();
      } catch (err) {
        console.warn('Real mic stream not available for canvas, using dynamic wave simulation:', err);
        // Fallback to dynamic Fourier sine wave animation
        const canvas = canvasRef.current;
        if (!canvas) return;
        const cCtx = canvas.getContext('2d');
        if (!cCtx) return;

        let phase = 0;
        const drawSimulated = () => {
          if (!isMounted) return;
          animFrameIdRef.current = requestAnimationFrame(drawSimulated);

          phase += 0.08;
          const width = canvas.width;
          const height = canvas.height;
          cCtx.clearRect(0, 0, width, height);

          const bars = 28;
          const barWidth = width / bars;
          const gradient = cCtx.createLinearGradient(0, height, 0, 0);
          gradient.addColorStop(0, '#00f2fe');
          gradient.addColorStop(0.6, '#6366f1');
          gradient.addColorStop(1, '#10b981');
          cCtx.fillStyle = gradient;

          for (let i = 0; i < bars; i++) {
            const wave = Math.sin(phase + (i * 0.35)) * 0.5 + 0.5;
            const barHeight = 8 + wave * (height * 0.75);
            const y = (height - barHeight) / 2;

            cCtx.beginPath();
            cCtx.roundRect(i * barWidth + 2, y, barWidth - 4, barHeight, 4);
            cCtx.fill();
          }
          setDecibels(Math.round(42 + Math.sin(phase * 2) * 12));
        };

        drawSimulated();
      }
    };

    initAudio();

    return () => {
      isMounted = false;
      if (animFrameIdRef.current) cancelAnimationFrame(animFrameIdRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, [isRecording]);

  if (!isRecording) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0, y: -10 }}
      animate={{ opacity: 1, height: 'auto', y: 0 }}
      exit={{ opacity: 0, height: 0, y: -10 }}
      transition={{ duration: 0.25 }}
      className="p-4 rounded-2xl bg-gradient-to-r from-cyan-950/40 via-indigo-950/40 to-slate-900 border border-cyan-500/40 shadow-xl overflow-hidden space-y-3"
    >
      {/* Top Status Ribbon */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-400" />
          </span>
          <span className="font-bold text-cyan-300 uppercase tracking-wider font-mono text-[11px]">
            Microphone Live • Voice Wavy Telemetry
          </span>
        </div>

        <div className="flex items-center space-x-3 text-[11px] font-mono text-slate-300">
          <span className="flex items-center space-x-1">
            <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{decibels} dB</span>
          </span>
          <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold">
            Recording
          </span>
        </div>
      </div>

      {/* Dynamic Animated Waveform Canvas */}
      <div className="w-full h-16 bg-slate-950/80 rounded-xl border border-white/[0.08] flex items-center justify-center p-2 relative overflow-hidden">
        {/* Ambient subtle glow background */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-indigo-500/10 to-emerald-500/10 pointer-events-none" />
        
        <canvas
          ref={canvasRef}
          width={480}
          height={64}
          className="w-full h-full object-contain relative z-10"
        />
      </div>

      {/* Real-time Candidate Dictation Preview */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between text-[11px] text-slate-300 gap-1.5 pt-1 border-t border-white/[0.06]">
        <div className="flex items-center space-x-1.5 overflow-hidden">
          <Activity className="w-3.5 h-3.5 text-cyan-400 shrink-0 animate-pulse" />
          <span className="font-semibold text-cyan-300">Live Voice Transcribed:</span>
          <span className="text-white font-mono truncate italic">
            "{transcript ? (transcript.length > 70 ? '...' + transcript.slice(-70) : transcript) : 'Listening for your voice...'}"
          </span>
        </div>
        <span className="font-mono text-emerald-400 font-bold shrink-0 self-start sm:self-auto flex items-center space-x-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          <span>STT Converting Live</span>
        </span>
      </div>
    </motion.div>
  );
};
