import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { JobItem, CompanyItem, CareerPathItem } from '../../types';
import { 
  Briefcase, 
  Building2, 
  MapPin, 
  DollarSign, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight,
  ExternalLink,
  Layers,
  Sparkles
} from 'lucide-react';

export const CareerJobsHub: React.FC = () => {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [paths, setPaths] = useState<CareerPathItem[]>([]);
  const [activeFilter, setActiveFilter] = useState<'all' | 'jobs' | 'roadmaps'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getJobs().catch(() => []),
      api.getCompanies().catch(() => []),
      api.getCareerPaths().catch(() => []),
    ]).then(([jList, cList, pList]) => {
      setJobs(jList.length > 0 ? jList : [
        {
          id: 1,
          title: 'Senior Frontend & 3D Engineer',
          company_name: 'Google',
          company_id: 1,
          description: 'Build futuristic web applications with React, TypeScript, Three.js, and WebGL.',
          required_skills: ['React', 'TypeScript', 'Three.js', 'Tailwind CSS', 'WebGL'],
          location: 'Mountain View, CA / Remote',
          salary_range: '$190k - $250k',
          job_type: 'Full-time',
          status: 'active',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          title: 'Distributed Systems & AI Engineer',
          company_name: 'Microsoft',
          company_id: 2,
          description: 'Design robust microservices and local SLM inference pipelines using FastAPI and Python.',
          required_skills: ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'PyTorch'],
          location: 'Redmond, WA / Hybrid',
          salary_range: '$180k - $235k',
          job_type: 'Full-time',
          status: 'active',
          created_at: new Date().toISOString(),
        },
        {
          id: 3,
          title: 'Cloud Solutions Architect',
          company_name: 'Amazon AWS',
          company_id: 3,
          description: 'Architect multi-tenant cloud platforms, distributed databases, and high availability systems.',
          required_skills: ['AWS', 'Kubernetes', 'Go', 'System Design', 'Terraform'],
          location: 'Seattle, WA',
          salary_range: '$200k - $270k',
          job_type: 'Full-time',
          status: 'active',
          created_at: new Date().toISOString(),
        },
      ]);
      setCompanies(cList);
      setPaths(pList);
      setLoading(false);
    });
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold mb-3">
          <Briefcase className="w-3.5 h-3.5 text-cyber-cyan" />
          <span>Talent Matching & Career Trajectories</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Hiring Partners & <span className="bg-gradient-to-r from-cyber-cyan to-indigo-400 bg-clip-text text-transparent">Career Roadmaps</span>
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm mt-2">
          Discover verified roles from tier-1 technology leaders and navigate tailored roadmaps for your engineering seniority.
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex justify-center space-x-2">
        <button
          onClick={() => setActiveFilter('all')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'all'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 border border-white/5'
          }`}
        >
          All Opportunities
        </button>
        <button
          onClick={() => setActiveFilter('jobs')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'jobs'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 border border-white/5'
          }`}
        >
          Hiring Roles
        </button>
        <button
          onClick={() => setActiveFilter('roadmaps')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'roadmaps'
              ? 'bg-brand-600 text-white shadow-md shadow-brand-500/25'
              : 'bg-slate-900 text-slate-400 border border-white/5'
          }`}
        >
          Career Roadmaps
        </button>
      </div>

      {/* Career Roadmaps section */}
      {(activeFilter === 'all' || activeFilter === 'roadmaps') && (
        <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 space-y-6">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <TrendingUp className="w-5 h-5 text-cyber-cyan" />
            <span>Engineering Seniority Roadmap</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { level: 'Level 1: Associate', title: 'Junior Engineer', duration: '0 - 18 mos', skills: ['Core CS', 'Git', 'Clean Code', 'REST APIs'] },
              { level: 'Level 2: Mid-Level', title: 'Software Engineer II', duration: '1.5 - 3 yrs', skills: ['System Architecture', 'DB Optimization', 'Testing', 'Full-Stack'] },
              { level: 'Level 3: Senior', title: 'Senior Engineer', duration: '3 - 6 yrs', skills: ['High Scale Systems', 'Distributed Concurrency', 'Mentorship', 'Cloud Ops'] },
              { level: 'Level 4: Staff/Lead', title: 'Staff Engineer / Architect', duration: '6+ yrs', skills: ['Strategic Direction', 'Org Impact', 'Cross-System Design'] },
            ].map((step, idx) => (
              <div key={idx} className="p-5 rounded-2xl bg-slate-900/70 border border-white/5 space-y-3 relative overflow-hidden">
                <span className="text-[10px] font-bold text-brand-400 uppercase tracking-widest block">
                  {step.level}
                </span>
                <h3 className="font-bold text-white text-base">{step.title}</h3>
                <span className="text-xs text-slate-400 font-mono block">{step.duration}</span>
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {step.skills.map((s, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 text-slate-300">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Jobs Grid */}
      {(activeFilter === 'all' || activeFilter === 'jobs') && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold text-white flex items-center space-x-2 px-1">
            <Building2 className="w-5 h-5 text-brand-400" />
            <span>Active Roles from Top Tech Employers</span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {jobs.map((job) => (
              <div
                key={job.id}
                className="glass-panel rounded-3xl p-6 border border-white/10 hover:border-brand-500/40 transition-all flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-brand-500/15 text-brand-300 border border-brand-500/25">
                      {job.company_name || 'Tech Company'}
                    </span>
                    <span className="text-xs font-semibold text-emerald-400">
                      {job.job_type}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-cyber-cyan transition-colors">
                    {job.title}
                  </h3>

                  <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">
                    {job.description}
                  </p>

                  <div className="flex items-center space-x-4 text-xs text-slate-400">
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job.location}</span>
                    </div>
                    <div className="flex items-center space-x-1 text-emerald-400 font-semibold">
                      <DollarSign className="w-3.5 h-3.5" />
                      <span>{job.salary_range}</span>
                    </div>
                  </div>

                  {/* Skills required */}
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {(Array.isArray(job.required_skills)
                      ? job.required_skills
                      : String(job.required_skills).split(',')
                    ).map((s, i) => (
                      <span
                        key={i}
                        className="text-[10px] px-2 py-0.5 rounded-md bg-slate-900 border border-white/5 text-slate-300"
                      >
                        {String(s).trim()}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => alert(`Applied to ${job.title} at ${job.company_name || 'Tech Company'}! Your ATS profile was shared.`)}
                  className="w-full mt-2 py-2.5 rounded-xl font-bold text-xs bg-slate-800 hover:bg-brand-600 text-white transition-colors flex items-center justify-center space-x-2"
                >
                  <span>Quick Apply with Profile</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
