import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bot, 
  X, 
  Send, 
  Sparkles, 
  BrainCircuit, 
  Volume2, 
  VolumeX, 
  ChevronDown, 
  ArrowRight,
  Maximize2,
  Minimize2,
  Trash2,
  HelpCircle,
  CheckCircle2
} from 'lucide-react';
import { api } from '../../services/api';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  time: string;
  actionTab?: string;
  actionLabel?: string;
}

interface HireMindAIAssistantProps {
  onNavigateTab: (tab: string) => void;
}

export const HireMindAIAssistant: React.FC<HireMindAIAssistantProps> = ({ onNavigateTab }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const initialMessages: Message[] = [
    {
      id: 'welcome',
      sender: 'ai',
      text: "👋 Welcome to **RAAHSETU**! I'm your dedicated platform copilot. Ask me anything about our 3D mock interviews, skill assessments, audio speech evaluation, ATS resume scanner, or verified certificates.",
      time: 'Just now',
    }
  ];

  const [messages, setMessages] = useState<Message[]>(initialMessages);

  const quickQuestions = [
    {
      q: "How does the 3D Mock Interview work?",
      tab: "interview",
      label: "Open Interview Room"
    },
    {
      q: "Why is audio playback audible & how does it work?",
      tab: "interview",
      label: "Test Audio"
    },
    {
      q: "Explain Skill Assessments & negative marking",
      tab: "assessment",
      label: "Start Assessment"
    },
    {
      q: "How does ATS Resume scoring work?",
      tab: "resume",
      label: "Open ATS Studio"
    },
    {
      q: "Where can I download my verified certificate?",
      tab: "badges",
      label: "View Credentials"
    }
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }, [messages, isOpen, isMinimized]);

  // Knowledge base answering logic
  const getAIResponse = (query: string): { text: string; tab?: string; label?: string } => {
    const q = query.toLowerCase();

    if (q.includes('interview') || q.includes('mock') || q.includes('avatar') || q.includes('3d')) {
      return {
        text: "🎯 **RAAHSETU 3D Mock Interview Engine**:\n\n• **3D Holographic Core**: Reacts in real-time to speaking, listening, and evaluating states.\n• **Speech Recognition & Real Audio**: Supports natural voice recording via microphone, backed by server-side WAV text-to-speech audio.\n• **6-Dimension Scoring**: Correctness, depth, communication clarity, relevance, architecture trade-offs, and pacing.\n• **Adaptive Follow-ups**: The AI analyzes your answer using Qwen SLM and poses realistic engineering follow-up questions.",
        tab: 'interview',
        label: 'Launch Mock Interview'
      };
    }

    if (q.includes('audio') || q.includes('sound') || q.includes('voice') || q.includes('audible') || q.includes('hear')) {
      return {
        text: "🔊 **Audio & Voice System**:\n\n• **Dual-Engine Audio**: Question audio is streamed directly from our backend TTS engine (`/interviews/tts`) with browser speech synthesis fallback.\n• **Audible Playback**: Questions can be heard automatically or repeated anytime using the **Repeat Audio** button.\n• **Volume & Mute**: Easily toggle sound on/off or test voice with the integrated audio controller.\n• **Speech-to-Text**: Click the microphone button to dictate answers in real time.",
        tab: 'interview',
        label: 'Go to Interview Room'
      };
    }

    if (q.includes('assessment') || q.includes('test') || q.includes('exam') || q.includes('negative')) {
      return {
        text: "⏱️ **Standardized Skill Assessments**:\n\n• **3 Key Sections**: Aptitude & Logic, Verbal English, and Data Structures & Algorithms (DSA).\n• **Timed Challenges**: 20 minutes per section with a live countdown timer.\n• **Scoring Formula**: +1.0 for correct answers, -0.25 negative marking for wrong options, and 0 for skipped questions.\n• **Automatic Certification**: Passing an assessment mints an official cryptographically verified certificate.",
        tab: 'assessment',
        label: 'Take Assessment'
      };
    }

    if (q.includes('resume') || q.includes('ats') || q.includes('cv')) {
      return {
        text: "📄 **ATS Resume Studio**:\n\n• **Vector Similarity**: Matches your resume competencies against real job requirements at Google, Microsoft, and Amazon.\n• **Skill Gap Analysis**: Pinpoints missing frameworks and keywords needed for high-stakes ATS filters.\n• **AI CV Generator**: Generates formatted, recruiter-ready CV summaries with instant PDF download.",
        tab: 'resume',
        label: 'Analyze Resume'
      };
    }

    if (q.includes('certificate') || q.includes('badge') || q.includes('download') || q.includes('cred')) {
      return {
        text: "🏆 **Verified Credentials & Badges**:\n\n• **Cryptographic Verification**: Each certificate carries a unique Credential ID (`HM-2026-928A`) for LinkedIn and recruiter verification.\n• **PDF Download**: Export high-resolution official PDF certificates directly with 1 click.\n• **Milestone Badges**: Unlock 1-5 star badges as your interview scores and XP level increase.",
        tab: 'badges',
        label: 'Download Certificate'
      };
    }

    if (q.includes('job') || q.includes('career') || q.includes('salary') || q.includes('company')) {
      return {
        text: "💼 **Jobs & Career Roadmaps**:\n\n• **Direct Tech Matches**: Browse active openings at Google, Stripe, and AWS with 93%–96% compatibility scores.\n• **Salary Transparency**: View verified compensation bands ($190k - $275k) and required tech stacks.\n• **Learning Roadmaps**: Step-by-step career path progressions from Junior to Staff Architect.",
        tab: 'career',
        label: 'Explore Tech Jobs'
      };
    }

    if (q.includes('light') || q.includes('dark') || q.includes('theme')) {
      return {
        text: "🌓 **Theme Switching**:\n\n• RAAHSETU supports both **Dark Obsidian** (cyberpunk engineering aesthetic) and **Light Mode** (crisp high-contrast enterprise theme).\n• Click the Sun/Moon icon in the top navigation bar to toggle anytime! Your preference is automatically saved.",
      };
    }

    // Default intelligent response
    return {
      text: `RAAHSETU is an autonomous career preparation platform. You can:\n\n1. **Practice 3D AI Interviews** with voice questions and rubric feedback.\n2. **Take Timed Assessments** across Aptitude, English, and DSA.\n3. **Scan your Resume** for ATS readiness.\n4. **Download verified certificates** for LinkedIn.\n\nWhat would you like to explore first?`,
      tab: 'dashboard',
      label: 'Explore Platform'
    };
  };

  const handleSendMessage = (textToSend?: string) => {
    const text = textToSend || inputText;
    if (!text.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: text.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInputText('');
    setIsTyping(true);

    setTimeout(() => {
      const responseData = getAIResponse(text);
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: responseData.text,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        actionTab: responseData.tab,
        actionLabel: responseData.label,
      };

      setMessages((prev) => [...prev, aiMsg]);
      setIsTyping(false);

      // Play audio if not muted
      if (!isMuted && 'speechSynthesis' in window) {
        try {
          const cleanText = responseData.text.replace(/[*#•_-]/g, ' ');
          const utterance = new SpeechSynthesisUtterance(cleanText.slice(0, 140));
          utterance.rate = 1.05;
          window.speechSynthesis.speak(utterance);
        } catch (e) {
          console.warn('AI voice playback skipped');
        }
      }
    }, 450);
  };

  const clearChat = () => {
    setMessages(initialMessages);
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans select-none">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ 
              opacity: 1, 
              scale: 1, 
              y: 0,
              height: isMinimized ? '56px' : '560px'
            }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            className={`w-[360px] sm:w-[410px] rounded-2xl glass-panel border border-white/[0.12] dark:border-white/[0.12] shadow-2xl flex flex-col overflow-hidden backdrop-blur-2xl transition-all duration-200 ${
              isMinimized ? 'bg-[#0D121F]' : 'bg-[#0B0F1A]/95'
            }`}
          >
            {/* Header */}
            <div className="h-14 px-4 bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-900 border-b border-white/[0.08] flex items-center justify-between shrink-0">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-600/30">
                  <BrainCircuit className="w-4 h-4 text-white" />
                </div>
                <div>
                  <div className="flex items-center space-x-1.5">
                    <span className="font-bold text-sm text-white">RAAHSETU Copilot</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  </div>
                  <span className="text-[10px] text-slate-400 font-mono">Platform Intelligence</span>
                </div>
              </div>

              <div className="flex items-center space-x-1 text-slate-400">
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  title={isMuted ? "Unmute Voice" : "Mute Voice"}
                  className="p-1.5 rounded-lg hover:text-white hover:bg-white/[0.06] transition-colors"
                >
                  {isMuted ? <VolumeX className="w-4 h-4 text-slate-500" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
                </button>

                <button
                  onClick={clearChat}
                  title="Clear Chat History"
                  className="p-1.5 rounded-lg hover:text-white hover:bg-white/[0.06] transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>

                <button
                  onClick={() => setIsMinimized(!isMinimized)}
                  title={isMinimized ? "Expand" : "Minimize"}
                  className="p-1.5 rounded-lg hover:text-white hover:bg-white/[0.06] transition-colors"
                >
                  {isMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
                </button>

                <button
                  onClick={() => setIsOpen(false)}
                  title="Close"
                  className="p-1.5 rounded-lg hover:text-white hover:bg-white/[0.06] transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Chat Body */}
            {!isMinimized && (
              <>
                <div className="flex-1 p-4 overflow-y-auto space-y-3.5 text-xs">
                  {messages.map((m) => (
                    <div
                      key={m.id}
                      className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
                    >
                      <div
                        className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 space-y-1.5 ${
                          m.sender === 'user'
                            ? 'bg-indigo-600 text-white rounded-br-xs'
                            : 'bg-slate-900/90 text-slate-200 border border-white/[0.08] rounded-bl-xs'
                        }`}
                      >
                        <div className="whitespace-pre-wrap leading-relaxed text-xs">
                          {m.text}
                        </div>

                        {/* Interactive Navigation Action Pill */}
                        {m.actionTab && (
                          <div className="pt-1.5 border-t border-white/[0.1]">
                            <button
                              onClick={() => {
                                onNavigateTab(m.actionTab!);
                                setIsOpen(false);
                              }}
                              className="w-full py-1.5 px-3 rounded-lg text-xs font-bold bg-white text-slate-900 hover:bg-slate-100 flex items-center justify-center space-x-1.5 transition-colors shadow-sm"
                            >
                              <span>{m.actionLabel || 'Go to Module'}</span>
                              <ArrowRight className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </div>
                      <span className="text-[10px] text-slate-500 mt-1 px-1 font-mono">{m.time}</span>
                    </div>
                  ))}

                  {isTyping && (
                    <div className="flex items-center space-x-1.5 p-3 rounded-2xl bg-slate-900/80 border border-white/[0.06] w-20">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-bounce [animation-delay:0.2s]" />
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-bounce [animation-delay:0.4s]" />
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Quick Suggestion Chips */}
                <div className="px-3 py-2 border-t border-white/[0.06] bg-slate-950/40">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold block mb-1.5 px-1">
                    Suggested Questions
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {quickQuestions.map((q, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(q.q)}
                        className="px-2.5 py-1 rounded-md text-[11px] bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 hover:text-white border border-white/[0.06] transition-colors text-left truncate max-w-[200px]"
                      >
                        {q.q}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Input Form */}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="p-3 border-t border-white/[0.08] bg-slate-950/60 flex items-center space-x-2"
                >
                  <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Ask about mock interviews, scoring, tests..."
                    className="flex-1 bg-slate-900/90 border border-white/[0.08] text-white text-xs rounded-xl px-3.5 py-2.5 focus:border-indigo-500 focus:outline-none placeholder:text-slate-500"
                  />
                  <button
                    type="submit"
                    disabled={!inputText.trim()}
                    className="p-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-indigo-600/30"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Trigger Button on the right side */}
      {!isOpen && (
        <motion.button
          onClick={() => setIsOpen(true)}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative group flex items-center space-x-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 text-white font-medium text-xs shadow-2xl shadow-indigo-600/40 border border-white/20 transition-all"
        >
          <div className="relative">
            <Bot className="w-5 h-5 text-white animate-pulse" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 border-2 border-[#090D16]" />
          </div>
          <span className="font-bold tracking-wide">Ask RAAHSETU</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-white/20 font-bold uppercase tracking-wider">
            AI
          </span>
        </motion.button>
      )}
    </div>
  );
};
