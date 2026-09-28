import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { 
  Menu, 
  X, 
  LogOut, 
  BrainCircuit, 
  ChevronDown,
  Sun,
  Moon
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onOpenAuth }) => {
  const { user, logout, demoLogin, loading } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [moreDropdownOpen, setMoreDropdownOpen] = useState(false);

  // Clean, focused primary navigation without clutter
  const primaryNav = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'interview', label: 'Mock Interview' },
    { id: 'assessment', label: 'Assessments' },
    { id: 'resume', label: 'Resume ATS' },
    { id: 'career', label: 'Jobs' },
    { id: 'pricing', label: 'Pricing' },
  ];

  const secondaryNav = [
    { id: 'badges', label: 'Credentials & Badges' },
  ];

  const handleNavClick = (id: string) => {
    if (id === 'pricing') {
      setActiveTab('dashboard');
      setTimeout(() => {
        const el = document.getElementById('pricing');
        if (el) {
          el.scrollIntoView({ behavior: 'smooth' });
        }
      }, 100);
    } else {
      setActiveTab(id);
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[#090D16]/85 backdrop-blur-md border-b border-white/[0.06] transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Minimalist Logo */}
          <div 
            onClick={() => setActiveTab('dashboard')}
            className="flex items-center space-x-2.5 cursor-pointer group select-none"
          >
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-md shadow-indigo-600/20 group-hover:bg-indigo-500 transition-colors">
              <BrainCircuit className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-base tracking-tight text-slate-900 dark:text-white">
              RAAHSETU<span className="text-cyan-500 dark:text-cyan-400 font-semibold ml-0.5">AI</span>
            </span>
          </div>

          {/* Clean, Spacious Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-1 lg:space-x-2">
            {primaryNav.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'text-indigo-600 dark:text-white bg-indigo-50 dark:bg-white/[0.08] border border-indigo-200/60 dark:border-transparent shadow-xs font-semibold'
                      : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.03]'
                  }`}
                >
                  {item.label}
                </button>
              );
            })}

            {/* Subtle 'More' dropdown for secondary items to avoid crowding */}
            <div className="relative">
              <button
                onClick={() => setMoreDropdownOpen(!moreDropdownOpen)}
                onBlur={() => setTimeout(() => setMoreDropdownOpen(false), 200)}
                className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  activeTab === 'badges'
                    ? 'text-indigo-600 dark:text-white bg-indigo-50 dark:bg-white/[0.08] font-semibold'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-white/[0.03]'
                }`}
              >
                <span>More</span>
                <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${moreDropdownOpen ? 'rotate-180' : ''}`} />
              </button>

              {moreDropdownOpen && (
                <div className="absolute right-0 mt-1.5 w-48 rounded-xl bg-white dark:bg-[#0D121F] border border-slate-200 dark:border-white/[0.08] shadow-2xl py-1.5 z-50 backdrop-blur-xl">
                  {secondaryNav.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => {
                        setActiveTab(item.id);
                        setMoreDropdownOpen(false);
                      }}
                      className="w-full text-left px-3.5 py-2 text-xs font-medium text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-white/[0.06] transition-colors"
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </nav>

          {/* Right Action: Clean, minimal authentication status & Theme toggle */}
          <div className="hidden md:flex items-center space-x-2.5">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/[0.06] transition-colors"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400 hover:rotate-45 transition-transform duration-300" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-600 hover:-rotate-12 transition-transform duration-300" />
              )}
            </button>

            {user ? (
              <div className="flex items-center space-x-3 pl-1">
                <div 
                  onClick={() => setActiveTab('badges')}
                  className="cursor-pointer flex items-center space-x-2 text-xs text-slate-300 hover:text-white transition-colors"
                >
                  <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 flex items-center justify-center text-white text-xs font-bold">
                    {user.name ? user.name[0].toUpperCase() : 'U'}
                  </div>
                  <span className="font-medium text-slate-200">{user.name}</span>
                </div>

                <button
                  onClick={logout}
                  title="Sign out"
                  className="p-1.5 rounded-md text-slate-500 hover:text-slate-300 hover:bg-white/[0.04] transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={demoLogin}
                  disabled={loading}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/[0.05] transition-colors"
                >
                  Demo
                </button>
                <button
                  onClick={onOpenAuth}
                  className="px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white text-slate-900 hover:bg-slate-100 transition-all shadow-sm"
                >
                  Sign In
                </button>
              </div>
            )}
          </div>

          {/* Mobile hamburger & theme toggle */}
          <div className="flex md:hidden items-center space-x-1.5">
            <button
              onClick={toggleTheme}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-600" />
              )}
            </button>
            {!user && (
              <button
                onClick={demoLogin}
                className="px-2.5 py-1 text-xs font-medium rounded text-slate-300 hover:text-white bg-white/[0.05]"
              >
                Demo
              </button>
            )}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-white/[0.06] bg-[#090D16] px-4 pt-2 pb-4 space-y-1">
          {[...primaryNav, ...secondaryNav].map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  handleNavClick(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium ${
                  isActive ? 'bg-white/[0.08] text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                {item.label}
              </button>
            );
          })}

          <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between">
            {user ? (
              <div className="flex items-center justify-between w-full">
                <span className="text-xs text-slate-300">{user.name}</span>
                <button
                  onClick={logout}
                  className="text-xs text-slate-400 hover:text-red-400 flex items-center space-x-1"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex space-x-2 w-full pt-1">
                <button
                  onClick={() => {
                    demoLogin();
                    setMobileMenuOpen(false);
                  }}
                  className="flex-1 py-2 text-xs font-medium rounded-lg bg-white/[0.05] text-slate-300"
                >
                  Quick Demo
                </button>
                <button
                  onClick={() => {
                    onOpenAuth();
                    setMobileMenuOpen(false);
                  }}
                  className="flex-1 py-2 text-xs font-semibold rounded-lg bg-white text-slate-900"
                >
                  Sign In
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
