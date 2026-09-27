import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../context/AuthContext';
import { X, Mail, Lock, User, ArrowRight, Sparkles, CheckCircle2 } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const { login, signup, demoLogin } = useAuth();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isSignUp) {
        if (!name.trim()) throw new Error('Please enter your full name');
        await signup(name, email, password, role);
      } else {
        await login(email, password);
      }
      onClose();
    } catch (err: any) {
      let msg = 'Authentication failed. Please check your credentials.';
      if (typeof err === 'string') {
        msg = err;
      } else if (err?.message) {
        msg = typeof err.message === 'string' ? err.message : JSON.stringify(err.message);
      }
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setError(null);
    setLoading(true);
    try {
      await demoLogin();
      onClose();
    } catch (err: any) {
      setError(err.message || 'Demo login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-md rounded-2xl glass-panel p-6 sm:p-8 border border-white/15 shadow-2xl shadow-brand-500/10 overflow-hidden"
        >
          {/* Top glowing edge */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-brand-500 via-cyber-cyan to-indigo-500" />

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Header */}
          <div className="mb-4">
            <h2 className="text-2xl font-black tracking-tight text-white flex items-center space-x-2">
              <span>{isSignUp ? 'Create HireMind AI Account' : 'Welcome to HireMind AI'}</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {isSignUp
                ? 'Create your candidate profile to practice with 3D AI and land top tier roles.'
                : 'Sign in to access your mock interview rooms, assessments and progress.'}
            </p>
          </div>

          {/* Segmented Mode Selector: Sign In vs Create Account */}
          <div className="flex p-1 mb-4 rounded-xl bg-slate-900/90 border border-white/10">
            <button
              type="button"
              onClick={() => {
                setIsSignUp(false);
                setError(null);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                !isSignUp
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => {
                setIsSignUp(true);
                setError(null);
              }}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition-all ${
                isSignUp
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Create Account (New User)
            </button>
          </div>

          {/* Seamless Database Registration Notice */}
          {!isSignUp && (
            <p className="text-[11px] text-cyan-300/90 bg-cyan-950/30 p-2.5 rounded-xl border border-cyan-500/20 mb-4 flex items-center space-x-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
              <span>Signing in with a new email automatically registers your profile in the database.</span>
            </p>
          )}

          {/* Demo account quick button */}
          <div className="mb-5 p-3 rounded-xl bg-gradient-to-r from-brand-950/80 to-indigo-950/80 border border-brand-500/30 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <Sparkles className="w-4 h-4 text-cyber-cyan animate-pulse" />
              <div>
                <p className="text-xs font-semibold text-slate-200">Instant Demo Access</p>
                <p className="text-[11px] text-slate-400">Pre-loaded candidate account with sample data</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleDemo}
              disabled={loading}
              className="px-3 py-1.5 rounded-lg text-xs font-bold bg-brand-500 hover:bg-brand-400 text-white transition-all shadow-md shadow-brand-500/30"
            >
              One-Click
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-xs text-red-300">
              {error}
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignUp && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Maya Patel"
                    className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none transition-colors"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="candidate@example.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none transition-colors"
                />
              </div>
            </div>

            {isSignUp && (
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Account Role</label>
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-xl bg-slate-900/80 border border-white/10 text-white text-sm focus:border-brand-500 focus:outline-none transition-colors"
                >
                  <option value="user">Candidate / Job Seeker</option>
                  <option value="admin">Recruiter / Admin</option>
                </select>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-brand-600 via-indigo-600 to-cyber-blue hover:from-brand-500 hover:to-cyber-cyan text-white shadow-lg shadow-brand-500/25 transition-all flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>{isSignUp ? 'Create My Account' : 'Sign In Now'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Sign Up / Sign In */}
          <div className="mt-5 text-center">
            <button
              type="button"
              onClick={() => {
                setIsSignUp(!isSignUp);
                setError(null);
              }}
              className="text-xs text-slate-400 hover:text-cyber-cyan transition-colors"
            >
              {isSignUp
                ? 'Already have an account? Sign in here'
                : "Don't have an account yet? Register for free"}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
