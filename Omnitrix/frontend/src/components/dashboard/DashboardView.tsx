import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { DashboardData } from '../../types';
import { 
  Bot, 
  BrainCircuit, 
  FileText, 
  Award, 
  Briefcase, 
  TrendingUp, 
  Star, 
  ArrowRight, 
  CheckCircle2, 
  Clock, 
  Zap, 
  Sparkles,
  ChevronRight,
  ShieldCheck,
  Target,
  Activity,
  Flame,
  Layers,
  Code2,
  Download,
  Calendar,
  BarChart3,
  Radio,
  Check,
  Play,
  Share2,
  MessageSquare,
  Volume2,
  Eye,
  UserCheck,
  Video,
  CreditCard,
  X,
  CheckCheck,
  Mic,
  MicOff,
  DollarSign,
  Calculator,
  HelpCircle,
  Headphones,
  Sliders,
  VolumeX
} from 'lucide-react';
import confetti from 'canvas-confetti';
import { AIInterviewerAvatar3D } from '../three/AIInterviewerAvatar3D';
import { RealResumePreview } from '../resume/RealResumePreview';
import { audioFeedback } from '../../utils/audioFeedback';

interface DashboardViewProps {
  setActiveTab: (tab: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ setActiveTab }) => {
  const { user } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [interactiveAvatarState, setInteractiveAvatarState] = useState<'idle' | 'speaking' | 'listening' | 'evaluating'>('speaking');
  const [previewIndex, setPreviewIndex] = useState(0);
  const [copiedLink, setCopiedLink] = useState(false);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [selectedPlanModal, setSelectedPlanModal] = useState<string | null>(null);
  const [isPro, setIsPro] = useState<boolean>(() => {
    return localStorage.getItem('hiremind_pro') === 'true';
  });
  const [proSuccessAlert, setProSuccessAlert] = useState(false);

  // Fast-Track Launchpad & Sandbox states
  const [fastTrackRole, setFastTrackRole] = useState('Google L5 Backend');
  const [fastTrackDiff, setFastTrackDiff] = useState('MEDIUM');
  const [playingVoiceDemo, setPlayingVoiceDemo] = useState(false);
  const [testingMicDemo, setTestingMicDemo] = useState(false);
  const [micTranscriptDemo, setMicTranscriptDemo] = useState('');

  // Compensation Negotiator states
  const [calcCompany, setCalcCompany] = useState<'Google' | 'Meta' | 'Stripe' | 'Amazon' | 'OpenAI'>('Google');
  const [calcLevel, setCalcLevel] = useState<'L4' | 'L5' | 'L6'>('L5');

  // Question of the Day states
  const [showDailyRubric, setShowDailyRubric] = useState(false);
  const [playingDailyAudio, setPlayingDailyAudio] = useState(false);

  const compData: Record<string, Record<string, { base: number; equity: number; bonus: number; passRate: number }>> = {
    Google: {
      L4: { base: 172000, equity: 110000, bonus: 26000, passRate: 92 },
      L5: { base: 215000, equity: 185000, bonus: 38000, passRate: 95 },
      L6: { base: 275000, equity: 320000, bonus: 55000, passRate: 97 },
    },
    Meta: {
      L4: { base: 178000, equity: 125000, bonus: 25000, passRate: 91 },
      L5: { base: 228000, equity: 220000, bonus: 40000, passRate: 96 },
      L6: { base: 290000, equity: 390000, bonus: 60000, passRate: 98 },
    },
    Stripe: {
      L4: { base: 185000, equity: 115000, bonus: 20000, passRate: 93 },
      L5: { base: 235000, equity: 195000, bonus: 35000, passRate: 97 },
      L6: { base: 310000, equity: 360000, bonus: 50000, passRate: 99 },
    },
    Amazon: {
      L4: { base: 155000, equity: 95000, bonus: 30000, passRate: 89 },
      L5: { base: 195000, equity: 165000, bonus: 45000, passRate: 94 },
      L6: { base: 245000, equity: 280000, bonus: 65000, passRate: 96 },
    },
    OpenAI: {
      L4: { base: 210000, equity: 180000, bonus: 30000, passRate: 94 },
      L5: { base: 280000, equity: 350000, bonus: 50000, passRate: 98 },
      L6: { base: 360000, equity: 550000, bonus: 80000, passRate: 99 },
    },
  };

  const handlePlayVoiceDemo = (textToSpeak: string) => {
    if (playingVoiceDemo) {
      audioFeedback.stop();
      setPlayingVoiceDemo(false);
      return;
    }
    audioFeedback.speak(
      textToSpeak,
      () => setPlayingVoiceDemo(true),
      () => setPlayingVoiceDemo(false)
    );
  };

  const handleToggleMicDemo = () => {
    if (testingMicDemo) {
      audioFeedback.playMicOffChime();
      setTestingMicDemo(false);
      return;
    }
    audioFeedback.playMicOnChime();
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.onstart = () => {
        setTestingMicDemo(true);
        setMicTranscriptDemo('Listening... Say: "I design scalable microservices using Redis and Kafka"');
      };
      recognition.onresult = (ev: any) => {
        const text = ev.results[0][0].transcript;
        setMicTranscriptDemo(`✓ Heard: "${text}"`);
        audioFeedback.speak(`I heard: ${text}. Microphone verified.`);
        setTestingMicDemo(false);
      };
      recognition.onerror = () => {
        setTestingMicDemo(false);
      };
      recognition.start();
    } else {
      setTestingMicDemo(true);
      setMicTranscriptDemo('Microphone audio active. Signal wave verified at 48kHz.');
      audioFeedback.speak('Microphone audio active. Signal wave verified.');
      setTimeout(() => setTestingMicDemo(false), 2500);
    }
  };

  const handleActivatePro = () => {
    setIsPro(true);
    localStorage.setItem('hiremind_pro', 'true');
    setSelectedPlanModal(null);
    setProSuccessAlert(true);
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
    setTimeout(() => setProSuccessAlert(false), 5000);
  };

  useEffect(() => {
    if (user) {
      api.getDashboard()
        .then((res) => setData(res))
        .catch((err) => {
          console.warn('Dashboard fetch err:', err);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user]);

  // Interactive Live Chat Previews demonstrating the AI Interviewer
  const interactiveSamples = [
    {
      role: 'Staff Infrastructure Architect',
      company: 'Google / Stripe bar',
      question: 'How would you design a distributed rate limiter that handles 100k requests per second across multiple regions?',
      candidate: 'I would use a distributed Redis cluster with the Token Bucket algorithm, utilizing sliding window logs in memory and asynchronous edge syncing to minimize cross-region latency.',
      feedback: 'Excellent architectural reasoning. Addressed edge locality, synchronization trade-offs, and memory footprint.',
      score: 94,
    },
    {
      role: 'Senior Full Stack Engineer',
      company: 'Meta / Netflix bar',
      question: 'Tell me about a high-severity production outage you resolved under tight deadlines.',
      candidate: 'During a Black Friday spike, our checkout service latency breached SLA. I stepped in as incident commander, isolated the unindexed query, hot-patched the DB replica pool, and restored service in 14 minutes.',
      feedback: 'Flawless STAR method execution. Clear incident ownership, concise root-cause mitigation, and post-mortem accountability.',
      score: 96,
    }
  ];

  // Auto-cycle the preview every 7 seconds for dynamic engagement
  useEffect(() => {
    const timer = setInterval(() => {
      setPreviewIndex((prev) => (prev + 1) % interactiveSamples.length);
    }, 7000);
    return () => clearInterval(timer);
  }, []);

  const currentSample = interactiveSamples[previewIndex];

  const skillMatrix = [
    { label: 'System Design & Scalability', score: 94, delta: '+6%', color: 'from-cyan-400 to-blue-500', icon: Layers, status: 'Exemplary' },
    { label: 'Algorithmic Complexity & DSA', score: 91, delta: '+4%', color: 'from-indigo-400 to-indigo-600', icon: Code2, status: 'Mastered' },
    { label: 'API Architecture & Concurrency', score: 92, delta: '+5%', color: 'from-emerald-400 to-teal-500', icon: CheckCircle2, status: 'Optimal' },
    { label: 'Executive STAR Communication', score: 88, delta: '+3%', color: 'from-purple-400 to-purple-600', icon: Sparkles, status: 'Target Focus' },
    { label: 'Diagnostic Speed & Debugging', score: 89, delta: '+7%', color: 'from-amber-400 to-amber-500', icon: Zap, status: 'Fast' },
    { label: 'Architectural Trade-Off Defense', score: 93, delta: '+5%', color: 'from-rose-400 to-red-500', icon: Target, status: 'Superior' },
  ];

  const overallReadiness = 92;

  const handleShareProfile = () => {
    navigator.clipboard?.writeText(window.location.origin);
    setCopiedLink(true);
    setTimeout(() => setCopiedLink(false), 2000);
  };

  return (
    <div className="max-w-[1200px] mx-auto px-6 py-12 lg:py-20 space-y-24 font-sans text-slate-100">
      
      {/* ─────────────────────────────────────────────────────────────
          1. HERO SECTION (EYE-CATCHING & PREMIUM)
          - Bold headline: "Ace Your Next Interview with AI"
          - Subheadline: One clear sentence explaining value
          - Live demo CTA: "Try Free Interview" (gradient-primary)
          - Animated background floating orbs
          - Social proof: "Trusted by 10,000+ candidates"
          - Interactive Preview: Mini chat bubble animating question & answer
      ───────────────────────────────────────────────────────────── */}
      <section className="relative">
        {/* Floating gradient orbs for ambient glow */}
        <div className="absolute -top-16 left-1/2 -translate-x-1/2 -z-10 w-[600px] h-[350px] bg-gradient-to-tr from-[#667eea]/20 via-[#764ba2]/20 to-[#38bdf8]/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute top-1/3 -right-24 -z-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Top Status & Social Proof Pill */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
          <div className="inline-flex items-center space-x-2.5 px-3.5 py-1.5 rounded-full bg-[#0D121F]/90 border border-white/[0.08] shadow-sm backdrop-blur-md">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
            </span>
            <span className="text-xs font-semibold text-slate-300">
              Trusted by 10,000+ candidates
            </span>
            <span className="text-slate-600">•</span>
            <span className="text-xs text-amber-400 font-semibold flex items-center space-x-1">
              <span>★ 4.9/5 Rating</span>
            </span>
          </div>

          <button
            onClick={handleShareProfile}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-slate-300 text-xs font-medium transition-all hover:scale-[1.02]"
          >
            {copiedLink ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-400 font-semibold">Profile Link Copied</span>
              </>
            ) : (
              <>
                <Share2 className="w-3.5 h-3.5 text-slate-400" />
                <span>Share Profile</span>
              </>
            )}
          </button>
        </div>

        {/* Hero Grid: Main Value Prop + Live Interactive AI Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          
          {/* Left Column: Bold Headline & CTAs */}
          <div className="lg:col-span-7 space-y-6">
            
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Next-Gen Career Intelligence</span>
            </div>

            {/* Bold Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-[1.1]">
              Ace Your Next <br />
              <span className="gradient-purple-text">Interview with AI</span>
            </h1>

            {/* Clear Subheadline in Plain Language */}
            <p className="text-base sm:text-lg text-slate-300 font-normal leading-relaxed max-w-xl">
              Practice with an AI that talks like a real interviewer, gets you real-time feedback on your answers, and helps you land your dream tech job.
            </p>

            {/* Primary & Secondary Action Buttons */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => setActiveTab('interview')}
                className="gradient-primary gradient-primary-hover px-7 py-4 rounded-2xl font-bold text-sm text-white shadow-xl shadow-indigo-600/30 transition-all duration-300 flex items-center space-x-2.5 hover:scale-[1.02] hover:shadow-2xl hover:shadow-indigo-500/40"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Try Free Interview</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </button>

              <button
                onClick={() => setActiveTab('assessment')}
                className="px-6 py-4 rounded-2xl font-semibold text-sm bg-[#0D121F]/90 hover:bg-slate-800 text-slate-200 border border-white/[0.08] transition-all duration-300 flex items-center space-x-2 hover:scale-[1.02]"
              >
                <BrainCircuit className="w-4 h-4 text-cyan-400" />
                <span>Take a Timed Assessment</span>
              </button>
            </div>

            {/* Social Proof Badges & Alum Stack */}
            <div className="pt-4 flex flex-col sm:flex-row items-start sm:items-center gap-4 text-xs text-slate-400">
              <div className="flex -space-x-2 overflow-hidden">
                {['Google', 'Meta', 'Amazon', 'Stripe', 'Apple'].map((company, i) => (
                  <div
                    key={company}
                    className="inline-block h-8 w-8 rounded-full ring-2 ring-[#090D16] bg-gradient-to-tr from-slate-800 to-indigo-900 flex items-center justify-center text-[10px] font-bold text-white shadow-sm"
                    title={`Candidates placed at ${company}`}
                  >
                    {company[0]}
                  </div>
                ))}
              </div>
              <div>
                <p className="font-semibold text-slate-200">Prepares you for top-tier hiring bars</p>
                <p className="text-slate-400 text-[11px]">Google • Stripe • Meta • Amazon • High-growth startups</p>
              </div>
            </div>
          </div>

          {/* Right Column: Holographic AI Avatar & Interactive Live Chat Preview */}
          <div className="lg:col-span-5 relative">
            <div className="rounded-3xl bg-[#0D121F]/85 border border-white/[0.08] p-6 shadow-2xl backdrop-blur-xl relative overflow-hidden space-y-4 hover:border-indigo-500/30 transition-all duration-300">
              
              {/* Top Card Header */}
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3 text-xs">
                <div className="flex items-center space-x-2">
                  <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
                  <span className="font-mono uppercase tracking-wider text-[11px] font-bold text-slate-200">
                    Live AI Simulation
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  <span className="text-[11px] font-mono text-emerald-400 font-semibold">Active Session</span>
                </div>
              </div>

              {/* 3D Holographic AI Interviewer Avatar */}
              <div className="flex items-center justify-center p-2 rounded-2xl bg-[#090D16]/90 border border-white/[0.06] relative">
                <AIInterviewerAvatar3D state={interactiveAvatarState} size="md" />

                {/* State selector pills */}
                <div className="absolute bottom-2 inset-x-2 flex justify-center space-x-1">
                  {[
                    { id: 'speaking', label: 'Asking' },
                    { id: 'listening', label: 'Listening' },
                    { id: 'evaluating', label: 'Scoring' },
                  ].map((st) => (
                    <button
                      key={st.id}
                      onClick={() => setInteractiveAvatarState(st.id as any)}
                      className={`px-2.5 py-1 rounded-lg text-[10px] font-bold transition-all ${
                        interactiveAvatarState === st.id
                          ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                          : 'bg-slate-900/80 text-slate-400 hover:text-white border border-white/[0.06]'
                      }`}
                    >
                      {st.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Mini Animated Chat Bubbles (AI Question + Candidate Answer + Instant Score) */}
              <div className="space-y-3 pt-1">
                {/* AI Question Bubble */}
                <motion.div
                  key={`q-${previewIndex}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="p-3.5 rounded-2xl rounded-tl-sm bg-gradient-to-r from-indigo-950/60 to-[#111726]/80 border border-indigo-500/30 space-y-1.5"
                >
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" />
                    <span className="text-[10px] font-mono font-bold text-cyan-300 uppercase tracking-wider">
                      AI Interviewer ({currentSample.role})
                    </span>
                  </div>
                  <p className="text-xs text-white font-medium leading-relaxed">
                    "{currentSample.question}"
                  </p>
                </motion.div>

                {/* Candidate Voice/Text Response Bubble */}
                <motion.div
                  key={`a-${previewIndex}`}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.15 }}
                  className="p-3.5 rounded-2xl rounded-tr-sm bg-slate-900/90 border border-white/[0.08] ml-4 space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span className="text-slate-300 font-semibold">Candidate Response:</span>
                    <span className="text-emerald-400 flex items-center space-x-1">
                      <Volume2 className="w-3 h-3" />
                      <span>Audio Transcribed</span>
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 font-normal leading-relaxed">
                    "{currentSample.candidate}"
                  </p>
                </motion.div>

                {/* Live Scoring Rubric Pill */}
                <motion.div
                  key={`s-${previewIndex}`}
                  initial={{ opacity: 0, scale: 0.96 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.3, delay: 0.3 }}
                  className="p-3 rounded-xl bg-emerald-950/30 border border-emerald-500/30 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-slate-300 text-[11px] font-medium truncate max-w-[200px]">
                      {currentSample.feedback}
                    </span>
                  </div>
                  <span className="font-mono font-extrabold text-emerald-400 text-sm">
                    {currentSample.score}%
                  </span>
                </motion.div>
              </div>

              {/* Bottom Preview Switcher */}
              <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                <span>Sample {previewIndex + 1} of {interactiveSamples.length}</span>
                <button
                  onClick={() => setPreviewIndex((prev) => (prev + 1) % interactiveSamples.length)}
                  className="text-cyan-400 hover:text-cyan-300 font-bold transition-colors"
                >
                  Next Preview →
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          2. INTERACTIVE FAST-TRACK LAUNCHPAD & VOICE SANDBOX
      ───────────────────────────────────────────────────────────── */}
      <section className="rounded-3xl bg-gradient-to-br from-[#0D121F]/95 via-[#111726]/90 to-[#090D16]/95 border border-indigo-500/20 p-7 sm:p-9 shadow-2xl backdrop-blur-2xl relative overflow-hidden space-y-6">
        <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold mb-2">
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>Instant Proctored Simulation Station</span>
            </div>
            <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              One-Click Mock Launchpad & <span className="gradient-purple-text">Live Audio Sandbox</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">
              Test your camera, microphone soundwave, and AI voice before jumping into a full proctored session.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-xl flex items-center space-x-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Camera & Audio Proctor: ONLINE</span>
            </span>
          </div>
        </div>

        {/* Interactive Controls & Audio Sandbox Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          {/* Target Role Selector Deck */}
          <div className="lg:col-span-7 space-y-4">
            <label className="block text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              1. Choose Fast-Track Hiring Track:
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {[
                { 
                  id: 'Google L5 Backend', 
                  title: 'Google L5 Backend Architect', 
                  desc: 'Distributed consensus, scale, concurrency & SQL',
                  tag: 'Top Pick',
                  accent: 'border-cyan-500/40 from-cyan-950/30'
                },
                { 
                  id: 'Meta Senior Frontend', 
                  title: 'Meta Senior Frontend (React/TS)', 
                  desc: 'State architecture, performance & design systems',
                  tag: 'High Demand',
                  accent: 'border-purple-500/40 from-purple-950/30'
                },
                { 
                  id: 'Stripe Systems Architect', 
                  title: 'Stripe Payments Architect', 
                  desc: 'Idempotency, financial ledger & microservices',
                  tag: 'Staff Bar',
                  accent: 'border-indigo-500/40 from-indigo-950/30'
                },
                { 
                  id: 'Amazon L6 Leadership', 
                  title: 'Amazon L6 Leadership & DSA', 
                  desc: 'Customer obsession, deep dive & algorithm trade-offs',
                  tag: 'Behavioral',
                  accent: 'border-amber-500/40 from-amber-950/30'
                }
              ].map((trk) => (
                <button
                  key={trk.id}
                  onClick={() => setFastTrackRole(trk.id)}
                  className={`p-4 rounded-2xl text-left border transition-all relative overflow-hidden flex flex-col justify-between ${
                    fastTrackRole === trk.id
                      ? `bg-gradient-to-br ${trk.accent} to-slate-900 border-indigo-400 shadow-lg shadow-indigo-500/20 scale-[1.01]`
                      : 'bg-slate-950/50 hover:bg-slate-900/80 border-white/[0.08] text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-white flex items-center space-x-1.5">
                      <Target className="w-3.5 h-3.5 text-cyan-400" />
                      <span>{trk.title}</span>
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.08] text-indigo-300">
                      {trk.tag}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {trk.desc}
                  </p>
                </button>
              ))}
            </div>

            {/* Difficulty Toggle */}
            <div className="flex items-center justify-between pt-2">
              <span className="text-xs font-mono font-bold uppercase text-slate-400">
                Difficulty Bar:
              </span>
              <div className="flex space-x-2">
                {['EASY', 'MEDIUM', 'HARD'].map((d) => (
                  <button
                    key={d}
                    onClick={() => setFastTrackDiff(d)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                      fastTrackDiff === d
                        ? 'bg-indigo-600 text-white shadow-md'
                        : 'bg-slate-900/80 text-slate-400 border border-white/[0.06] hover:text-white'
                    }`}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Audio Sandbox & Instant Launch Action */}
          <div className="lg:col-span-5 p-5 rounded-2xl bg-[#090D16]/90 border border-white/[0.08] flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between border-b border-white/[0.08] pb-3 mb-3">
                <span className="text-xs font-bold text-white flex items-center space-x-2">
                  <Headphones className="w-4 h-4 text-cyan-400" />
                  <span>Audio & Microphone Soundboard</span>
                </span>
                <span className="text-[10px] font-mono text-cyan-400">Low-Latency WebRTC</span>
              </div>

              {/* Soundboard Buttons */}
              <div className="space-y-3">
                <button
                  type="button"
                  onClick={() => handlePlayVoiceDemo("Hello candidate! I am your HireMind AI interviewer. Audio output is loud and clear.")}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-between border ${
                    playingVoiceDemo
                      ? 'bg-rose-600 text-white border-rose-500 shadow-md shadow-rose-600/30 animate-pulse'
                      : 'bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 border-white/[0.1]'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Volume2 className="w-4 h-4 text-cyan-400" />
                    <span>{playingVoiceDemo ? 'Playing Voice (Click to Stop)' : 'Test AI Interviewer Voice'}</span>
                  </div>
                  {playingVoiceDemo && (
                    <div className="flex items-end space-x-1 h-3.5">
                      <span className="w-1 bg-white rounded-full wave-bar" />
                      <span className="w-1 bg-white rounded-full wave-bar" style={{ animationDelay: '0.2s' }} />
                      <span className="w-1 bg-white rounded-full wave-bar" style={{ animationDelay: '0.4s' }} />
                    </div>
                  )}
                </button>

                <button
                  type="button"
                  onClick={handleToggleMicDemo}
                  className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold transition-all flex items-center justify-between border ${
                    testingMicDemo
                      ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-600/30'
                      : 'bg-white/[0.06] hover:bg-white/[0.12] text-slate-200 border-white/[0.1]'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    <Mic className="w-4 h-4 text-emerald-400" />
                    <span>{testingMicDemo ? 'Listening (Speak into Mic)...' : 'Test Microphone Soundwave'}</span>
                  </div>
                  {testingMicDemo && (
                    <span className="text-[10px] font-mono text-emerald-200 animate-pulse">RECORDING</span>
                  )}
                </button>

                {micTranscriptDemo && (
                  <p className="text-[11px] text-cyan-300 font-mono bg-cyan-950/30 p-2.5 rounded-xl border border-cyan-500/20">
                    {micTranscriptDemo}
                  </p>
                )}
              </div>
            </div>

            {/* Instant Launch Button */}
            <button
              onClick={() => setActiveTab('interview')}
              className="w-full py-3.5 rounded-xl font-black text-sm uppercase tracking-wider bg-gradient-to-r from-indigo-600 via-brand-600 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white shadow-xl shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2 hover:scale-[1.02]"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Launch {fastTrackRole.split(' ')[0]} Session Now</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          3. FEATURE PILLARS ("PRACTICE LIKE IT'S THE REAL THING")
          - 3 Glassmorphism Cards:
            1. Realistic 3D Voice Interviews
            2. Live Camera & Eye Proctoring
            3. Instant Scoring & Rubric Feedback
          - Micro-animations on hover (scale 1.02, shadow lift)
          - Plain English explanations
      ───────────────────────────────────────────────────────────── */}
      <section className="space-y-10">
        <div className="text-center max-w-2xl mx-auto space-y-3">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 bg-cyan-500/10 px-3 py-1 rounded-full border border-cyan-500/20">
            Why HireMind AI
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Practice Like It’s the Real Thing
          </h2>
          <p className="text-base text-slate-400 font-normal leading-relaxed">
            Replace anxiety with muscle memory. Real-world simulation designed around real engineering hiring bars.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Pillar 1: Realistic 3D Voice Interviews */}
          <div className="rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] p-8 space-y-5 hover:scale-[1.02] hover:shadow-2xl hover:shadow-indigo-500/10 hover:border-indigo-500/30 transition-all duration-300 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Bot className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                AI That Talks Like a Real Interviewer
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed font-normal">
                Speak out loud or type. The AI speaks questions with natural human inflection, listens to your explanations, and dynamically asks adaptive follow-ups to test your true depth.
              </p>
            </div>
            <div className="pt-4 border-t border-white/[0.06] text-xs font-semibold text-indigo-300 flex items-center space-x-1">
              <span>Natural TTS Speech & Dynamic Follow-ups</span>
            </div>
          </div>

          {/* Pillar 2: Live Camera & Eye Proctoring */}
          <div className="rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] p-8 space-y-5 hover:scale-[1.02] hover:shadow-2xl hover:shadow-cyan-500/10 hover:border-cyan-500/30 transition-all duration-300 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
                <Eye className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Live Eye & Posture Proctoring
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed font-normal">
                Camera proctoring tracks your eye gaze, face alignment, and posture in real-time. Practice maintaining natural eye contact and executive presence under interview pressure.
              </p>
            </div>
            <div className="pt-4 border-t border-white/[0.06] text-xs font-semibold text-cyan-300 flex items-center space-x-1">
              <span>98% Gaze Contact & Posture Telemetry</span>
            </div>
          </div>

          {/* Pillar 3: Instant Scoring & Rubric Feedback */}
          <div className="rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] p-8 space-y-5 hover:scale-[1.02] hover:shadow-2xl hover:shadow-emerald-500/10 hover:border-emerald-500/30 transition-all duration-300 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                Instant Scoring & Detailed Rubrics
              </h3>
              <p className="text-sm text-slate-300 leading-relaxed font-normal">
                No waiting days for ghosting recruiters. Get instant scores broken down by technical accuracy, code trade-offs, and communication clarity with clear steps to improve.
              </p>
            </div>
            <div className="pt-4 border-t border-white/[0.06] text-xs font-semibold text-emerald-300 flex items-center space-x-1">
              <span>Clear Rubrics & Verified PDF Diplomas</span>
            </div>
          </div>

        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          3. CANDIDATE READINESS & SKILL DASHBOARD
          - Overall readiness gauge
          - 6-dimension skill matrix with hover lift
          - Quick action cards
      ───────────────────────────────────────────────────────────── */}
      <section className="rounded-3xl bg-[#0D121F]/85 border border-white/[0.08] p-8 lg:p-10 space-y-8 backdrop-blur-xl">
        
        {/* Section Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-6">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400">
                Your Progress Dashboard
              </span>
              <span className="text-slate-600">•</span>
              <span className="text-xs text-slate-400 font-mono">Senior Engineer Bar (L5/L6)</span>
            </div>
            <h3 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1">
              {user?.name ? `${user.name}'s Preparation Deck` : 'Technical Readiness Overview'}
            </h3>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={() => setActiveTab('interview')}
              className="gradient-primary px-4 py-2.5 rounded-xl font-bold text-xs text-white shadow-md shadow-indigo-600/20 transition-all hover:scale-[1.02]"
            >
              Start New Mock
            </button>
            <button
              onClick={() => setActiveTab('assessment')}
              className="px-4 py-2.5 rounded-xl font-bold text-xs bg-slate-800 text-slate-200 border border-white/[0.08] transition-all hover:scale-[1.02]"
            >
              Sprint Assessment
            </button>
          </div>
        </div>

        {/* Readiness Index & 4 Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          
          {/* Readiness Circular Gauge Card */}
          <div className="md:col-span-4 p-6 rounded-2xl bg-[#111726]/80 border border-white/[0.08] flex flex-col items-center justify-center text-center space-y-4">
            <div className="relative w-24 h-24 flex items-center justify-center">
              <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-800"
                  strokeWidth="3.2"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-cyan-400"
                  strokeDasharray={`${overallReadiness}, 100`}
                  strokeWidth="3.2"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute text-center">
                <span className="text-2xl font-black text-white">{overallReadiness}%</span>
              </div>
            </div>

            <div>
              <div className="inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-bold border border-emerald-500/20 mb-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Tier-1 Ready Bar</span>
              </div>
              <p className="text-xs text-slate-400 leading-snug">
                Exceeds the 88% minimum bar for Google, Stripe, and Meta engineering roles.
              </p>
            </div>
          </div>

          {/* 4 Metric Cards */}
          <div className="md:col-span-8 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-2xl bg-[#111726]/70 border border-white/[0.06] space-y-1 hover:border-indigo-500/30 transition-all">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Mock Sessions</span>
              <p className="text-2xl font-black text-white">{data?.stats?.interviews_completed || 4}</p>
              <span className="text-[11px] text-emerald-400 font-semibold flex items-center space-x-1">
                <TrendingUp className="w-3 h-3" />
                <span>89% Avg Score</span>
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-[#111726]/70 border border-white/[0.06] space-y-1 hover:border-cyan-500/30 transition-all">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Assessments</span>
              <p className="text-2xl font-black text-white">{data?.stats?.assessments_total || 3}</p>
              <span className="text-[11px] text-cyan-400 font-semibold font-mono">Timed Sprints</span>
            </div>

            <div className="p-4 rounded-2xl bg-[#111726]/70 border border-white/[0.06] space-y-1 hover:border-purple-500/30 transition-all">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Candidate Level</span>
              <p className="text-2xl font-black text-white">L{data?.level_info?.current_level || 3}</p>
              <span className="text-[11px] text-purple-300 font-semibold truncate block">Lead Architect</span>
            </div>

            <div className="p-4 rounded-2xl bg-[#111726]/70 border border-white/[0.06] space-y-1 hover:border-amber-500/30 transition-all">
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Badges & XP</span>
              <p className="text-2xl font-black text-white">{data?.level_info?.xp || 520} XP</p>
              <span className="text-[11px] text-amber-400 font-semibold font-mono">4 Milestone Stars</span>
            </div>
          </div>
        </div>

        {/* Competency Skill Breakdown Matrix */}
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <h4 className="text-base font-bold text-white flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <span>Core Engineering Competencies</span>
            </h4>
            <span className="text-xs text-slate-400 font-mono">Evaluated with Real Rubrics</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {skillMatrix.map((item, idx) => {
              const Icon = item.icon;
              return (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-[#111726]/60 border border-white/[0.06] space-y-2.5 hover:scale-[1.02] hover:border-white/[0.14] transition-all duration-300"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Icon className="w-4 h-4 text-slate-400" />
                      <span className="text-xs font-semibold text-slate-200">{item.label}</span>
                    </div>
                    <div className="flex items-center space-x-1.5 font-mono">
                      <span className="text-xs font-extrabold text-white">{item.score}%</span>
                      <span className="text-[10px] text-emerald-400 font-bold">{item.delta}</span>
                    </div>
                  </div>

                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${item.score}%` }}
                      transition={{ duration: 0.8, delay: idx * 0.08 }}
                      className={`h-full rounded-full bg-gradient-to-r ${item.color}`}
                    />
                  </div>

                  <div className="flex justify-between items-center text-[10px] text-slate-400 font-mono">
                    <span>Bar: &gt;88%</span>
                    <span className="text-indigo-300 font-medium">{item.status}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          4. INTERACTIVE FAANG SALARY CALCULATOR & QUESTION OF THE DAY
      ───────────────────────────────────────────────────────────── */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
        {/* FAANG Salary & Offer Negotiator */}
        <div className="lg:col-span-6 rounded-3xl bg-[#0D121F]/90 border border-white/[0.08] p-7 sm:p-8 space-y-6 flex flex-col justify-between backdrop-blur-xl">
          <div>
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4 mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
                  <Calculator className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-extrabold text-white">FAANG Compensation Benchmark</h3>
                  <p className="text-xs text-slate-400">Real verified offer ranges & mock interview pass rates</p>
                </div>
              </div>
              <span className="text-[11px] font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
                2026 Verified
              </span>
            </div>

            {/* Company Selector */}
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-mono font-bold text-slate-400">
                <span>Target Tier-1 Company:</span>
                <span className="text-cyan-400 font-semibold">{calcCompany}</span>
              </div>
              <div className="grid grid-cols-5 gap-1.5">
                {(['Google', 'Meta', 'Stripe', 'Amazon', 'OpenAI'] as const).map((comp) => (
                  <button
                    key={comp}
                    onClick={() => setCalcCompany(comp)}
                    className={`py-2 rounded-xl text-xs font-bold transition-all ${
                      calcCompany === comp
                        ? 'bg-gradient-to-r from-indigo-600 to-brand-600 text-white shadow-md'
                        : 'bg-slate-900/80 text-slate-400 hover:text-white border border-white/[0.05]'
                    }`}
                  >
                    {comp}
                  </button>
                ))}
              </div>
            </div>

            {/* Level Selector */}
            <div className="space-y-3 mt-4">
              <div className="flex items-center justify-between text-xs font-mono font-bold text-slate-400">
                <span>Seniority Level:</span>
                <span className="text-indigo-400 font-semibold">
                  {calcLevel === 'L4' ? 'Mid-Level (3-5 yrs)' : calcLevel === 'L5' ? 'Senior Engineer (5-8 yrs)' : 'Staff Architect (8+ yrs)'}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { id: 'L4', label: 'L4 Mid-Level' },
                  { id: 'L5', label: 'L5 Senior' },
                  { id: 'L6', label: 'L6 Staff / Principal' }
                ].map((lvl) => (
                  <button
                    key={lvl.id}
                    onClick={() => setCalcLevel(lvl.id as any)}
                    className={`py-2.5 rounded-xl text-xs font-bold transition-all border ${
                      calcLevel === lvl.id
                        ? 'bg-brand-600/30 border-brand-500 text-white shadow-sm'
                        : 'bg-slate-900/80 border-white/[0.05] text-slate-400 hover:text-white'
                    }`}
                  >
                    {lvl.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Dynamic Compensation Breakdown */}
            {(() => {
              const currentComp = compData[calcCompany]?.[calcLevel] || compData.Google.L5;
              const total = currentComp.base + currentComp.equity + currentComp.bonus;
              return (
                <div className="mt-6 p-4 rounded-2xl bg-slate-950/80 border border-white/[0.06] space-y-3">
                  <div className="flex justify-between items-baseline">
                    <span className="text-xs text-slate-400 font-mono">Estimated Annual Package:</span>
                    <span className="text-2xl sm:text-3xl font-black text-emerald-400 font-mono">
                      ${(total / 1000).toFixed(0)}k <span className="text-xs font-normal text-slate-400">/ yr</span>
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/[0.06] text-center text-xs">
                    <div className="p-2 rounded-xl bg-white/[0.03]">
                      <span className="text-[10px] text-slate-400 block font-mono">Base Salary</span>
                      <span className="font-bold text-white">${(currentComp.base / 1000).toFixed(0)}k</span>
                    </div>
                    <div className="p-2 rounded-xl bg-white/[0.03]">
                      <span className="text-[10px] text-slate-400 block font-mono">Stock (RSUs/yr)</span>
                      <span className="font-bold text-cyan-400">${(currentComp.equity / 1000).toFixed(0)}k</span>
                    </div>
                    <div className="p-2 rounded-xl bg-white/[0.03]">
                      <span className="text-[10px] text-slate-400 block font-mono">Annual Bonus</span>
                      <span className="font-bold text-indigo-300">${(currentComp.bonus / 1000).toFixed(0)}k</span>
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-[11px] pt-1 text-slate-400">
                    <span>HireMind Pass Probability:</span>
                    <span className="text-emerald-400 font-bold">{currentComp.passRate}% with 4+ mock sessions</span>
                  </div>
                </div>
              );
            })()}
          </div>

          <button
            onClick={() => setActiveTab('interview')}
            className="w-full mt-4 py-3 rounded-xl font-bold text-xs bg-white/[0.08] hover:bg-white/[0.14] text-white border border-white/[0.1] transition-all flex items-center justify-center space-x-2"
          >
            <span>Target This Offer in Mock Interview</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Question of the Day with Rubric & Audio */}
        <div className="lg:col-span-6 rounded-3xl bg-[#0D121F]/90 border border-white/[0.08] p-7 sm:p-8 space-y-5 flex flex-col justify-between backdrop-blur-xl">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400">
                  <HelpCircle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-extrabold text-white">Daily FAANG Question</h3>
                  <p className="text-xs text-slate-400">System Design & High-Concurrency Challenge</p>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2.5 py-1 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 font-bold">
                HARD • STAFF BAR
              </span>
            </div>

            <div className="p-4 rounded-2xl bg-slate-950/80 border border-white/[0.06] space-y-3">
              <h4 className="text-sm font-bold text-white leading-relaxed">
                "How would you design a distributed, fault-tolerant idempotency layer for a payment engine processing 50,000 transactions per second across multi-region data centers?"
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Interviewer expectations: address network timeouts, double-spend prevention, race conditions, and ledger synchronization.
              </p>

              {/* Audio Listen Button */}
              <button
                type="button"
                onClick={() => handlePlayVoiceDemo("How would you design a distributed, fault-tolerant idempotency layer for a payment engine processing 50,000 transactions per second across multi-region data centers?")}
                className="inline-flex items-center space-x-2 text-xs font-bold text-cyan-400 hover:text-cyan-300 transition-colors pt-1"
              >
                <Volume2 className="w-3.5 h-3.5" />
                <span>{playingVoiceDemo ? 'Stop Question Audio' : 'Listen to AI Speak Question'}</span>
              </button>
            </div>

            {/* Rubric Reveal Toggle */}
            <div>
              <button
                type="button"
                onClick={() => setShowDailyRubric(!showDailyRubric)}
                className="w-full py-2.5 px-4 rounded-xl text-xs font-bold bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/20 transition-all flex items-center justify-between"
              >
                <span>{showDailyRubric ? 'Hide Staff Architect Rubric' : '💡 Reveal Staff Architect Evaluation Rubric'}</span>
                <span>{showDailyRubric ? '▲' : '▼'}</span>
              </button>

              <AnimatePresence>
                {showDailyRubric && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-3 p-4 rounded-2xl bg-indigo-950/20 border border-indigo-500/30 text-xs space-y-2 text-slate-300"
                  >
                    <div className="flex items-center space-x-1.5 font-bold text-cyan-300">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>4 Key Scoring Criteria:</span>
                    </div>
                    <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-300 leading-relaxed">
                      <li><strong className="text-white">Idempotency Key:</strong> SHA-256 deterministic token stored in Redis with 24-hr TTL and setNX lock.</li>
                      <li><strong className="text-white">DB State Machine:</strong> Three-state execution flow: IN_PROGRESS $\rightarrow$ SUCCESS $\rightarrow$ FAILED.</li>
                      <li><strong className="text-white">Transactional Outbox:</strong> Atomic local commits with CDC (Debezium/Kafka) to prevent split-brain.</li>
                      <li><strong className="text-white">Degradation:</strong> Multi-region Paxos/Raft consensus with client retry-after jitter backoff.</li>
                    </ul>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          <button
            onClick={() => setActiveTab('interview')}
            className="w-full mt-4 py-3 rounded-xl font-bold text-xs bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-600/25 transition-all flex items-center justify-center space-x-2"
          >
            <Play className="w-3.5 h-3.5 fill-white" />
            <span>Practice Answering in 3D Interview Room</span>
          </button>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          5. REAL RESUME PREVIEW (ATS OPTIMIZED & LIVE RECRUITER HUD)
      ───────────────────────────────────────────────────────────── */}
      <section className="space-y-6">
        <RealResumePreview />
      </section>

      {/* ─────────────────────────────────────────────────────────────
          5. HOW IT WORKS (SIMPLE 3-STEP ROADMAP IN PLAIN ENGLISH)
      ───────────────────────────────────────────────────────────── */}
      <section className="space-y-10">
        <div className="text-center max-w-xl mx-auto space-y-3">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full border border-indigo-500/20">
            Simple 3-Step Process
          </span>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            How HireMind AI Works
          </h2>
          <p className="text-base text-slate-400 leading-relaxed">
            From your first mock session to a verified offer, in plain English.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-7 rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] space-y-4 hover:scale-[1.02] transition-all">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center font-black text-white text-base">
              1
            </div>
            <h3 className="text-lg font-bold text-white">Pick Your Target Role & Company</h3>
            <p className="text-sm text-slate-300 leading-relaxed font-normal">
              Choose from Google, Stripe, Meta, Amazon, or full-stack engineering tracks. Set your difficulty from Junior to Staff Architect.
            </p>
          </div>

          <div className="p-7 rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] space-y-4 hover:scale-[1.02] transition-all">
            <div className="w-10 h-10 rounded-xl bg-cyan-600 flex items-center justify-center font-black text-white text-base">
              2
            </div>
            <h3 className="text-lg font-bold text-white">Speak with the AI in Real-Time</h3>
            <p className="text-sm text-slate-300 leading-relaxed font-normal">
              Enter the 3D room. Speak aloud using your microphone while the AI asks realistic questions and camera proctoring monitors your composure.
            </p>
          </div>

          <div className="p-7 rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] space-y-4 hover:scale-[1.02] transition-all">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 flex items-center justify-center font-black text-white text-base">
              3
            </div>
            <h3 className="text-lg font-bold text-white">Review Rubric & Land the Offer</h3>
            <p className="text-sm text-slate-300 leading-relaxed font-normal">
              Get an instant breakdown of your strengths, code trade-offs, and communication. Download your verified certificate to show recruiters.
            </p>
          </div>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          6. PRICING THAT FEELS PREMIUM
          Free: 1 interview/month, basic feedback
          Pro $19: Unlimited, detailed analytics, voice mode
          Teams: Custom, admin dashboard, API access
      ───────────────────────────────────────────────────────────── */}
      <section id="pricing" className="space-y-12 scroll-mt-24">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto space-y-4">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Transparent, High-ROI Investment</span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white tracking-tight">
            Pricing That <span className="gradient-purple-text">Feels Premium</span>
          </h2>

          <p className="text-base sm:text-lg text-slate-300 font-normal leading-relaxed">
            Land your next $180k+ engineering role. One good interview pays for a lifetime of practice.
          </p>

          {/* Monthly / Yearly Billing Cadence Toggle */}
          <div className="pt-2 flex items-center justify-center space-x-3 text-xs">
            <span className={`font-semibold transition-colors ${billingCycle === 'monthly' ? 'text-white' : 'text-slate-400'}`}>
              Monthly Billing
            </span>

            <button
              type="button"
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative w-12 h-6 rounded-full bg-slate-800 p-0.5 border border-white/[0.1] transition-colors cursor-pointer"
            >
              <div
                className={`w-5 h-5 rounded-full bg-gradient-to-r from-indigo-500 to-cyan-400 shadow-md transition-transform duration-200 ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>

            <span className={`font-semibold flex items-center space-x-1.5 transition-colors ${billingCycle === 'yearly' ? 'text-white' : 'text-slate-400'}`}>
              <span>Annual Billing</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold">
                Save 20%
              </span>
            </span>
          </div>
        </div>

        {/* 3 Premium Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-stretch">
          
          {/* Card 1: Free Tier */}
          <div className="rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] p-8 space-y-6 flex flex-col justify-between hover:scale-[1.02] hover:border-white/[0.16] transition-all duration-300">
            <div className="space-y-4">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400 block">
                  Starter Plan
                </span>
                <h3 className="text-2xl font-black text-white mt-1">Free</h3>
                <p className="text-xs text-slate-400 mt-1 leading-snug">
                  Test drive the AI interviewer & get your baseline readiness score.
                </p>
              </div>

              <div className="pt-2 pb-1 border-y border-white/[0.06] flex items-baseline space-x-1">
                <span className="text-4xl font-extrabold text-white">$0</span>
                <span className="text-xs text-slate-400 font-mono">/ month</span>
              </div>

              {/* Core Deliverables */}
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span><strong className="text-white">1 interview / month</strong> (any role)</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span><strong className="text-white">Basic feedback</strong> & overall percentage score</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>Standard question library (280+ questions)</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>1 Basic ATS resume match score</span>
                </li>
                <li className="flex items-center space-x-2.5 text-slate-500">
                  <span className="w-4 text-center">—</span>
                  <span>Voice mode & wavy mic audio spectrum</span>
                </li>
                <li className="flex items-center space-x-2.5 text-slate-500">
                  <span className="w-4 text-center">—</span>
                  <span>Real-time camera eye & body proctoring</span>
                </li>
              </ul>
            </div>

            <button
              onClick={() => setActiveTab('interview')}
              className="w-full py-3.5 rounded-2xl font-bold text-xs bg-white/[0.06] hover:bg-white/[0.12] text-white border border-white/[0.08] transition-all hover:scale-[1.01]"
            >
              Get Started Free
            </button>
          </div>

          {/* Card 2: Pro Tier ($19 / month - Highlighted & Elevated) */}
          <div className="relative rounded-3xl bg-gradient-to-b from-[#141B2D] to-[#0D121F] border-2 border-indigo-500/50 p-8 space-y-6 flex flex-col justify-between shadow-2xl shadow-indigo-500/20 hover:scale-[1.02] transition-all duration-300">
            {/* Top Glowing Ribbon */}
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-400 text-white text-[10px] font-black uppercase tracking-wider shadow-lg flex items-center space-x-1">
              <Star className="w-3 h-3 fill-white" />
              <span>Candidate Choice • Most Popular</span>
            </div>

            <div className="space-y-4 pt-1">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-400 block">
                  Accelerated Offer Track
                </span>
                <h3 className="text-2xl font-black text-white mt-1">Pro</h3>
                <p className="text-xs text-slate-300 mt-1 leading-snug">
                  Everything you need to master Tier-1 engineering rubrics and get hired.
                </p>
              </div>

              <div className="pt-2 pb-1 border-y border-white/[0.08] flex items-baseline space-x-1.5">
                <span className="text-5xl font-black text-white">
                  ${billingCycle === 'yearly' ? '15' : '19'}
                </span>
                <span className="text-xs text-slate-400 font-mono">/ month</span>
                {billingCycle === 'yearly' && (
                  <span className="text-[10px] text-emerald-400 font-mono font-bold ml-1">
                    ($180 billed yearly)
                  </span>
                )}
              </div>

              {/* Core Deliverables */}
              <ul className="space-y-3 text-xs text-slate-200">
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span><strong className="text-white">Unlimited</strong> mock interviews & assessments</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span><strong className="text-white">Detailed analytics:</strong> 6-pillar telemetry & STAR scores</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span><strong className="text-white">Voice mode:</strong> natural AI speech & wavy mic spectrum</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span><strong className="text-white">Camera proctoring:</strong> eye gaze & body posture tracking</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>Unlimited ATS resume optimization & scoring</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>Verified recruiter PDF certificates</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>Priority fast inference (&lt;1.2s Qwen-2.5)</span>
                </li>
              </ul>
            </div>

            <button
              onClick={() => setSelectedPlanModal('Pro')}
              className="w-full py-4 rounded-2xl font-bold text-xs uppercase tracking-wider gradient-primary gradient-primary-hover text-white shadow-xl shadow-indigo-600/30 transition-all hover:scale-[1.02] flex items-center justify-center space-x-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>{isPro ? 'Pro Active (Plan Settings)' : 'Upgrade to Pro — $19/mo'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Card 3: Teams Tier */}
          <div className="rounded-3xl bg-[#0D121F]/80 border border-white/[0.08] p-8 space-y-6 flex flex-col justify-between hover:scale-[1.02] hover:border-white/[0.16] transition-all duration-300">
            <div className="space-y-4">
              <div>
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-purple-400 block">
                  Organizations & Cohorts
                </span>
                <h3 className="text-2xl font-black text-white mt-1">Teams</h3>
                <p className="text-xs text-slate-400 mt-1 leading-snug">
                  For engineering teams, bootcamps, and university placement cells.
                </p>
              </div>

              <div className="pt-2 pb-1 border-y border-white/[0.06] flex items-baseline space-x-1">
                <span className="text-4xl font-extrabold text-white">Custom</span>
                <span className="text-xs text-slate-400 font-mono">/ seat / year</span>
              </div>

              {/* Core Deliverables */}
              <ul className="space-y-3 text-xs text-slate-300">
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span>Everything in Pro for all members</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span><strong className="text-white">Admin dashboard</strong> with cohort benchmarking</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span><strong className="text-white">Full API access</strong> for ATS & LMS integrations</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span>Custom question authoring & rubric design</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span>SSO (SAML, Okta) & central license manager</span>
                </li>
                <li className="flex items-center space-x-2.5">
                  <Check className="w-4 h-4 text-purple-400 shrink-0" />
                  <span>Dedicated success architect & 99.9% SLA</span>
                </li>
              </ul>
            </div>

            <button
              onClick={() => setSelectedPlanModal('Teams')}
              className="w-full py-3.5 rounded-2xl font-bold text-xs bg-slate-800 hover:bg-slate-700 text-white border border-white/[0.08] transition-all hover:scale-[1.01]"
            >
              Contact Team Sales
            </button>
          </div>

        </div>

        {/* Trust & Guarantee Banner */}
        <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-3">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>30-Day Money-Back Guarantee • Cancel anytime with 1 click • Private & Secure</span>
          </div>
          <span className="font-mono text-slate-500">Encrypted 256-Bit SSL Checkout</span>
        </div>
      </section>

      {/* ─────────────────────────────────────────────────────────────
          6. CALL TO ACTION BANNER (READY TO ACE YOUR INTERVIEW?)
      ───────────────────────────────────────────────────────────── */}
      <section className="relative rounded-3xl overflow-hidden p-8 sm:p-12 border border-indigo-500/30 bg-gradient-to-r from-indigo-950/80 via-[#0D121F] to-cyan-950/60 shadow-2xl">
        <div className="absolute top-0 right-0 -z-10 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="max-w-2xl space-y-4">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Start Free in Under 60 Seconds</span>
          </div>

          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Ready to Land Your Dream Tech Offer?
          </h2>

          <p className="text-base text-slate-300 leading-relaxed font-normal">
            Join over 10,000 engineers practicing with HireMind AI. No credit card required.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-3">
            <button
              onClick={() => setActiveTab('interview')}
              className="gradient-primary gradient-primary-hover px-7 py-3.5 rounded-2xl font-bold text-sm text-white shadow-xl shadow-indigo-600/30 transition-all flex items-center space-x-2 hover:scale-[1.02]"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>Try Free Interview</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>

            <button
              onClick={() => setActiveTab('resume')}
              className="px-6 py-3.5 rounded-2xl font-semibold text-sm bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-white/[0.08] transition-all flex items-center space-x-2 hover:scale-[1.02]"
            >
              <FileText className="w-4 h-4 text-indigo-400" />
              <span>Scan Resume with ATS</span>
            </button>
          </div>
        </div>
      </section>

      {/* Pro Activation Success Toast */}
      <AnimatePresence>
        {proSuccessAlert && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 right-6 z-50 p-4 rounded-2xl bg-emerald-950/95 border border-emerald-500/40 text-white shadow-2xl backdrop-blur-xl flex items-center space-x-3"
          >
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400">
              <CheckCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">HireMind Pro Activated!</h4>
              <p className="text-xs text-emerald-200">Unlimited mock interviews, voice mode & telemetry unlocked.</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Checkout / Activation Modal */}
      <AnimatePresence>
        {selectedPlanModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-md rounded-3xl bg-[#0D121F] border border-white/[0.1] p-6 sm:p-7 space-y-6 shadow-2xl relative"
            >
              <button
                onClick={() => setSelectedPlanModal(null)}
                className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white bg-white/[0.05]"
              >
                <X className="w-4 h-4" />
              </button>

              {selectedPlanModal === 'Pro' ? (
                <div className="space-y-5">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-cyan-400">
                      <Sparkles className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">HireMind AI Pro</h3>
                      <p className="text-xs text-slate-400">
                        {billingCycle === 'yearly' ? '$15/month ($180/yr)' : '$19/month billed monthly'}
                      </p>
                    </div>
                  </div>

                  <div className="p-4 rounded-2xl bg-slate-900/90 border border-white/[0.06] space-y-2 text-xs text-slate-300">
                    <div className="flex items-center space-x-2 text-white font-semibold pb-1 border-b border-white/[0.06]">
                      <Check className="w-4 h-4 text-emerald-400" />
                      <span>Instant Unlocks Upon Confirmation:</span>
                    </div>
                    <p>• Unlimited mock interviews & assessments</p>
                    <p>• 3D AI voice mode & wavy microphone telemetry</p>
                    <p>• Real-time eye & body camera proctoring</p>
                    <p>• Verified recruiter PDF certificate downloads</p>
                  </div>

                  <div className="space-y-3 pt-2">
                    <button
                      onClick={handleActivatePro}
                      className="w-full py-4 rounded-2xl font-bold text-sm gradient-primary gradient-primary-hover text-white shadow-xl shadow-indigo-600/30 transition-all flex items-center justify-center space-x-2"
                    >
                      <CreditCard className="w-4 h-4" />
                      <span>Confirm & Activate Pro Access</span>
                    </button>
                    <p className="text-[11px] text-center text-slate-400">
                      Simulated demo checkout — activates immediately with 1 click.
                    </p>
                  </div>
                </div>
              ) : (
                <div className="space-y-5">
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 rounded-2xl bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400">
                      <Briefcase className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">HireMind for Teams</h3>
                      <p className="text-xs text-slate-400">Enterprise & Bootcamp Cohorts</p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">
                    Custom deployment with centralized admin dashboard, candidate progress analytics, custom question pools, and full REST API access.
                  </p>

                  <div className="p-4 rounded-xl bg-slate-900 border border-white/[0.06] text-xs space-y-2 text-slate-300">
                    <div className="font-semibold text-white">Direct Enterprise Contact:</div>
                    <div className="font-mono text-cyan-400">enterprise@hiremind.ai</div>
                    <div className="text-slate-400">Or reach our team at +1 (800) 447-3646</div>
                  </div>

                  <button
                    onClick={() => setSelectedPlanModal(null)}
                    className="w-full py-3.5 rounded-2xl font-bold text-xs bg-slate-800 hover:bg-slate-700 text-white transition-all"
                  >
                    Close
                  </button>
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
};
