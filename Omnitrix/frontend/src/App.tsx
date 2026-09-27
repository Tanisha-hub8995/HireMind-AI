import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/navigation/Navbar';
import { Footer } from './components/navigation/Footer';
import { DashboardView } from './components/dashboard/DashboardView';
import { InterviewRoom } from './components/interview/InterviewRoom';
import { AssessmentHub } from './components/assessment/AssessmentHub';
import { ResumeStudio } from './components/resume/ResumeStudio';
import { CareerJobsHub } from './components/career/CareerJobsHub';
import { BadgesCertificatesHub } from './components/gamification/BadgesCertificatesHub';
import { AuthModal } from './components/auth/AuthModal';
import { CyberBackground3D } from './components/three/CyberBackground3D';
import { HireMindAIAssistant } from './components/assistant/HireMindAIAssistant';

const MainLayout: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const { user } = useAuth();

  return (
    <div className="relative min-h-screen flex flex-col tech-grid text-slate-900 dark:text-slate-100 transition-colors">
      {/* 3D Background Galaxy */}
      <CyberBackground3D />

      {/* Navbar with Theme Toggle */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenAuth={() => setAuthModalOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 w-full relative z-10">
        {activeTab === 'dashboard' && <DashboardView setActiveTab={setActiveTab} />}
        {activeTab === 'interview' && <InterviewRoom />}
        {activeTab === 'assessment' && <AssessmentHub />}
        {activeTab === 'resume' && <ResumeStudio />}
        {activeTab === 'career' && <CareerJobsHub />}
        {activeTab === 'badges' && <BadgesCertificatesHub />}
      </main>

      {/* Floating AI Assistant on the Right Side of the Website */}
      <HireMindAIAssistant onNavigateTab={setActiveTab} />

      {/* Footer */}
      <Footer />

      {/* Authentication Modal */}
      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
    </div>
  );
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainLayout />
      </AuthProvider>
    </ThemeProvider>
  );
}
