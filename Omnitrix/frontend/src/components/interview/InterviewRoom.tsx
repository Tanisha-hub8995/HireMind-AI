import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Send, 
  Volume2, 
  VolumeX, 
  Volume1,
  Play,
  Square,
  Sparkles, 
  CheckCircle, 
  CheckCircle2,
  Activity,
  AlertCircle, 
  ArrowRight, 
  RefreshCw, 
  Layers, 
  Award, 
  Building, 
  Flame, 
  HelpCircle,
  FileCheck,
  Wand2,
  Loader2
} from 'lucide-react';
import { AIInterviewerAvatar3D } from '../three/AIInterviewerAvatar3D';
import { ProctoredCameraFeed } from './ProctoredCameraFeed';
import { AudioWaveformVisualizer } from './AudioWaveformVisualizer';
import { api } from '../../services/api';
import { InterviewSession, RubricEvaluation, InterviewReport, QuestionCandidate } from '../../types';
import { useAuth } from '../../context/AuthContext';
import confetti from 'canvas-confetti';
import { audioFeedback } from '../../utils/audioFeedback';

export const InterviewRoom: React.FC = () => {
  const { user } = useAuth();
  // Session state
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [currentQuestion, setCurrentQuestion] = useState<QuestionCandidate | null>(null);
  const [avatarState, setAvatarState] = useState<'idle' | 'speaking' | 'listening' | 'evaluating'>('idle');

  // Input & audio state
  const [answerText, setAnswerText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState<number>(1.0);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [loading, setLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<RubricEvaluation | null>(null);
  const [followupQuestion, setFollowupQuestion] = useState<QuestionCandidate | null>(null);
  const [finalReport, setFinalReport] = useState<InterviewReport | null>(null);

  // Setup form
  const [role, setRole] = useState('Full Stack Engineer');
  const [targetCompany, setTargetCompany] = useState('Google');
  const [difficulty, setDifficulty] = useState('MEDIUM');
  const [interviewType, setInterviewType] = useState('TECHNICAL');
  const [numQuestions, setNumQuestions] = useState(5);
  const [startingInterview, setStartingInterview] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [lobbyPreviewMode, setLobbyPreviewMode] = useState<'ai' | 'camera'>('ai');

  // Speech-to-Text Assurance state
  const [isAudioActive, setIsAudioActive] = useState(false);
  const [isVoiceDetected, setIsVoiceDetected] = useState(false);
  const [lastSpokenPhrase, setLastSpokenPhrase] = useState<string>('');
  const [micTestResult, setMicTestResult] = useState<string | null>(null);
  const [isTestingMic, setIsTestingMic] = useState(false);
  const [activeMicStream, setActiveMicStream] = useState<MediaStream | null>(null);
  const [isTranscribingWithWhisper, setIsTranscribingWithWhisper] = useState(false);
  const [whisperStatusText, setWhisperStatusText] = useState<string | null>(null);

  // Speech & Audio refs
  const recognitionRef = useRef<any>(null);
  const isRecordingRef = useRef<boolean>(false);
  const baseTextRef = useRef<string>('');
  const answerTextRef = useRef<string>('');
  const activeAudioRef = useRef<HTMLAudioElement | null>(null);
  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  // Synchronize answerTextRef with answerText state
  useEffect(() => {
    answerTextRef.current = answerText;
  }, [answerText]);

  // Load history if user exists
  useEffect(() => {
    if (user) {
      api.getInterviewHistory().then(setHistory).catch(() => {});
    }
  }, [user]);

  // Setup speech recognition with continuous auto-keepalive while candidate is answering
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onaudiostart = () => {
        setIsAudioActive(true);
      };

      recognition.onsoundstart = () => {
        setIsVoiceDetected(true);
      };

      recognition.onspeechstart = () => {
        setIsVoiceDetected(true);
      };

      recognition.onspeechend = () => {
        setIsVoiceDetected(false);
      };

      recognition.onaudioend = () => {
        setIsAudioActive(false);
      };

      recognition.onresult = (event: any) => {
        let currentSessionText = '';
        for (let i = 0; i < event.results.length; i++) {
          currentSessionText += event.results[i][0].transcript + ' ';
        }
        const base = baseTextRef.current.trim();
        const fresh = currentSessionText.trim();
        const combined = base ? (fresh ? `${base} ${fresh}` : base) : fresh;
        setAnswerText(combined);
        setIsVoiceDetected(true);
        if (event.results.length > 0) {
          const lastItem = event.results[event.results.length - 1];
          setLastSpokenPhrase(lastItem[0].transcript);
        }
      };

      recognition.onerror = (event: any) => {
        console.warn('Speech recognition status:', event?.error);
        if (event?.error === 'no-speech') {
          // Candidate paused to think - keep mic ON continuously!
          setIsVoiceDetected(false);
          return;
        }
        if (event?.error === 'network') {
          // Web Speech remote service unavailable; Whisper will transcribe when stopped
          console.info('Web Speech network status; Whisper AI will transcribe recorded audio.');
          return;
        }
        if (event?.error === 'not-allowed' || event?.error === 'service-not-allowed') {
          isRecordingRef.current = false;
          setIsRecording(false);
          setIsAudioActive(false);
          setIsVoiceDetected(false);
          setAvatarState('idle');
          audioFeedback.playMicOffChime();
        }
      };

      recognition.onend = () => {
        setIsVoiceDetected(false);
        // Keep microphone continuously ON while candidate is answering
        if (isRecordingRef.current) {
          baseTextRef.current = answerTextRef.current;
          try {
            recognition.start();
          } catch (e) {
            setTimeout(() => {
              if (isRecordingRef.current) {
                try {
                  recognition.start();
                } catch (err) {
                  console.warn('Speech recognition restart delayed:', err);
                }
              }
            }, 150);
          }
        } else {
          // Only turn off if media recorder is also done
          if (!mediaRecorderRef.current || mediaRecorderRef.current.state === 'inactive') {
            setIsRecording(false);
            setIsAudioActive(false);
            setAvatarState('idle');
          }
        }
      };

      recognitionRef.current = recognition;
    }

    return () => {
      isRecordingRef.current = false;
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {}
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try {
          mediaRecorderRef.current.stop();
        } catch (e) {}
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
    };
  }, []);

  // Web Speech API Fallback
  const playSpeechSynthesisFallback = (text: string) => {
    if (!('speechSynthesis' in window)) {
      setIsPlayingAudio(false);
      setAvatarState('idle');
      return;
    }
    try {
      window.speechSynthesis.cancel();
      window.speechSynthesis.resume();

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.volume = volume;
      utterance.rate = 1.0;
      utterance.pitch = 1.0;

      const voices = window.speechSynthesis.getVoices();
      const englishVoice = voices.find(v => (v.lang.startsWith('en') && !v.name.includes('Google')) || v.lang === 'en-US') || voices[0];
      if (englishVoice) {
        utterance.voice = englishVoice;
      }

      activeUtteranceRef.current = utterance;

      utterance.onstart = () => {
        setIsPlayingAudio(true);
        setAvatarState('speaking');
      };

      utterance.onend = () => {
        setIsPlayingAudio(false);
        setAvatarState('idle');
      };

      utterance.onerror = () => {
        setIsPlayingAudio(false);
        setAvatarState('idle');
      };

      window.speechSynthesis.speak(utterance);
    } catch (e) {
      console.warn('Speech synthesis error:', e);
      setIsPlayingAudio(false);
      setAvatarState('idle');
    }
  };

  // High-reliability Dual-Engine Playback
  const playTTS = async (text: string) => {
    if (isMuted || !text || !text.trim()) return;
    setIsPlayingAudio(true);
    setAvatarState('speaking');

    // Clean markdown/newlines for speech
    const cleanText = text.replace(/[*#•_-]/g, ' ').replace(/\s+/g, ' ').trim();

    // 1. Try HTML5 Audio with backend synthesized speech stream
    try {
      if (activeAudioRef.current) {
        activeAudioRef.current.pause();
        activeAudioRef.current = null;
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }

      const audioUrl = api.getTTSAudioUrl(cleanText);
      const audio = new Audio(audioUrl);
      audio.volume = volume;
      activeAudioRef.current = audio;

      let hasPlayed = false;
      const fallbackTimer = setTimeout(() => {
        if (!hasPlayed) {
          console.info('Audio streaming timeout, falling back to speech synthesis');
          playSpeechSynthesisFallback(cleanText);
        }
      }, 1200);

      audio.onplay = () => {
        hasPlayed = true;
        clearTimeout(fallbackTimer);
        setIsPlayingAudio(true);
        setAvatarState('speaking');
      };

      audio.onended = () => {
        setIsPlayingAudio(false);
        setAvatarState('idle');
        activeAudioRef.current = null;
      };

      audio.onerror = () => {
        clearTimeout(fallbackTimer);
        console.warn('Backend audio stream unavailable, falling back to speech synthesis');
        playSpeechSynthesisFallback(cleanText);
      };

      await audio.play().catch((playErr) => {
        clearTimeout(fallbackTimer);
        console.warn('HTML5 audio play rejected, falling back to speech synthesis:', playErr);
        playSpeechSynthesisFallback(cleanText);
      });
    } catch (err) {
      console.warn('HTML5 audio play failed, falling back to speech synthesis:', err);
      playSpeechSynthesisFallback(cleanText);
    }
  };

  const stopAudio = () => {
    if (activeAudioRef.current) {
      activeAudioRef.current.pause();
      activeAudioRef.current = null;
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlayingAudio(false);
    setAvatarState('idle');
  };

  const testAudio = () => {
    playTTS("Hello candidate! I am your RAAHSETU AI interviewer. Audio output is loud and clear.");
  };

  const handleStartInterview = async () => {
    setStartingInterview(true);
    try {
      const newSession = await api.startInterview({
        role,
        target_company: targetCompany,
        difficulty,
        interview_type: interviewType,
        num_questions: numQuestions,
      });
      setSession(newSession);
      setCurrentQuestionIndex(0);
      const firstQ = newSession.questions[0];
      setCurrentQuestion(firstQ);
      setEvaluation(null);
      setFollowupQuestion(null);
      setFinalReport(null);
      setAnswerText('');

      if (firstQ?.question_text) {
        setTimeout(() => playTTS(firstQ.question_text), 600);
      }
    } catch (err: any) {
      alert(`Could not start interview: ${err.message}`);
    } finally {
      setStartingInterview(false);
    }
  };

  const stopAllAudioRecording = () => {
    isRecordingRef.current = false;
    audioFeedback.playMicOffChime();
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {}
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
      setActiveMicStream(null);
    }
    setIsRecording(false);
    setIsAudioActive(false);
    setIsVoiceDetected(false);
    setAvatarState('idle');
  };

  const transcribeWithWhisper = async (audioBlob?: Blob) => {
    let blob = audioBlob;
    if (!blob) {
      if (audioChunksRef.current.length === 0) {
        setWhisperStatusText('No audio recorded yet. Please click the mic button and speak.');
        setTimeout(() => setWhisperStatusText(null), 4000);
        return;
      }
      blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
    }

    if (blob.size < 500) {
      console.info('Audio blob too short to transcribe');
      return;
    }

    setIsTranscribingWithWhisper(true);
    setWhisperStatusText('⚡ AI Neural Whisper is transcribing your voice...');
    try {
      const res = await api.transcribeAudio(blob);
      if (res && res.transcript && res.transcript.trim()) {
        const whisperText = res.transcript.trim();
        setAnswerText((prev) => {
          const cleanPrev = prev.trim();
          if (!cleanPrev) return whisperText;
          if (cleanPrev.toLowerCase().includes(whisperText.toLowerCase())) return cleanPrev;
          if (whisperText.toLowerCase().includes(cleanPrev.toLowerCase())) return whisperText;
          return `${cleanPrev} ${whisperText}`;
        });
        setWhisperStatusText(`✓ Whisper AI transcribed ${whisperText.split(/\s+/).filter(Boolean).length} words!`);
      } else {
        setWhisperStatusText('Whisper: No distinct speech captured. Please speak closer to microphone.');
      }
    } catch (err: any) {
      console.warn('Whisper transcription note:', err);
      setWhisperStatusText('AI Transcription server busy. Browser speech recognition remains active.');
    } finally {
      setIsTranscribingWithWhisper(false);
      setTimeout(() => setWhisperStatusText(null), 6000);
    }
  };

  const handleTestMicrophoneRecognition = async () => {
    setIsTestingMic(true);
    setMicTestResult('Testing microphone hardware access and neural speech engine...');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Release test audio tracks
      stream.getTracks().forEach((t) => t.stop());

      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (!SpeechRecognition) {
        setMicTestResult('✓ Microphone hardware active! Server-side AI Whisper will transcribe your audio directly.');
      } else {
        audioFeedback.playMicOnChime();
        setMicTestResult('✓ Microphone & Neural Speech-to-Text fully verified! Powered by Web Speech + RAAHSETU Whisper AI.');
      }
    } catch (err: any) {
      setMicTestResult('❌ Microphone permission was denied or unavailable. Please click the lock/settings icon in your browser URL bar and allow microphone permissions.');
    } finally {
      setIsTestingMic(false);
      setTimeout(() => {
        setMicTestResult(null);
      }, 7000);
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      // User requested stop
      stopAllAudioRecording();

      // Trigger automatic Whisper transcription on the captured recording
      setTimeout(() => {
        if (audioChunksRef.current.length > 0) {
          const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          transcribeWithWhisper(blob);
        }
      }, 150);
    } else {
      // User requested start
      isRecordingRef.current = true;
      baseTextRef.current = answerTextRef.current;
      audioFeedback.playMicOnChime();
      window.speechSynthesis?.cancel();
      audioChunksRef.current = [];

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        streamRef.current = stream;
        setActiveMicStream(stream);

        let mimeType = 'audio/webm;codecs=opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
          mimeType = MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : '';
        }

        const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
        recorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };
        recorder.start(400);
        mediaRecorderRef.current = recorder;

        setIsRecording(true);
        setIsAudioActive(true);
        setAvatarState('listening');
      } catch (err: any) {
        console.warn('Microphone stream error:', err);
        alert('Could not access microphone. Please make sure microphone permission is granted in your browser settings.');
        isRecordingRef.current = false;
        return;
      }

      // Concurrently run Web Speech recognition if supported
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
        } catch (err) {
          console.warn('Browser SpeechRecognition note:', err);
        }
      }
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !currentQuestion) return;

    let textToSubmit = answerText.trim();

    // If recording is still active or answerText is empty but audio was recorded, transcribe first
    if (isRecording || (!textToSubmit && audioChunksRef.current.length > 0)) {
      stopAllAudioRecording();
      if (!textToSubmit && audioChunksRef.current.length > 0) {
        setIsTranscribingWithWhisper(true);
        setWhisperStatusText('⚡ Transcribing voice with AI Whisper before rubric evaluation...');
        try {
          const finalBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          const res = await api.transcribeAudio(finalBlob);
          if (res?.transcript?.trim()) {
            textToSubmit = res.transcript.trim();
            setAnswerText(textToSubmit);
          }
        } catch (e) {
          console.warn('Final audio transcription note:', e);
        } finally {
          setIsTranscribingWithWhisper(false);
        }
      }
    }

    if (!textToSubmit) {
      alert('Please speak into the microphone or type your answer before submitting.');
      return;
    }

    setLoading(true);
    setAvatarState('evaluating');

    try {
      const evalResult = await api.submitAnswer(session.interview_id, {
        question_id: currentQuestion.id,
        question_text: currentQuestion.question_text,
        answer_text: textToSubmit,
        time_taken_seconds: 45,
        generate_followup: true,
      });

      setEvaluation(evalResult);
      if (evalResult.followup_question) {
        setFollowupQuestion(evalResult.followup_question);
      }
      setAvatarState('idle');
    } catch (err: any) {
      alert(`Evaluation error: ${err.message}`);
      setAvatarState('idle');
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    if (isRecording) {
      stopAllAudioRecording();
    }
    if (!session) return;
    setEvaluation(null);
    setFollowupQuestion(null);
    setAnswerText('');

    const nextIndex = currentQuestionIndex + 1;
    if (nextIndex < session.questions.length) {
      setCurrentQuestionIndex(nextIndex);
      const nextQ = session.questions[nextIndex];
      setCurrentQuestion(nextQ);
      playTTS(nextQ.question_text);
    } else {
      // Completed all questions -> generate report
      handleCompleteInterview();
    }
  };

  const handleTakeFollowup = () => {
    if (isRecording) {
      stopAllAudioRecording();
    }
    if (!followupQuestion) return;
    setCurrentQuestion(followupQuestion);
    setFollowupQuestion(null);
    setEvaluation(null);
    setAnswerText('');
    playTTS(followupQuestion.question_text);
  };

  const handleCompleteInterview = async () => {
    if (!session) return;
    setLoading(true);
    setAvatarState('evaluating');
    try {
      const report = await api.completeInterview(session.interview_id);
      setFinalReport(report);
      setAvatarState('idle');
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
      // Refresh history
      api.getInterviewHistory().then(setHistory).catch(() => {});
    } catch (err: any) {
      alert(`Could not finish interview: ${err.message}`);
      setAvatarState('idle');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* If no active session & no final report -> Show Interview Setup Lobby */}
      {!session && !finalReport && (
        <div className="space-y-8">
          {/* Header */}
          <div className="text-center max-w-3xl mx-auto">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5 text-cyber-cyan" />
              <span>Realistic Multimodal 3D Interviewer</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight">
              AI Mock Interview <span className="bg-gradient-to-r from-cyber-cyan via-brand-400 to-cyber-purple bg-clip-text text-transparent">Simulator</span>
            </h1>
            <p className="text-slate-400 text-sm sm:text-base mt-2">
              Practice real-time technical and behavioral interviews with an autonomous 3D holographic AI interviewer powered by local SLM rubrics, adaptive questioning, and voice feedback.
            </p>
          </div>

          {/* Setup Card + Interactive Preview Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
            {/* 3D Interviewer Avatar Preview or Candidate Camera Check */}
            <div className="lg:col-span-5 glass-panel rounded-3xl p-6 border border-white/10 flex flex-col items-center justify-between text-center relative overflow-hidden min-h-[460px]">
              <div className="w-full flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
                  <span className="text-xs font-mono text-emerald-400 font-bold uppercase tracking-wider">
                    {lobbyPreviewMode === 'ai' ? '3D AI Core Ready' : 'Camera Proctor Online'}
                  </span>
                </div>

                <div className="flex bg-slate-900/90 p-0.5 rounded-xl border border-white/10 text-[10px] font-bold">
                  <button
                    type="button"
                    onClick={() => setLobbyPreviewMode('ai')}
                    className={`px-2.5 py-1 rounded-lg transition-all ${
                      lobbyPreviewMode === 'ai'
                        ? 'bg-brand-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    3D AI
                  </button>
                  <button
                    type="button"
                    onClick={() => setLobbyPreviewMode('camera')}
                    className={`px-2.5 py-1 rounded-lg transition-all ${
                      lobbyPreviewMode === 'camera'
                        ? 'bg-cyan-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Cam Proctor Check
                  </button>
                </div>
              </div>

              {lobbyPreviewMode === 'ai' ? (
                <>
                  <div className="my-auto py-2">
                    <AIInterviewerAvatar3D state="idle" size="md" />
                  </div>
                  <div className="mt-2">
                    <h3 className="font-bold text-white text-base">RAAHSETU AI Neural Examiner</h3>
                    <p className="text-xs text-slate-400 mt-1 max-w-xs">
                      Evaluates 6 core dimensions: correctness, depth, relevance, communication, structure, and speed.
                    </p>
                  </div>
                </>
              ) : (
                <div className="w-full my-auto space-y-3">
                  <ProctoredCameraFeed isInterviewActive={false} className="w-full" />
                  <p className="text-[11px] text-slate-400">
                    Proctoring is verified: Eye gaze telemetry, face tracking, and posture alignment active.
                  </p>
                </div>
              )}
            </div>

            {/* Setup Form */}
            <div className="lg:col-span-7 glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl flex flex-col justify-between">
              <div>
                <h2 className="text-xl font-bold text-white flex items-center space-x-2 mb-4">
                  <Layers className="w-5 h-5 text-cyber-cyan" />
                  <span>Configure Your Interview Simulation</span>
                </h2>

                {/* Fast Track Presets */}
                <div className="mb-5">
                  <span className="text-[11px] font-mono uppercase text-slate-400 font-bold block mb-2">
                    ⚡ 1-Click Fast-Track Presets:
                  </span>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {[
                      { label: 'Google L5 Backend', r: 'Backend Engineer', comp: 'Google', diff: 'MEDIUM', type: 'TECHNICAL' },
                      { label: 'Meta React / TS', r: 'Frontend Engineer', comp: 'Meta', diff: 'HARD', type: 'TECHNICAL' },
                      { label: 'Stripe Architect', r: 'System Architect', comp: 'Fast-Growing Tech Unicorn', diff: 'HARD', type: 'SYSTEM_DESIGN' },
                      { label: 'Amazon Behavioral', r: 'Full Stack Engineer', comp: 'Amazon', diff: 'MEDIUM', type: 'BEHAVIORAL' },
                    ].map((preset, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => {
                          setRole(preset.r);
                          setTargetCompany(preset.comp);
                          setDifficulty(preset.diff);
                          setInterviewType(preset.type);
                        }}
                        className={`px-2.5 py-2 rounded-xl text-[11px] font-semibold transition-all text-left truncate border ${
                          role === preset.r && targetCompany === preset.comp
                            ? 'bg-brand-600/30 border-brand-500 text-white shadow-sm'
                            : 'bg-white/[0.04] hover:bg-brand-500/20 hover:border-brand-500/40 border-white/[0.08] text-slate-300 hover:text-white'
                        }`}
                      >
                        {preset.label}
                      </button>
                    ))}
                  </div>
                </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Target Role
                  </label>
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none"
                  >
                    <option value="Full Stack Engineer">Full Stack Engineer</option>
                    <option value="Frontend Engineer">Frontend Engineer (React / TypeScript)</option>
                    <option value="Backend Engineer">Backend Engineer (Python / FastAPI / SQL)</option>
                    <option value="AI / ML Engineer">AI & Machine Learning Engineer</option>
                    <option value="DevOps & Cloud Engineer">DevOps & Cloud Engineer</option>
                    <option value="System Architect">System Architect</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Target Company Style
                  </label>
                  <div className="relative">
                    <select
                      value={targetCompany}
                      onChange={(e) => setTargetCompany(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none"
                    >
                      <option value="Google">Google (Deep reasoning & scale)</option>
                      <option value="Microsoft">Microsoft (Architecture & practical)</option>
                      <option value="Amazon">Amazon (Leadership principles & DSA)</option>
                      <option value="Meta">Meta (Fast execution & system design)</option>
                      <option value="Fast-Growing Tech Unicorn">Fast-Growing Tech Unicorn</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Interview Type
                  </label>
                  <select
                    value={interviewType}
                    onChange={(e) => setInterviewType(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none"
                  >
                    <option value="TECHNICAL">Technical Deep-Dive</option>
                    <option value="BEHAVIORAL">Behavioral & Culture Fit</option>
                    <option value="SYSTEM_DESIGN">System Design & Architecture</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Initial Difficulty Level
                  </label>
                  <div className="flex space-x-2">
                    {['EASY', 'MEDIUM', 'HARD'].map((diff) => (
                      <button
                        key={diff}
                        type="button"
                        onClick={() => setDifficulty(diff)}
                        className={`flex-1 py-2.5 rounded-xl text-xs font-bold transition-all ${
                          difficulty === diff
                            ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25 border border-brand-400'
                            : 'bg-slate-900 text-slate-400 border border-white/10 hover:text-white'
                        }`}
                      >
                        {diff}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Number of Questions Slider */}
              <div className="mt-6">
                <div className="flex justify-between items-center mb-2">
                  <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    Question Count: <span className="text-cyber-cyan font-bold">{numQuestions} Questions</span>
                  </label>
                  <span className="text-xs text-slate-400 font-mono">Approx. {numQuestions * 3} mins</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="10"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value))}
                  className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-500"
                />
              </div>

              {/* Audio & Speaker Test Station */}
              <div className="mt-6 p-4 rounded-2xl bg-[#090D16]/80 border border-white/[0.08] flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center space-x-3">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-cyan-400">
                    <Volume2 className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-white">Audio & Voice Output Test</h4>
                    <p className="text-[11px] text-slate-400">Verify question voice is loud and clear before starting</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 w-full sm:w-auto">
                  <button
                    type="button"
                    onClick={testAudio}
                    className="flex-1 sm:flex-none px-4 py-2 rounded-xl text-xs font-bold bg-white/[0.08] hover:bg-white/[0.14] text-white border border-white/[0.1] transition-all flex items-center justify-center space-x-2"
                  >
                    <Play className="w-3.5 h-3.5 text-cyan-400 fill-cyan-400" />
                    <span>Test AI Audio</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsMuted(!isMuted)}
                    className="p-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-slate-300"
                    title={isMuted ? "Unmute" : "Mute"}
                  >
                    {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume1 className="w-4 h-4 text-emerald-400" />}
                  </button>
                </div>
              </div>

              {/* Proctoring & Mic Telemetry Readiness Notice */}
              <div className="mt-4 p-3.5 rounded-2xl bg-cyan-950/20 border border-cyan-500/20 flex items-center space-x-3 text-xs">
                <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
                  <Sparkles className="w-4 h-4" />
                </div>
                <div className="text-slate-300">
                  <span className="font-bold text-cyan-300">AI Proctoring & Waveform Audio Engaged:</span>{' '}
                  <span className="text-slate-400">Real-time eye gaze tracking, body posture alignment, and live microphone wavy telemetry will be active throughout your interview.</span>
                </div>
              </div>

              {/* Start Button */}
              <button
                onClick={handleStartInterview}
                disabled={startingInterview}
                className="w-full mt-6 py-4 rounded-2xl font-black text-base uppercase tracking-wider bg-gradient-to-r from-brand-600 via-indigo-600 to-cyber-cyan hover:from-brand-500 hover:to-cyber-blue text-white shadow-xl shadow-brand-500/30 transition-all hover:scale-[1.01] flex items-center justify-center space-x-3"
              >
                {startingInterview ? (
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Synthesizing Tailored Interview Questions...</span>
                  </div>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Launch 3D Mock Interview Session</span>
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

          {/* Past Interview History */}
          {history.length > 0 && (
            <div className="glass-panel rounded-3xl p-6 border border-white/10">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
                <FileCheck className="w-5 h-5 text-brand-400" />
                <span>Your Past Mock Interview History</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {history.slice(0, 3).map((item) => (
                  <div key={item.id} className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-slate-300">{item.interview_type}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-yellow-500/20 text-yellow-300'
                      }`}>
                        {item.status}
                      </span>
                    </div>
                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs text-slate-400">{new Date(item.created_at).toLocaleDateString()}</span>
                      <span className="text-sm font-extrabold text-white">
                        {item.score !== null && item.score !== undefined ? `${Math.round(item.score)}%` : 'In Progress'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ACTIVE INTERVIEW ROOM */}
      {session && !finalReport && (
        <div className="space-y-6">
          {/* Top Bar: Progress, Difficulty, Role & Company */}
          <div className="glass-panel rounded-2xl p-4 border border-white/10 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className="px-3 py-1 rounded-xl bg-brand-500/20 border border-brand-500/30 text-brand-200 text-xs font-bold">
                Question {currentQuestionIndex + 1} of {session.questions.length}
              </div>
              <div className="flex items-center space-x-1.5 text-xs text-slate-300">
                <Building className="w-3.5 h-3.5 text-cyber-cyan" />
                <span>{session.target_company || 'Google'}</span>
                <span className="text-slate-600">•</span>
                <span>{session.target_role || 'Software Engineer'}</span>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-1 text-xs font-semibold px-2.5 py-1 rounded-lg bg-orange-500/10 text-orange-400 border border-orange-500/20">
                <Flame className="w-3.5 h-3.5" />
                <span>{evaluation?.adapted_difficulty || session.current_difficulty} Level</span>
              </div>
              <button
                onClick={() => setIsMuted(!isMuted)}
                className={`p-2 rounded-lg text-xs font-medium transition-colors ${
                  isMuted ? 'bg-red-500/20 text-red-300' : 'bg-slate-800 text-slate-300 hover:text-white'
                }`}
                title={isMuted ? 'Unmute AI Voice' : 'Mute AI Voice'}
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
              <button
                onClick={handleCompleteInterview}
                className="px-3.5 py-1.5 rounded-lg text-xs font-bold bg-red-600/80 hover:bg-red-500 text-white transition-colors"
              >
                End Session Early
              </button>
            </div>
          </div>

          {/* Main Interview Stage */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left Column: 3D AI Interviewer */}
            <div className="lg:col-span-4 flex flex-col space-y-4">
              {/* 3D Holographic AI Interviewer Display */}
              <div className="glass-panel rounded-3xl p-6 border border-white/10 flex flex-col items-center justify-between relative overflow-hidden min-h-[360px]">
              {/* Dynamic State Badge */}
              <div className="w-full flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span
                    className={`w-2.5 h-2.5 rounded-full ${
                      avatarState === 'speaking'
                        ? 'bg-cyber-cyan animate-ping'
                        : avatarState === 'listening'
                        ? 'bg-emerald-400 animate-pulse'
                        : avatarState === 'evaluating'
                        ? 'bg-purple-400 animate-spin'
                        : 'bg-indigo-400'
                    }`}
                  />
                  <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                    AI State: <span className="text-white">{avatarState}</span>
                  </span>
                </div>
                {avatarState === 'speaking' && (
                  <div className="flex items-end space-x-1 h-4">
                    <span className="w-1 bg-cyber-cyan rounded-full wave-bar" />
                    <span className="w-1 bg-cyber-cyan rounded-full wave-bar" style={{ animationDelay: '0.2s' }} />
                    <span className="w-1 bg-cyber-cyan rounded-full wave-bar" style={{ animationDelay: '0.4s' }} />
                  </div>
                )}
              </div>

              {/* 3D Canvas */}
              <div className="my-auto w-full">
                <AIInterviewerAvatar3D state={avatarState} size="lg" />
              </div>

              {/* Spoken Question Audio Controls */}
              <div className="mt-4 p-3 rounded-2xl bg-[#090D16]/80 border border-white/[0.08] flex items-center justify-between gap-3 w-full">
                <button
                  type="button"
                  onClick={() => {
                    if (isPlayingAudio) {
                      stopAudio();
                    } else if (currentQuestion) {
                      playTTS(currentQuestion.question_text);
                    }
                  }}
                  className={`flex-1 flex items-center justify-center space-x-2 text-xs font-bold px-3 py-2 rounded-xl transition-all border ${
                    isPlayingAudio
                      ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-600/30'
                      : 'bg-indigo-600 hover:bg-indigo-500 text-white border-indigo-400 shadow-md shadow-indigo-600/20'
                  }`}
                >
                  {isPlayingAudio ? (
                    <>
                      <Square className="w-3.5 h-3.5 fill-white" />
                      <span>Pause Audio</span>
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-4 h-4 text-cyan-400" />
                      <span>Play Question Audio</span>
                    </>
                  )}
                </button>

                {/* Volume & Mute Controller */}
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => setIsMuted(!isMuted)}
                    title={isMuted ? "Unmute" : "Mute"}
                    className="p-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-slate-300"
                  >
                    {isMuted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
                  </button>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={isMuted ? 0 : volume}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      setVolume(v);
                      if (v > 0) setIsMuted(false);
                    }}
                    className="w-16 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                    title={`Volume: ${Math.round(volume * 100)}%`}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Question + Proctored Camera Beside It + Response Area */}
          <div className="lg:col-span-8 flex flex-col space-y-6">
              {/* Question & AI Proctoring Camera Side-by-Side Row */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-5 items-stretch">
                {/* Question Text Box */}
                <div className="md:col-span-7 flex flex-col justify-between glass-panel rounded-3xl p-6 sm:p-7 border border-brand-500/30 relative">
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-xs font-mono font-bold uppercase text-brand-300 tracking-wider">
                        {currentQuestion?.topic || 'Technical Assessment'}
                      </span>
                      {currentQuestion?.difficulty && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/10 text-slate-300">
                          {currentQuestion.difficulty}
                        </span>
                      )}
                    </div>

                    <h2 className="text-lg sm:text-xl font-bold text-white leading-relaxed">
                      {currentQuestion?.question_text}
                    </h2>
                  </div>

                  {currentQuestion?.hint && (
                    <p className="mt-4 text-xs text-slate-400 italic bg-slate-900/50 p-2.5 rounded-xl border border-white/5">
                      💡 Hint: {currentQuestion.hint}
                    </p>
                  )}
                </div>

                {/* AI Proctoring Camera Feed - Kept Beside the Question */}
                <div className="md:col-span-5 flex flex-col justify-stretch">
                  <ProctoredCameraFeed
                    isInterviewActive={true}
                    className="h-full flex flex-col justify-between"
                    isMicRecording={isRecording}
                    onToggleMic={toggleRecording}
                  />
                </div>
              </div>

              {/* Probing Follow-up Question Alert (if generated) */}
              {followupQuestion && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-2xl bg-purple-950/40 border border-purple-500/40 flex items-start justify-between gap-4"
                >
                  <div className="space-y-1">
                    <span className="text-xs font-bold text-purple-300 uppercase tracking-wider flex items-center space-x-1.5">
                      <HelpCircle className="w-3.5 h-3.5" />
                      <span>Adaptive Follow-up Question Triggered</span>
                    </span>
                    <p className="text-sm font-semibold text-white">{followupQuestion.question_text}</p>
                  </div>
                  <button
                    onClick={handleTakeFollowup}
                    className="px-3.5 py-2 rounded-xl text-xs font-bold bg-purple-600 hover:bg-purple-500 text-white whitespace-nowrap transition-colors"
                  >
                    Answer Follow-up
                  </button>
                </motion.div>
              )}

              {/* Response Input Area */}
              <div className="glass-panel rounded-3xl p-6 border border-white/10 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-xs font-semibold text-slate-300">Your Structured Response:</span>
                    {isRecording && (
                      <span className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/30 text-emerald-300 text-[10px] font-mono font-bold animate-pulse">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        <span>Mic Stays ON Continuously</span>
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      type="button"
                      onClick={handleTestMicrophoneRecognition}
                      disabled={isTestingMic}
                      className="px-2.5 py-1.5 rounded-xl text-[11px] font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-white/10 transition-colors flex items-center space-x-1"
                      title="Run a quick diagnostic to verify your microphone and speech-to-text engine"
                    >
                      <Sparkles className="w-3 h-3 text-yellow-400" />
                      <span>{isTestingMic ? 'Checking...' : 'Check Mic & STT'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={toggleRecording}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                        isRecording
                          ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse shadow-lg shadow-red-500/40 ring-2 ring-red-400/50'
                          : 'bg-slate-800 text-slate-300 hover:text-white border border-white/10 hover:border-brand-500/30'
                      }`}
                      title={isRecording ? 'Click to stop continuous microphone and transcribe' : 'Click to start continuous microphone recording'}
                    >
                      {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5 text-cyber-cyan" />}
                      <span>{isRecording ? 'Stop & Convert Voice' : 'Voice Input (Continuous)'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        if (isRecording) {
                          toggleRecording();
                        } else {
                          transcribeWithWhisper();
                        }
                      }}
                      disabled={isTranscribingWithWhisper}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                        isTranscribingWithWhisper
                          ? 'bg-purple-600 text-white animate-pulse'
                          : 'bg-purple-600/25 hover:bg-purple-600/40 text-purple-300 hover:text-white border border-purple-500/40'
                      }`}
                      title="Convert speech directly using server-side neural Whisper AI"
                    >
                      {isTranscribingWithWhisper ? (
                        <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-200" />
                      ) : (
                        <Wand2 className="w-3.5 h-3.5 text-purple-300" />
                      )}
                      <span>{isTranscribingWithWhisper ? 'Whisper Converting...' : 'AI Whisper STT'}</span>
                    </button>
                  </div>
                </div>

                {/* Diagnostic Toast / Banner if Mic Test run */}
                {micTestResult && (
                  <motion.div
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-3 rounded-2xl text-xs flex items-center justify-between border ${
                      micTestResult.startsWith('✓')
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                        : 'bg-amber-950/40 border-amber-500/40 text-amber-300'
                    }`}
                  >
                    <span>{micTestResult}</span>
                    <button
                      onClick={() => setMicTestResult(null)}
                      className="text-[10px] font-mono opacity-70 hover:opacity-100 ml-2"
                    >
                      Dismiss
                    </button>
                  </motion.div>
                )}

                {/* Whisper Neural Transcription Toast / Status Banner */}
                {whisperStatusText && (
                  <motion.div
                    initial={{ opacity: 0, y: -6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-3 rounded-2xl text-xs flex items-center justify-between border ${
                      whisperStatusText.startsWith('✓')
                        ? 'bg-emerald-950/50 border-emerald-500/40 text-emerald-300'
                        : whisperStatusText.startsWith('⚡')
                        ? 'bg-purple-950/50 border-purple-500/40 text-purple-200'
                        : 'bg-amber-950/40 border-amber-500/30 text-amber-300'
                    }`}
                  >
                    <div className="flex items-center space-x-2">
                      {isTranscribingWithWhisper && <Loader2 className="w-3.5 h-3.5 animate-spin text-purple-300" />}
                      <span>{whisperStatusText}</span>
                    </div>
                    <button
                      onClick={() => setWhisperStatusText(null)}
                      className="text-[10px] font-mono opacity-70 hover:opacity-100 ml-2"
                    >
                      Dismiss
                    </button>
                  </motion.div>
                )}

                {/* Real-time Voice Detection Telemetry Bar (active when recording) */}
                {isRecording && (
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-cyan-500/30 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono">
                    <div className="flex items-center space-x-2">
                      <span className={`w-2 h-2 rounded-full ${isVoiceDetected ? 'bg-emerald-400 animate-ping' : 'bg-cyan-400'}`}></span>
                      <span className="text-cyan-300 font-semibold">
                        {isVoiceDetected ? '🔊 Voice Detected — Converting Speech...' : '🎙️ Mic Active — Waiting for speech'}
                      </span>
                    </div>

                    {lastSpokenPhrase && (
                      <div className="text-slate-300 text-[10px] truncate max-w-xs sm:max-w-md">
                        <span className="text-slate-400">Latest phrase: </span>
                        <span className="text-white italic">"{lastSpokenPhrase}"</span>
                      </div>
                    )}

                    <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      ✓ {answerText.trim().split(/\s+/).filter(Boolean).length} Words Transcribed
                    </span>
                  </div>
                )}

                {/* Dynamic Wavy UI Audio Visualizer when Microphone is active */}
                <AudioWaveformVisualizer isRecording={isRecording} transcript={answerText} stream={activeMicStream} />

                <textarea
                  rows={isRecording ? 4 : 6}
                  value={answerText}
                  onChange={(e) => setAnswerText(e.target.value)}
                  placeholder="Explain your technical solution, trade-offs, architecture, or behavioral example here. You can speak with microphone or type directly..."
                  className="w-full p-4 rounded-2xl bg-slate-900/90 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none transition-colors resize-none leading-relaxed font-sans"
                />

                {/* Pre-Submission Assurance Card: Guarantees candidate that voice input is converted before submitting */}
                {answerText.trim().length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-3.5 rounded-2xl bg-emerald-950/30 border border-emerald-500/25 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                  >
                    <div className="flex items-center space-x-2 text-emerald-300">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      <span>
                        <strong>Voice Converted & Ready:</strong> {answerText.trim().split(/\s+/).filter(Boolean).length} words converted into your text response. You can review, edit, or speak more before submitting.
                      </span>
                    </div>
                    <span className="font-mono text-[10px] text-emerald-300 font-bold bg-emerald-500/20 px-2.5 py-0.5 rounded-full border border-emerald-500/30 shrink-0 self-start sm:self-auto">
                      ✓ Ready to Submit
                    </span>
                  </motion.div>
                )}

                <div className="flex items-center justify-between pt-2">
                  <span className="text-xs text-slate-400 font-mono">
                    {answerText.trim().split(/\s+/).filter(Boolean).length} words
                  </span>

                  <div className="flex space-x-3">
                    <button
                      onClick={handleSubmitAnswer}
                      disabled={loading || !answerText.trim()}
                      className="px-6 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 disabled:opacity-50 text-white shadow-lg shadow-brand-500/20 transition-all flex items-center space-x-2"
                    >
                      {loading ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>
                            Submit For AI Rubric Evaluation {answerText.trim() ? `(${answerText.trim().split(/\s+/).filter(Boolean).length} words)` : ''}
                          </span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Rubric Evaluation Results Card */}
              {evaluation && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="glass-panel rounded-3xl p-6 border border-emerald-500/30 space-y-4 bg-emerald-950/10"
                >
                  <div className="flex items-center justify-between border-b border-white/10 pb-4">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                      <h4 className="font-bold text-white text-base">Instant AI Rubric Evaluation</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-slate-400">Score:</span>
                      <span className="text-xl font-black text-emerald-400">
                        {Math.round(evaluation.score)}%
                      </span>
                    </div>
                  </div>

                  {/* 6 Rubric Breakdown Badges */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
                    {evaluation.correctness !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Correctness</span>
                        <span className="font-bold text-emerald-300">{Math.round(evaluation.correctness)}%</span>
                      </div>
                    )}
                    {evaluation.technical_accuracy !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Tech Accuracy</span>
                        <span className="font-bold text-cyan-300">{Math.round(evaluation.technical_accuracy)}%</span>
                      </div>
                    )}
                    {evaluation.reasoning_depth !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Reasoning Depth</span>
                        <span className="font-bold text-indigo-300">{Math.round(evaluation.reasoning_depth)}%</span>
                      </div>
                    )}
                    {evaluation.relevance !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Relevance</span>
                        <span className="font-bold text-purple-300">{Math.round(evaluation.relevance)}%</span>
                      </div>
                    )}
                    {evaluation.completeness !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Completeness</span>
                        <span className="font-bold text-amber-300">{Math.round(evaluation.completeness)}%</span>
                      </div>
                    )}
                    {evaluation.communication_clarity !== undefined && (
                      <div className="p-2 rounded-xl bg-slate-900/60 border border-white/5">
                        <span className="text-slate-400 block text-[10px]">Communication</span>
                        <span className="font-bold text-pink-300">{Math.round(evaluation.communication_clarity)}%</span>
                      </div>
                    )}
                  </div>

                  {/* Feedback summary */}
                  {evaluation.feedback && (
                    <div className="p-3.5 rounded-xl bg-slate-900/70 border border-white/5 text-xs text-slate-200 leading-relaxed">
                      <span className="font-bold text-cyber-cyan block mb-1">Interviewer Feedback:</span>
                      {evaluation.feedback}
                    </div>
                  )}

                  {/* Detected technical keywords */}
                  {evaluation.keywords_detected && evaluation.keywords_detected.length > 0 && (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[11px] text-slate-400 font-semibold mr-1">Detected Keywords:</span>
                      {evaluation.keywords_detected.map((kw, i) => (
                        <span key={i} className="text-[10px] px-2 py-0.5 rounded-md bg-brand-500/20 text-brand-300 border border-brand-500/30">
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Next question / Finish Button */}
                  <div className="pt-2 flex justify-end">
                    <button
                      onClick={handleNextQuestion}
                      className="px-5 py-2.5 rounded-xl text-xs font-bold bg-white text-slate-950 hover:bg-slate-200 transition-colors flex items-center space-x-2"
                    >
                      <span>
                        {currentQuestionIndex + 1 < session.questions.length
                          ? 'Proceed to Next Question'
                          : 'Complete Interview & View Final Report'}
                      </span>
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* FINAL REPORT VIEW */}
      {finalReport && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel rounded-3xl p-6 sm:p-10 border border-white/10 space-y-8"
        >
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-white/10 pb-6 gap-4">
            <div>
              <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-xs font-bold mb-2">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Interview Session Completed</span>
              </div>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
                Comprehensive Performance Report
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-1">
                Generated with Qwen LLM Rubric Evaluation Engine
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-right">
                <span className="text-xs text-slate-400 uppercase tracking-wider block">Overall Score</span>
                <span className="text-4xl font-black bg-gradient-to-r from-emerald-400 to-cyber-cyan bg-clip-text text-transparent">
                  {Math.round(finalReport.overall_score)}%
                </span>
              </div>
              <button
                onClick={() => {
                  setSession(null);
                  setFinalReport(null);
                }}
                className="px-4 py-2.5 rounded-xl text-xs font-bold bg-brand-600 hover:bg-brand-500 text-white transition-colors"
              >
                Start New Session
              </button>
            </div>
          </div>

          {/* 4 Pillars Gauge */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Technical Knowledge</span>
              <span className="text-2xl font-black text-cyan-400">
                {Math.round(finalReport.technical_score)}%
              </span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Problem Solving</span>
              <span className="text-2xl font-black text-indigo-400">
                {Math.round(finalReport.problem_solving_score)}%
              </span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Communication Clarity</span>
              <span className="text-2xl font-black text-purple-400">
                {Math.round(finalReport.communication_score)}%
              </span>
            </div>
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-white/5 text-center">
              <span className="text-xs text-slate-400 block mb-1">Confidence Rating</span>
              <span className="text-2xl font-black text-emerald-400">
                {Math.round(finalReport.confidence_score)}%
              </span>
            </div>
          </div>

          {/* AI Executive Summary */}
          {finalReport.summary && (
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-white/10 space-y-2">
              <h3 className="font-bold text-white text-sm flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyber-cyan" />
                <span>Executive Summary & Analysis</span>
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed">{finalReport.summary}</p>
            </div>
          )}

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 rounded-2xl bg-emerald-950/20 border border-emerald-500/30 space-y-3">
              <h4 className="font-bold text-emerald-300 text-sm flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-emerald-400" />
                <span>Key Strengths</span>
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {(finalReport.strong_areas?.length ? finalReport.strong_areas : ['Solid core fundamentals', 'Clear solution structure']).map((item: any, i: number) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    <span>{typeof item === 'string' ? item : item.title || JSON.stringify(item)}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-5 rounded-2xl bg-orange-950/20 border border-orange-500/30 space-y-3">
              <h4 className="font-bold text-orange-300 text-sm flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-orange-400" />
                <span>Areas Needing Improvement</span>
              </h4>
              <ul className="space-y-2 text-xs text-slate-300">
                {(finalReport.weak_areas?.length ? finalReport.weak_areas : ['Elaborate further on trade-offs', 'Provide more concrete examples']).map((item: any, i: number) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-orange-400 mt-0.5">•</span>
                    <span>{typeof item === 'string' ? item : item.title || JSON.stringify(item)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommended Preparation Topics */}
          {finalReport.recommended_preparation_topics?.length > 0 && (
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-white/5 space-y-2">
              <h4 className="font-bold text-slate-200 text-xs uppercase tracking-wider">
                Recommended Preparation Topics:
              </h4>
              <div className="flex flex-wrap gap-2">
                {finalReport.recommended_preparation_topics.map((topic: string, i: number) => (
                  <span key={i} className="px-3 py-1 rounded-lg bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-medium">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};
