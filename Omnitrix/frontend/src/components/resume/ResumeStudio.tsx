import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../../services/api';
import { 
  FileText, 
  UploadCloud, 
  Sparkles, 
  CheckCircle, 
  Download, 
  Brain, 
  AlertCircle,
  FileCheck,
  RefreshCw,
  Zap
} from 'lucide-react';
import { RealResumePreview } from './RealResumePreview';

export const ResumeStudio: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'upload' | 'text' | 'generate' | 'preview'>('preview');
  const [file, setFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  // Resume Generator State
  const [candidateName, setCandidateName] = useState('Alex Chen');
  const [targetChoice, setTargetChoice] = useState('Full Stack Software Engineer');
  const [generatedCv, setGeneratedCv] = useState<any>(null);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const res = await api.uploadResume(file);
      setAnalysisResult(res);
    } catch (err: any) {
      alert(`Resume upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTextAnalyze = async () => {
    if (!resumeText.trim()) return;
    setLoading(true);
    try {
      const res = await api.analyzeResumeText(resumeText);
      setAnalysisResult(res);
    } catch (err: any) {
      alert(`Resume analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCV = async () => {
    setLoading(true);
    try {
      const res = await api.generateResume(candidateName, targetChoice);
      setGeneratedCv(res);
    } catch (err: any) {
      alert(`CV generation error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    try {
      const blob = await api.downloadGeneratedResumePdf(candidateName, targetChoice);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${candidateName.replace(/\s+/g, '_')}_Resume.pdf`;
      a.click();
    } catch (err: any) {
      alert(`PDF download error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold mb-3">
          <Sparkles className="w-3.5 h-3.5 text-cyber-cyan" />
          <span>Vector ATS & Semantic Skill Extraction</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Smart Resume Studio & <span className="bg-gradient-to-r from-cyber-cyan to-brand-400 bg-clip-text text-transparent">ATS Matcher</span>
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm mt-2">
          Extract technical skills, compute role gap affinities, and generate AI-crafted, ATS-optimized resumes.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center space-x-2">
        <button
          onClick={() => setActiveTab('upload')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'upload'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-white/5'
          }`}
        >
          Upload Document (.PDF / .DOCX)
        </button>
        <button
          onClick={() => setActiveTab('text')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'text'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-white/5'
          }`}
        >
          Paste Raw Resume Text
        </button>
        <button
          onClick={() => setActiveTab('generate')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'generate'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-white/5'
          }`}
        >
          AI Resume Generator
        </button>
        <button
          onClick={() => setActiveTab('preview')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
            activeTab === 'preview'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 hover:text-white border border-white/5'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5 text-cyber-cyan" />
          <span>Real Resume Preview</span>
        </button>
      </div>

      {/* Live ATS Document Preview View */}
      {activeTab === 'preview' && (
        <div className="space-y-6">
          <RealResumePreview
            candidateData={{
              name: candidateName,
              targetRole: targetChoice,
              summary: generatedCv?.summary,
              skills: generatedCv?.skills || (analysisResult?.skills ? analysisResult.skills.map((s: any) => typeof s === 'string' ? s : s.name) : undefined),
              experience: generatedCv?.experience,
              projects: generatedCv?.projects,
              education: generatedCv?.education,
              certifications: generatedCv?.certifications,
              achievements: generatedCv?.achievements,
              domains: generatedCv?.domains,
            }}
            onExportPdf={handleDownloadPdf}
            onSwitchToGenerator={() => setActiveTab('generate')}
          />
        </div>
      )}

      {/* Upload View */}
      {activeTab === 'upload' && (
        <div className="glass-panel rounded-3xl p-8 border border-white/10 max-w-xl mx-auto space-y-6">
          <form onSubmit={handleFileUpload} className="space-y-4">
            <div className="border-2 border-dashed border-white/15 hover:border-brand-500/50 rounded-2xl p-8 text-center transition-colors cursor-pointer bg-slate-950/40">
              <UploadCloud className="w-12 h-12 text-cyber-cyan mx-auto mb-3 animate-float" />
              <p className="text-sm font-bold text-white">Click or drag & drop your resume file</p>
              <p className="text-xs text-slate-400 mt-1">Supports PDF, DOCX, TXT up to 10 MB</p>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="mt-4 text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-brand-500 file:text-white hover:file:bg-brand-400 cursor-pointer"
              />
            </div>

            {file && (
              <div className="p-3 rounded-xl bg-slate-900 border border-white/10 flex items-center justify-between text-xs">
                <span className="font-semibold text-slate-200">{file.name}</span>
                <span className="text-slate-400">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || !file}
              className="w-full py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider bg-gradient-to-r from-brand-600 to-cyber-cyan disabled:opacity-40 text-white shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center space-x-2"
            >
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Parse & Evaluate Resume</span>
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* Paste Raw Text View */}
      {activeTab === 'text' && (
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 max-w-2xl mx-auto space-y-4">
          <label className="block text-xs font-semibold text-slate-300">
            Paste your resume contents or LinkedIn summary:
          </label>
          <textarea
            rows={8}
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            placeholder="Experienced Software Engineer with proficiency in React, TypeScript, Python, FastAPI, Docker, and PostgreSQL. Built scalable distributed systems..."
            className="w-full p-4 rounded-2xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none leading-relaxed resize-none"
          />

          <button
            onClick={handleTextAnalyze}
            disabled={loading || !resumeText.trim()}
            className="w-full py-3.5 rounded-xl font-bold text-xs uppercase tracking-wider bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 text-white shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center space-x-2"
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <span>Analyze Skills & ATS Match</span>}
          </button>
        </div>
      )}

      {/* AI Resume Generator */}
      {activeTab === 'generate' && (
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 max-w-2xl mx-auto space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Your Full Name</label>
              <input
                type="text"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Target Professional Role</label>
              <input
                type="text"
                value={targetChoice}
                onChange={(e) => setTargetChoice(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none"
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={handleGenerateCV}
                disabled={loading}
                className="flex-1 py-3.5 rounded-xl font-bold text-xs bg-brand-600 hover:bg-brand-500 text-white transition-all flex items-center justify-center space-x-2"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <span>Generate AI Optimized Resume</span>}
              </button>

              <button
                onClick={handleDownloadPdf}
                disabled={loading}
                className="px-5 py-3.5 rounded-xl font-bold text-xs bg-emerald-600 hover:bg-emerald-500 text-white transition-all flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Export PDF</span>
              </button>
            </div>
          </div>

          {generatedCv && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 rounded-2xl bg-slate-900/90 border border-brand-500/30 space-y-4 text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
                <div>
                  <span className="font-bold text-white text-sm">{generatedCv.name}</span>
                  <span className="text-cyber-cyan font-mono block text-xs">{generatedCv.target_role || targetChoice}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setActiveTab('preview')}
                  className="px-3.5 py-1.5 rounded-xl font-bold text-xs bg-gradient-to-r from-brand-600 to-cyber-cyan hover:from-brand-500 hover:to-cyber-cyan text-white shadow-md shadow-brand-500/25 transition-all flex items-center space-x-1.5 self-start sm:self-auto"
                >
                  <Sparkles className="w-3.5 h-3.5 text-cyan-200" />
                  <span>View in Real Resume Preview</span>
                </button>
              </div>
              <p className="text-slate-300 leading-relaxed">{generatedCv.summary}</p>
            </motion.div>
          )}
        </div>
      )}

      {/* Analysis Output Section */}
      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 space-y-6"
        >
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <h3 className="font-bold text-white text-lg flex items-center space-x-2">
              <FileCheck className="w-5 h-5 text-emerald-400" />
              <span>ATS Analysis & Extracted Skills</span>
            </h3>
            <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300">
              Verified
            </span>
          </div>

          {/* Skill Badges */}
          <div className="space-y-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Identified Competencies:
            </span>
            <div className="flex flex-wrap gap-2">
              {(
                analysisResult.skills ||
                analysisResult.analysis?.skills?.map((s: any) => (typeof s === 'string' ? s : s.name)) ||
                ['Python', 'React', 'TypeScript', 'FastAPI', 'SQL', 'Docker', 'System Design']
              ).map((skill: string, idx: number) => (
                <span
                  key={idx}
                  className="px-3 py-1 rounded-xl bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-semibold"
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Career recommendations */}
          {analysisResult.career_recommendations && analysisResult.career_recommendations.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-white/10">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Top Matched Career Paths:
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {analysisResult.career_recommendations.slice(0, 4).map((rec: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-1">
                    <div className="flex justify-between items-center">
                      <h4 className="font-bold text-white text-sm">{rec.role || rec.target_role}</h4>
                      <span className="text-xs font-bold text-emerald-400">
                        {Math.round(rec.match_percentage || rec.score || 85)}% Match
                      </span>
                    </div>
                    {rec.missing_skills?.length > 0 && (
                      <p className="text-[11px] text-orange-400">
                        Skill Gaps: {rec.missing_skills.join(', ')}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
};
