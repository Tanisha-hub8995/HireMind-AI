import React from 'react';
import { Database, ShieldCheck, Terminal, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="mt-auto border-t border-white/10 glass-panel py-6 px-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between text-xs text-slate-400 gap-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-mono font-medium">RAAHSETU Engine v4.2 • Systems Operational</span>
          </div>
          <span className="hidden sm:inline text-slate-600">|</span>
          <div className="flex items-center space-x-1.5 text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>Qwen SLM Rubrics & Embeddings</span>
          </div>
        </div>

        <div className="flex items-center space-x-6">
          <span className="flex items-center space-x-1 text-slate-500">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>PostgreSQL Neon Cloud</span>
          </span>
          <span className="flex items-center space-x-1 text-slate-500">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>JWT Bearer Security</span>
          </span>
          <span className="flex items-center space-x-1 text-slate-500">
            <Terminal className="w-3.5 h-3.5" />
            <span>React Three Fiber 3D</span>
          </span>
        </div>
      </div>
    </footer>
  );
};
