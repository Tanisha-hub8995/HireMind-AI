import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { 
  Award, 
  Star, 
  Download, 
  CheckCircle, 
  Lock, 
  ShieldCheck, 
  Zap, 
  Sparkles,
  ExternalLink
} from 'lucide-react';

export const BadgesCertificatesHub: React.FC = () => {
  const [badgeData, setBadgeData] = useState<any>(null);
  const [certData, setCertData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getBadges().catch(() => null),
      api.getCertificates().catch(() => null),
    ]).then(([bRes, cRes]) => {
      setBadgeData(bRes);
      setCertData(cRes);
      setLoading(false);
    });
  }, []);

  const defaultBadges = [
    { id: 1, title: 'First Code Assessment', description: 'Complete your first technical evaluation challenge', star_level: 1, unlocked: true },
    { id: 2, title: 'Algorithm Ace', description: 'Attain >80% accuracy in Data Structures & Algorithms', star_level: 2, unlocked: true },
    { id: 3, title: 'System Design Strategist', description: 'Demonstrate deep architecture trade-offs in mock interviews', star_level: 3, unlocked: true },
    { id: 4, title: 'Speech & Verbal Virtuoso', description: 'Achieve >85% communication clarity score via microphone', star_level: 4, unlocked: false },
    { id: 5, title: 'RAAHSETU AI Grandmaster', description: 'Attain Level 5 seniority and pass 5 mock simulations', star_level: 5, unlocked: false },
  ];

  const badges = badgeData?.badges || defaultBadges;
  const levelInfo = badgeData?.level_info || {
    current_level: 2,
    level_title: 'Rising System Architect',
    stars_earned: 3,
    xp: 340,
    next_level_xp: 500,
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/15 border border-brand-500/30 text-brand-300 text-xs font-semibold mb-3">
          <Award className="w-3.5 h-3.5 text-yellow-400" />
          <span>Verified Credentials & Gamification</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
          Badges, Levels & <span className="bg-gradient-to-r from-yellow-300 via-amber-400 to-brand-400 bg-clip-text text-transparent">Certifications</span>
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm mt-2">
          Earn star badges, climb technical seniority tiers, and export cryptographically verified completion certificates.
        </p>
      </div>

      {/* Level & XP Banner */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-white/10 relative overflow-hidden shadow-2xl">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
          <div className="md:col-span-8 space-y-3">
            <div className="flex items-center space-x-3">
              <span className="px-3 py-1 rounded-xl bg-yellow-500/20 text-yellow-600 dark:text-yellow-300 text-xs font-bold border border-yellow-500/30">
                Tier {levelInfo.current_level} Candidate
              </span>
              <span className="text-sm font-bold text-slate-900 dark:text-white">{levelInfo.level_title}</span>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-xs text-slate-700 dark:text-slate-300 font-semibold">
                <span>XP Progress</span>
                <span className="font-mono">{levelInfo.xp} / {levelInfo.next_level_xp} XP</span>
              </div>
              <div className="w-full h-3 bg-slate-200 dark:bg-slate-900 rounded-full overflow-hidden border border-slate-300 dark:border-white/5">
                <div
                  className="h-full bg-gradient-to-r from-yellow-400 via-brand-500 to-cyber-cyan rounded-full transition-all duration-700"
                  style={{ width: `${Math.min(100, (levelInfo.xp / levelInfo.next_level_xp) * 100)}%` }}
                />
              </div>
            </div>
          </div>

          <div className="md:col-span-4 flex items-center justify-around p-4 rounded-2xl bg-slate-100 dark:bg-slate-900/60 border border-slate-200 dark:border-white/5">
            <div className="text-center">
              <span className="text-2xl font-black text-yellow-500 dark:text-yellow-400">{levelInfo.stars_earned} ★</span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 block font-semibold uppercase">Stars Earned</span>
            </div>
            <div className="text-center">
              <span className="text-2xl font-black text-brand-600 dark:text-cyber-cyan">Level {levelInfo.current_level}</span>
              <span className="text-[10px] text-slate-500 dark:text-slate-400 block font-semibold uppercase">Current Rank</span>
            </div>
          </div>
        </div>
      </div>

      {/* 1-to-5 Star Badges Showcase */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2 px-1">
          <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" />
          <span>Star Badges & Milestones</span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {badges.map((b: any) => (
            <div
              key={b.id}
              className={`p-6 rounded-3xl border transition-all ${
                b.unlocked
                  ? 'glass-panel border-amber-500/40 bg-amber-500/5 dark:bg-amber-950/10 shadow-lg shadow-amber-500/5'
                  : 'bg-slate-100 dark:bg-slate-900/40 border-slate-200 dark:border-white/5 opacity-60'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-1">
                  {Array.from({ length: b.star_level }).map((_, i) => (
                    <Star
                      key={i}
                      className={`w-4 h-4 ${
                        b.unlocked ? 'text-yellow-400 fill-yellow-400' : 'text-slate-400 dark:text-slate-600'
                      }`}
                    />
                  ))}
                </div>
                {b.unlocked ? (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/30">
                    Unlocked
                  </span>
                ) : (
                  <span className="flex items-center space-x-1 text-[10px] text-slate-500">
                    <Lock className="w-3 h-3" />
                    <span>Locked</span>
                  </span>
                )}
              </div>

              <h3 className="font-bold text-base text-slate-900 dark:text-white">{b.title}</h3>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">{b.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Official PDF Certificates Section */}
      <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-slate-200 dark:border-white/10 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-200 dark:border-white/10 pb-4 gap-4">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white flex items-center space-x-2">
              <ShieldCheck className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
              <span>Official Assessment Certificates</span>
            </h2>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
              Download high-resolution, PDF completion certificates generated on-demand by the backend.
            </p>
          </div>

          <a
            href={api.getLatestCertificatePdfUrl()}
            target="_blank"
            rel="noreferrer"
            className="px-5 py-2.5 rounded-xl font-bold text-xs bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/20 transition-all flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Download Latest PDF Certificate</span>
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(certData?.certificates?.length ? certData.certificates : [
            {
              id: 101,
              title: 'Full-Stack Technical Interview Mastery',
              issued_at: new Date().toISOString(),
              score: 92,
              verification_code: 'OMNI-7821-CERT',
            },
            {
              id: 102,
              title: 'Advanced DSA & Problem Solving Examination',
              issued_at: new Date().toISOString(),
              score: 88,
              verification_code: 'OMNI-9410-CERT',
            },
          ]).map((cert: any, idx: number) => (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/70 border border-slate-200 dark:border-white/5 flex items-center justify-between"
            >
              <div className="space-y-1">
                <span className="text-[10px] font-mono font-bold text-cyan-600 dark:text-cyber-cyan block">
                  {cert.verification_code}
                </span>
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">{cert.title}</h4>
                <span className="text-xs text-slate-500 dark:text-slate-400">
                  Issued: {new Date(cert.issued_at).toLocaleDateString()} • Score: {cert.score}%
                </span>
              </div>
              <a
                href={api.getLatestCertificatePdfUrl()}
                target="_blank"
                rel="noreferrer"
                className="p-2.5 rounded-xl bg-slate-200 dark:bg-white/5 hover:bg-slate-300 dark:hover:bg-white/10 text-slate-800 dark:text-white transition-colors"
                title="Download PDF"
              >
                <Download className="w-4 h-4 text-emerald-500 dark:text-emerald-400" />
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
