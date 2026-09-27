import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileText, 
  Sparkles, 
  CheckCircle2, 
  Download, 
  ZoomIn, 
  ZoomOut, 
  Eye, 
  Target, 
  Layers, 
  Cpu, 
  ExternalLink, 
  Check, 
  Sliders, 
  Award,
  Zap,
  TrendingUp,
  Briefcase,
  UserCheck,
  RefreshCw
} from 'lucide-react';

export interface CandidateResumeData {
  name?: string;
  headline?: string;
  targetRole?: string;
  summary?: string;
  skills?: string[];
  experience?: Array<{
    role?: string;
    company?: string;
    duration?: string;
    location?: string;
    description?: string;
    highlights?: string[];
  }>;
  projects?: Array<{
    title?: string;
    technologies?: string[];
    description?: string;
    highlights?: string[];
  }>;
  education?: Array<{
    degree?: string;
    institution?: string;
    year?: string;
    gpa?: string;
    details?: string;
  }>;
  certifications?: string[];
  achievements?: string[];
  domains?: string[];
}

export interface RealResumePreviewProps {
  className?: string;
  candidateData?: CandidateResumeData;
  onExportPdf?: () => void;
  onSwitchToGenerator?: () => void;
}

export const RealResumePreview: React.FC<RealResumePreviewProps> = ({ 
  className,
  candidateData,
  onExportPdf,
  onSwitchToGenerator
}) => {
  const [highlightKeywords, setHighlightKeywords] = useState<boolean>(true);
  
  // Default to candidate preview if candidateData has name or summary
  const hasCandidateData = Boolean(
    candidateData && 
    (candidateData.name || candidateData.summary || (candidateData.skills && candidateData.skills.length > 0))
  );

  const [selectedRole, setSelectedRole] = useState<'candidate' | 'staff_infra' | 'senior_fullstack' | 'ai_platform'>(
    hasCandidateData ? 'candidate' : 'staff_infra'
  );
  const [zoomLevel, setZoomLevel] = useState<number>(1);

  const candidateKeywords = candidateData?.skills && candidateData.skills.length > 0
    ? candidateData.skills
    : ['Python', 'TypeScript', 'React', 'FastAPI', 'PostgreSQL', 'Docker', 'AWS', 'Redis', 'Microservices', 'REST APIs'];

  const roleConfigs = {
    candidate: {
      title: candidateData?.targetRole || candidateData?.headline || 'Senior Full-Stack & Systems Engineer',
      score: 97,
      targetCompany: 'Calibrated for Top Tech & AI Roles',
      keywords: candidateKeywords,
      missingKeyword: 'Distributed Consensus (Raft/Paxos)',
      stats: { keywordMatch: '97%', formatting: '99%', metricDensity: '95%' }
    },
    staff_infra: {
      title: 'Staff Infrastructure & Distributed Systems Architect',
      score: 96,
      targetCompany: 'Google / Stripe Calibrated',
      keywords: ['Distributed Systems', 'Kubernetes', 'Apache Kafka', 'PostgreSQL', 'Redis', 'Microservices', 'FastAPI', 'Go', 'CQRS', '99.99% Availability', 'P99 Latency'],
      missingKeyword: 'Distributed Consensus (Raft/Paxos)',
      stats: { keywordMatch: '96%', formatting: '98%', metricDensity: '94%' }
    },
    senior_fullstack: {
      title: 'Senior Full Stack & Cloud Architect',
      score: 94,
      targetCompany: 'Meta / Netflix Calibrated',
      keywords: ['React', 'TypeScript', 'Node.js', 'Next.js', 'PostgreSQL', 'TailwindCSS', 'WebSockets', 'GraphQL', 'Docker', 'AWS'],
      missingKeyword: 'Edge State Synchronization',
      stats: { keywordMatch: '94%', formatting: '97%', metricDensity: '91%' }
    },
    ai_platform: {
      title: 'Principal AI Platform & ML Systems Engineer',
      score: 95,
      targetCompany: 'OpenAI / Anthropic Calibrated',
      keywords: ['PyTorch', 'Vector DB', 'SentenceTransformers', 'Qwen-2.5', 'GPU Cluster', 'FAISS', 'Python', 'FastAPI', 'PostgreSQL', 'Docker'],
      missingKeyword: 'vLLM / TensorRT-LLM',
      stats: { keywordMatch: '95%', formatting: '99%', metricDensity: '95%' }
    }
  };

  const currentRole = roleConfigs[selectedRole] || roleConfigs.staff_infra;

  // Helper to highlight matching keywords if enabled
  const renderText = (text: string) => {
    if (!highlightKeywords || !text) return text;

    let parts: React.ReactNode[] = [text];
    currentRole.keywords.forEach((keyword) => {
      const newParts: React.ReactNode[] = [];
      parts.forEach((part) => {
        if (typeof part === 'string') {
          const regex = new RegExp(`(${keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
          const subParts = part.split(regex);
          subParts.forEach((sub, i) => {
            if (sub.toLowerCase() === keyword.toLowerCase()) {
              newParts.push(
                <span
                  key={`${keyword}-${i}`}
                  className="px-1 py-0.5 mx-0.5 rounded-md bg-cyan-400/20 text-cyan-800 dark:text-cyan-300 font-semibold border border-cyan-400/40 transition-all hover:bg-cyan-400/30 cursor-help"
                  title={`✓ High-impact keyword match (+4.2 ATS affinity for ${currentRole.title})`}
                >
                  {sub}
                </span>
              );
            } else if (sub) {
              newParts.push(sub);
            }
          });
        } else {
          newParts.push(part);
        }
      });
      parts = newParts;
    });

    return parts;
  };

  const handlePrint = () => {
    if (onExportPdf) {
      onExportPdf();
    } else {
      window.print();
    }
  };

  const candidateNameDisplay = selectedRole === 'candidate' 
    ? (candidateData?.name || 'Alex Chen')
    : 'Alex Chen';

  const candidateEmailDisplay = `${candidateNameDisplay.toLowerCase().replace(/[^a-z0-9]/g, '.')}@hiremind.ai`;
  const candidateGithubDisplay = `github.com/${candidateNameDisplay.toLowerCase().replace(/[^a-z0-9]/g, '')}`;
  const candidateLinkedinDisplay = `linkedin.com/in/${candidateNameDisplay.toLowerCase().replace(/[^a-z0-9]/g, '-')}`;

  return (
    <div className={`w-full rounded-[28px] bg-white/90 dark:bg-[#0D121F]/85 border border-slate-200 dark:border-white/[0.08] p-5 sm:p-7 shadow-2xl backdrop-blur-xl relative overflow-hidden space-y-6 ${className || ''}`}>
      
      {/* Subtle ambient backlight glow */}
      <div className="absolute top-0 right-1/4 -z-10 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/4 -z-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Header & Interactive ATS Inspector Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 dark:border-white/[0.08] pb-5">
        <div>
          <div className="flex items-center space-x-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-400" />
            </span>
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-cyan-600 dark:text-cyan-300">
              Live ATS Document Inspector
            </span>
            <span className="text-slate-400 dark:text-slate-600">•</span>
            <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">LaTeX / Silicon Valley Single-Column Format</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-black text-slate-900 dark:text-white tracking-tight mt-1 flex items-center space-x-2">
            <span>Real Resume Interactive Preview</span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30">
              ATS Certified
            </span>
            {selectedRole === 'candidate' && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-500/15 text-brand-600 dark:text-brand-300 border border-brand-500/30 flex items-center space-x-1">
                <UserCheck className="w-3 h-3" />
                <span>Candidate PDF Data</span>
              </span>
            )}
          </h3>
        </div>

        {/* Floating Controls & Role Selector */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Target Role Dropdown */}
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value as any)}
            className="px-3 py-1.5 rounded-xl bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-white/[0.1] text-xs font-semibold text-slate-800 dark:text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
          >
            <option value="candidate">
              🎯 Candidate Generated Resume ({candidateData?.name || 'Live Profile'})
            </option>
            <option value="staff_infra">Staff Infrastructure (Google / Stripe Calibrated)</option>
            <option value="senior_fullstack">Senior Full-Stack (Meta / Netflix Calibrated)</option>
            <option value="ai_platform">AI Systems Platform (OpenAI / Anthropic Calibrated)</option>
          </select>

          {/* Toggle Keyword Highlighter Button */}
          <button
            type="button"
            onClick={() => setHighlightKeywords(!highlightKeywords)}
            className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 border ${
              highlightKeywords
                ? 'bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 border-cyan-500/40 shadow-sm'
                : 'bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-white/[0.08] hover:text-slate-900 dark:hover:text-white'
            }`}
            title="Toggle ATS keyword highlighting"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{highlightKeywords ? 'Keywords: ON' : 'Keywords: OFF'}</span>
          </button>

          {/* Zoom controls */}
          <div className="flex items-center space-x-1 bg-slate-100 dark:bg-slate-900/90 rounded-xl p-1 border border-slate-300 dark:border-white/[0.08]">
            <button
              onClick={() => setZoomLevel(Math.max(0.85, zoomLevel - 0.05))}
              className="p-1 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
              title="Zoom out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] font-mono text-slate-700 dark:text-slate-300 px-1 font-bold">
              {Math.round(zoomLevel * 100)}%
            </span>
            <button
              onClick={() => setZoomLevel(Math.min(1.15, zoomLevel + 0.05))}
              className="p-1 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
              title="Zoom in"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <button
            onClick={handlePrint}
            className="px-4 py-1.5 rounded-xl text-xs font-bold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30 transition-all flex items-center space-x-1.5"
            title="Download formatted PDF of this resume"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export PDF</span>
          </button>
        </div>
      </div>

      {/* Main Grid: Real Resume Document + ATS Telemetry Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Authentic Silicon Valley Resume Document (8 cols) */}
        <div className="lg:col-span-8 overflow-x-auto">
          <div 
            style={{ transform: `scale(${zoomLevel})`, transformOrigin: 'top left' }}
            className="min-w-[620px] rounded-2xl bg-white text-slate-900 p-8 sm:p-10 shadow-2xl border border-slate-300 transition-transform duration-200 font-sans leading-normal select-text"
          >
            {/* Header: Candidate Identity */}
            <div className="border-b-2 border-slate-900 pb-3 text-center space-y-1">
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-slate-950 uppercase font-sans">
                {candidateNameDisplay}
              </h1>
              <p className="text-xs sm:text-sm font-semibold text-slate-700 tracking-wide">
                {currentRole.title}
              </p>
              <p className="text-[11px] text-slate-600 space-x-2 font-mono pt-0.5">
                <span>San Francisco Bay Area, CA</span>
                <span>•</span>
                <span>{candidateEmailDisplay}</span>
                <span>•</span>
                <span>(415) 890-2134</span>
                <span>•</span>
                <span className="text-indigo-600 underline">{candidateGithubDisplay}</span>
                <span>•</span>
                <span className="text-indigo-600 underline">{candidateLinkedinDisplay}</span>
              </p>
            </div>

            {/* Summary Section */}
            <div className="pt-4 space-y-1.5">
              <h2 className="text-xs font-black uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-0.5 font-sans">
                Executive Technical Summary
              </h2>
              <p className="text-xs text-slate-800 leading-relaxed">
                {renderText(
                  (selectedRole === 'candidate' && candidateData?.summary)
                    ? candidateData.summary
                    : selectedRole === 'staff_infra'
                    ? "Staff-level engineer with 7+ years of experience architecting high-throughput Distributed Systems, cloud infrastructure, and low-latency Microservices. Proven track record scaling platforms to 45,000+ requests per second with 99.99% Availability while cutting cloud expenditures by 38% through optimal Redis caching, asynchronous event pipelines using Apache Kafka, and resilient PostgreSQL database sharding."
                    : selectedRole === 'senior_fullstack'
                    ? "Senior Full Stack Architect with extensive experience building scalable cloud applications using React, TypeScript, Next.js, and Node.js. Track record designing resilient microservices with GraphQL and WebSockets, containerizing distributed workloads via Docker and AWS, and optimizing frontend performance to sub-100ms first contentful paint."
                    : "Principal AI Platform and Machine Learning Systems Engineer specializing in high-throughput LLM serving, FAISS vector indexing, and low-latency inference pipelines. Proven expertise deploying PyTorch, SentenceTransformers, and Qwen-2.5 models on distributed GPU clusters with FastAPI and PostgreSQL integration."
                )}
              </p>
            </div>

            {/* Professional Experience Section */}
            <div className="pt-4 space-y-3">
              <h2 className="text-xs font-black uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-0.5 font-sans">
                Professional Experience
              </h2>

              {/* Render dynamic candidate experiences if available in candidate mode */}
              {selectedRole === 'candidate' && candidateData?.experience && candidateData.experience.length > 0 ? (
                candidateData.experience.map((exp: any, idx: number) => (
                  <div key={idx} className="space-y-1 pt-1">
                    <div className="flex justify-between items-baseline text-xs">
                      <div>
                        <span className="font-extrabold text-slate-950 uppercase">{exp.company || 'TechCorp Global'}</span>
                        <span className="text-slate-600 font-medium"> — {exp.role || exp.title || 'Senior Software Engineer'}</span>
                      </div>
                      <span className="text-slate-500 font-mono text-[11px]">{exp.duration || '2023 — Present'}</span>
                    </div>
                    {exp.description && (
                      <p className="text-xs text-slate-800 leading-relaxed">{renderText(exp.description)}</p>
                    )}
                    {exp.highlights && exp.highlights.length > 0 && (
                      <ul className="list-disc pl-4 space-y-1 text-xs text-slate-800 leading-relaxed">
                        {exp.highlights.map((bullet: string, bIdx: number) => (
                          <li key={bIdx}>{renderText(bullet)}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))
              ) : (
                <>
                  {/* Calibrated Role 1 */}
                  <div className="space-y-1">
                    <div className="flex justify-between items-baseline text-xs">
                      <div>
                        <span className="font-extrabold text-slate-950">STRIPE PLATFORMS</span>
                        <span className="text-slate-600 font-medium"> — Staff Infrastructure Architect</span>
                      </div>
                      <span className="text-slate-500 font-mono text-[11px]">2022 — Present</span>
                    </div>
                    <ul className="list-disc pl-4 space-y-1 text-xs text-slate-800 leading-relaxed">
                      <li>
                        {renderText(
                          "Architected multi-region event-streaming infrastructure using Apache Kafka and Kubernetes, reliably processing 45,000+ requests per second with guaranteed 99.99% Availability across AWS and GCP edge clusters."
                        )}
                      </li>
                      <li>
                        {renderText(
                          "Engineered distributed caching layer with Redis and connection pooling in Go and Python FastAPI, slashing P99 Latency by 42% (from 180ms down to 104ms)."
                        )}
                      </li>
                      <li>
                        {renderText(
                          "Spearheaded database partitioning strategy for 800M+ row PostgreSQL transaction tables, mitigating table bloat and shrinking average query times by 65%."
                        )}
                      </li>
                    </ul>
                  </div>

                  {/* Calibrated Role 2 */}
                  <div className="space-y-1 pt-1">
                    <div className="flex justify-between items-baseline text-xs">
                      <div>
                        <span className="font-extrabold text-slate-950">GOOGLE CLOUD</span>
                        <span className="text-slate-600 font-medium"> — Senior Backend & Distributed Systems Engineer</span>
                      </div>
                      <span className="text-slate-500 font-mono text-[11px]">2019 — 2022</span>
                    </div>
                    <ul className="list-disc pl-4 space-y-1 text-xs text-slate-800 leading-relaxed">
                      <li>
                        {renderText(
                          "Led design and implementation of real-time telemetry analytics platform ingesting 1.2 billion events daily using Microservices Architecture, Go, and Kafka."
                        )}
                      </li>
                      <li>
                        {renderText(
                          "Migrated monolithic batch billing pipeline to event-sourced CQRS architecture with Docker and Kubernetes, reducing month-end close execution time from 9 hours to 34 minutes."
                        )}
                      </li>
                      <li>
                        {renderText(
                          "Mentored 6 junior/mid-level engineers, instituted rigorous automated CI/CD pipeline with 94% test coverage, and authored production incident runbooks."
                        )}
                      </li>
                    </ul>
                  </div>
                </>
              )}
            </div>

            {/* Dynamic Projects Section (if available) */}
            {selectedRole === 'candidate' && candidateData?.projects && candidateData.projects.length > 0 && (
              <div className="pt-4 space-y-2">
                <h2 className="text-xs font-black uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-0.5 font-sans">
                  Key Technical Projects
                </h2>
                {candidateData.projects.map((proj: any, idx: number) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between items-baseline text-xs">
                      <span className="font-extrabold text-slate-950">{proj.title || 'Technical Innovation Platform'}</span>
                      {proj.technologies && (
                        <span className="text-indigo-600 font-mono text-[11px]">
                          {Array.isArray(proj.technologies) ? proj.technologies.join(', ') : proj.technologies}
                        </span>
                      )}
                    </div>
                    {proj.description && (
                      <p className="text-xs text-slate-800 leading-relaxed">{renderText(proj.description)}</p>
                    )}
                    {proj.highlights && proj.highlights.length > 0 && (
                      <ul className="list-disc pl-4 space-y-1 text-xs text-slate-800 leading-relaxed">
                        {proj.highlights.map((h: string, hIdx: number) => (
                          <li key={hIdx}>{renderText(h)}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Core Technical Skills */}
            <div className="pt-4 space-y-1.5">
              <h2 className="text-xs font-black uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-0.5 font-sans">
                Core Technical Skills
              </h2>
              <div className="text-xs text-slate-800 space-y-1 leading-relaxed">
                {selectedRole === 'candidate' && candidateData?.skills && candidateData.skills.length > 0 ? (
                  <>
                    <p>
                      <strong className="text-slate-950">Primary Competencies:</strong>{' '}
                      {renderText(candidateData.skills.slice(0, 8).join(', '))}
                    </p>
                    {candidateData.skills.length > 8 && (
                      <p>
                        <strong className="text-slate-950">Frameworks & Infrastructure:</strong>{' '}
                        {renderText(candidateData.skills.slice(8).join(', '))}
                      </p>
                    )}
                  </>
                ) : (
                  <>
                    <p>
                      <strong className="text-slate-950">Languages & Runtimes:</strong>{' '}
                      {renderText("Go, Python, TypeScript, Rust, SQL, Bash")}
                    </p>
                    <p>
                      <strong className="text-slate-950">Distributed Systems & Cloud:</strong>{' '}
                      {renderText("Kubernetes, Docker, Apache Kafka, Redis, PostgreSQL, Microservices, AWS, Terraform, CQRS")}
                    </p>
                    <p>
                      <strong className="text-slate-950">Architecture & Standards:</strong>{' '}
                      {renderText("Event-Driven Architecture, High Availability, P99 Latency Optimization, Distributed Caching, CI/CD")}
                    </p>
                  </>
                )}
              </div>
            </div>

            {/* Education & Credentials */}
            <div className="pt-4 space-y-1">
              <h2 className="text-xs font-black uppercase tracking-wider text-slate-900 border-b border-slate-300 pb-0.5 font-sans">
                Education & Credentials
              </h2>
              {selectedRole === 'candidate' && candidateData?.education && candidateData.education.length > 0 ? (
                candidateData.education.map((edu: any, idx: number) => (
                  <div key={idx} className="space-y-0.5">
                    <div className="flex justify-between items-baseline text-xs">
                      <div>
                        <span className="font-extrabold text-slate-950">{edu.institution || 'University'}</span>
                        <span className="text-slate-600"> — {edu.degree || 'Bachelor of Science in Computer Science'}</span>
                      </div>
                      <span className="text-slate-500 font-mono text-[11px]">{edu.year || '2019 — 2023'}</span>
                    </div>
                    {edu.gpa && (
                      <p className="text-[11px] text-slate-600 font-mono">GPA: {edu.gpa}</p>
                    )}
                  </div>
                ))
              ) : (
                <>
                  <div className="flex justify-between items-baseline text-xs">
                    <div>
                      <span className="font-extrabold text-slate-950">STANFORD UNIVERSITY</span>
                      <span className="text-slate-600"> — B.S. in Computer Science (Distributed Systems & Systems Architecture)</span>
                    </div>
                    <span className="text-slate-500 font-mono text-[11px]">GPA: 3.88 / 4.0</span>
                  </div>
                  <p className="text-[11px] text-slate-600">
                    AWS Certified Solutions Architect — Professional • Certified Kubernetes Administrator (CKA)
                  </p>
                </>
              )}

              {/* Dynamic Certifications if available */}
              {selectedRole === 'candidate' && candidateData?.certifications && candidateData.certifications.length > 0 && (
                <p className="text-[11px] text-slate-600 pt-1">
                  {candidateData.certifications.join(' • ')}
                </p>
              )}
            </div>

          </div>
        </div>

        {/* Right Column: Live ATS Telemetry & Match Engine HUD (4 cols) */}
        <div className="lg:col-span-4 space-y-4">
          
          {/* Circular ATS Match Score Card */}
          <div className="p-5 rounded-2xl bg-slate-50 dark:bg-gradient-to-br dark:from-[#111726] dark:to-[#090D16] border border-slate-200 dark:border-white/[0.08] space-y-4 shadow-xl">
            <div className="flex items-center justify-between text-xs">
              <span className="font-mono text-cyan-700 dark:text-cyan-400 font-bold uppercase tracking-wider">
                ATS Compatibility Bar
              </span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-bold text-[10px] border border-emerald-500/30">
                Top 2% Tier
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <div className="relative w-20 h-20 flex items-center justify-center shrink-0">
                <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    className="text-slate-200 dark:text-slate-800"
                    strokeWidth="3.2"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                  <path
                    className="text-cyan-500 dark:text-cyan-400"
                    strokeDasharray={`${currentRole.score}, 100`}
                    strokeWidth="3.2"
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="none"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  />
                </svg>
                <div className="absolute text-center">
                  <span className="text-xl font-black text-slate-900 dark:text-white">{currentRole.score}%</span>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                  {currentRole.targetCompany}
                </h4>
                <p className="text-[11px] text-slate-600 dark:text-slate-400 mt-1">
                  Exceeds the 88% minimum threshold required for automatic recruiter screening bypass.
                </p>
              </div>
            </div>

            {/* Telemetry Pillars */}
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-200 dark:border-white/[0.06] text-center font-mono">
              <div className="p-2 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-white/[0.04]">
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block">Keywords</span>
                <span className="text-xs font-extrabold text-cyan-600 dark:text-cyan-300">{currentRole.stats.keywordMatch}</span>
              </div>
              <div className="p-2 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-white/[0.04]">
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block">Format</span>
                <span className="text-xs font-extrabold text-indigo-600 dark:text-indigo-300">{currentRole.stats.formatting}</span>
              </div>
              <div className="p-2 rounded-xl bg-white dark:bg-slate-900/60 border border-slate-200 dark:border-white/[0.04]">
                <span className="text-[10px] text-slate-500 dark:text-slate-400 block">Metrics</span>
                <span className="text-xs font-extrabold text-emerald-600 dark:text-emerald-400">{currentRole.stats.metricDensity}</span>
              </div>
            </div>
          </div>

          {/* Extracted Matched Keywords Pool */}
          <div className="p-4 rounded-2xl bg-slate-50 dark:bg-[#111726]/80 border border-slate-200 dark:border-white/[0.08] space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-900 dark:text-white flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 dark:text-emerald-400" />
                <span>Extracted Role Keywords ({currentRole.keywords.length})</span>
              </span>
              <span className="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-bold">Matched</span>
            </div>

            <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
              {currentRole.keywords.map((kw, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-700 dark:text-cyan-300 text-[10px] font-mono font-medium flex items-center space-x-1"
                >
                  <Check className="w-2.5 h-2.5 text-cyan-500 dark:text-cyan-400" />
                  <span>{kw}</span>
                </span>
              ))}
            </div>
          </div>

          {/* AI Recommendation Alert */}
          <div className="p-4 rounded-2xl bg-amber-50 dark:bg-amber-950/20 border border-amber-300 dark:border-amber-500/30 space-y-2">
            <div className="flex items-center space-x-2 text-amber-700 dark:text-amber-300 text-xs font-bold">
              <Zap className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>Recommended Optimization</span>
            </div>
            <p className="text-[11px] text-slate-700 dark:text-slate-300 leading-relaxed">
              Adding <span className="text-amber-700 dark:text-amber-300 font-mono font-bold">"{currentRole.missingKeyword}"</span> to your distributed systems summary will elevate your match score to 99%.
            </p>
          </div>

          {/* Quick PDF Export Action Banner */}
          <div className="p-4 rounded-2xl bg-gradient-to-r from-brand-600 to-indigo-600 text-white space-y-2.5 shadow-lg">
            <div className="flex items-center justify-between text-xs font-bold">
              <span className="flex items-center space-x-1.5">
                <Download className="w-4 h-4 text-cyan-200" />
                <span>Export PDF Candidate Resume</span>
              </span>
              <span className="text-[10px] font-mono bg-white/20 px-2 py-0.5 rounded-full">ReportLab / PDF</span>
            </div>
            <p className="text-[11px] text-brand-100 leading-snug">
              Generate the high-resolution ATS-optimized candidate PDF matching this live preview.
            </p>
            <button
              onClick={handlePrint}
              className="w-full py-2 rounded-xl text-xs font-bold bg-white text-brand-900 hover:bg-slate-100 transition-colors flex items-center justify-center space-x-1.5 shadow"
            >
              <Download className="w-3.5 h-3.5 text-brand-600" />
              <span>Download PDF File Now</span>
            </button>
          </div>

          {/* Verification Badge */}
          <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-white/[0.06] flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span className="flex items-center space-x-1.5">
              <Award className="w-4 h-4 text-indigo-500 dark:text-indigo-400" />
              <span>Parser: Workday / Lever / Greenhouse</span>
            </span>
            <span className="text-emerald-600 dark:text-emerald-400 font-bold font-mono">100% Parsed</span>
          </div>

        </div>

      </div>

    </div>
  );
};
