import {
  User,
  AuthResponse,
  InterviewSession,
  RubricEvaluation,
  InterviewReport,
  DashboardData,
  JobItem,
  CompanyItem,
  CareerPathItem,
  AssessmentSectionInstruction
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getHeaders(isFormData = false): HeadersInit {
  const token = localStorage.getItem('raahsetu_token') || localStorage.getItem('hiremind_token') || localStorage.getItem('omnitrix_token');
  const headers: Record<string, string> = {};
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorDetail = 'An error occurred';
    try {
      const errJson = await res.json();
      if (Array.isArray(errJson.detail)) {
        errorDetail = errJson.detail
          .map((item: any) => item.msg || item.message || JSON.stringify(item))
          .join(', ');
      } else if (typeof errJson.detail === 'object' && errJson.detail !== null) {
        errorDetail = JSON.stringify(errJson.detail);
      } else if (errJson.detail) {
        errorDetail = String(errJson.detail);
      } else if (errJson.message) {
        errorDetail = String(errJson.message);
      } else {
        errorDetail = JSON.stringify(errJson);
      }
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Auth endpoints
  async signup(data: { name: string; email: string; password: string; role?: string }): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return handleResponse<User>(res);
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });
    const data = await handleResponse<AuthResponse>(res);
    localStorage.setItem('raahsetu_token', data.access_token);
    localStorage.setItem('hiremind_token', data.access_token);
    localStorage.setItem('omnitrix_token', data.access_token);
    return data;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    return handleResponse<User>(res);
  },

  // Onboarding
  async getOnboarding(): Promise<{ education?: string; experience?: string; career_goal?: string }> {
    const res = await fetch(`${API_BASE}/onboarding/`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async saveOnboarding(data: { education: string; experience: string; career_goal: string }): Promise<any> {
    const res = await fetch(`${API_BASE}/onboarding/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  // Dashboard
  async getDashboard(): Promise<DashboardData> {
    const res = await fetch(`${API_BASE}/dashboard/`, {
      headers: getHeaders(),
    });
    return handleResponse<DashboardData>(res);
  },

  // Interviews
  async startInterview(params: {
    role?: string;
    difficulty?: string;
    interview_type?: string;
    target_company?: string;
    num_questions?: number;
    topics?: string[];
    resume_id?: number;
  }): Promise<InterviewSession> {
    const res = await fetch(`${API_BASE}/interviews/start`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(params),
    });
    return handleResponse<InterviewSession>(res);
  },

  async submitAnswer(
    interviewId: number,
    data: {
      question_id?: number;
      question_text?: string;
      answer_text: string;
      time_taken_seconds?: number;
      generate_followup?: boolean;
    }
  ): Promise<RubricEvaluation> {
    const res = await fetch(`${API_BASE}/interviews/${interviewId}/answer`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse<RubricEvaluation>(res);
  },

  async submitAudioAnswer(
    interviewId: number,
    audioBlob: Blob,
    questionId?: number,
    questionText?: string,
    timeTakenSeconds = 60,
    generateFollowup = false
  ): Promise<RubricEvaluation> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'response.wav');
    if (questionId) formData.append('question_id', String(questionId));
    if (questionText) formData.append('question_text', questionText);
    formData.append('time_taken_seconds', String(timeTakenSeconds));
    formData.append('generate_followup', String(generateFollowup));

    const res = await fetch(`${API_BASE}/interviews/${interviewId}/answer-audio`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse<RubricEvaluation>(res);
  },

  async completeInterview(interviewId: number): Promise<InterviewReport> {
    const res = await fetch(`${API_BASE}/interviews/${interviewId}/complete`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<InterviewReport>(res);
  },

  async getInterviewHistory(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/interviews/history`, {
      headers: getHeaders(),
    });
    return handleResponse<any[]>(res);
  },

  async getInterviewDetail(interviewId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/interviews/${interviewId}`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  getTTSAudioUrl(text: string): string {
    return `${API_BASE}/interviews/tts?text=${encodeURIComponent(text)}`;
  },

  getQuestionAudioUrl(questionId: number): string {
    return `${API_BASE}/interviews/questions/${questionId}/audio`;
  },

  async transcribeAudio(audioBlob: Blob): Promise<{ status: string; transcript: string; length_bytes: number }> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.webm');
    const res = await fetch(`${API_BASE}/interviews/transcribe`, {
      method: 'POST',
      body: formData,
    });
    return handleResponse(res);
  },

  // Assessments
  async getAssessmentInstructions(): Promise<{ total_duration_minutes: number; sections: AssessmentSectionInstruction[] }> {
    const res = await fetch(`${API_BASE}/assessments/instructions`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  async startAssessment(userId: number, mode: string = 'FULL'): Promise<any> {
    const res = await fetch(`${API_BASE}/assessments/start?user_id=${userId}&assessment_mode=${mode}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getAssessmentQuestion(assessmentId: number, userId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/questions?user_id=${userId}`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async answerAssessmentQuestion(
    assessmentId: number,
    questionId: number,
    userId: number,
    selectedOption: string,
    timeSpentSeconds = 15
  ): Promise<any> {
    const res = await fetch(
      `${API_BASE}/assessments/${assessmentId}/questions/${questionId}/answer?user_id=${userId}&selected_option=${encodeURIComponent(selectedOption)}&time_spent_seconds=${timeSpentSeconds}`,
      {
        method: 'PUT',
        headers: getHeaders(),
      }
    );
    return handleResponse<any>(res);
  },

  async submitAssessmentSection(assessmentId: number, userId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/submit-section?user_id=${userId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async finalizeAssessment(assessmentId: number, userId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/finalize?user_id=${userId}`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getAssessmentResult(assessmentId: number, userId: number): Promise<any> {
    const res = await fetch(`${API_BASE}/assessments/${assessmentId}/result?user_id=${userId}`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  // Resume
  async uploadResume(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/resume/upload`, {
      method: 'POST',
      headers: getHeaders(true),
      body: formData,
    });
    return handleResponse<any>(res);
  },

  async listResumes(): Promise<any[]> {
    const res = await fetch(`${API_BASE}/resume/`, {
      headers: getHeaders(),
    });
    return handleResponse<any[]>(res);
  },

  async analyzeResumeText(text: string): Promise<any> {
    const res = await fetch(`${API_BASE}/resume/analyze`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ text }),
    });
    return handleResponse<any>(res);
  },

  async generateResume(name: string, choice: string): Promise<any> {
    const res = await fetch(`${API_BASE}/resume/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, choice }),
    });
    return handleResponse<any>(res);
  },

  async downloadGeneratedResumePdf(name: string, choice: string): Promise<Blob> {
    const res = await fetch(`${API_BASE}/resume/generate/pdf`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, choice }),
    });
    if (!res.ok) throw new Error('Failed to download CV PDF');
    return res.blob();
  },

  // Jobs & Companies
  async getJobs(): Promise<JobItem[]> {
    const res = await fetch(`${API_BASE}/jobs/`, {
      headers: getHeaders(),
    });
    return handleResponse<JobItem[]>(res);
  },

  async getJobRecommendations(): Promise<any> {
    const res = await fetch(`${API_BASE}/jobs/recommendations`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getCompanies(): Promise<CompanyItem[]> {
    const res = await fetch(`${API_BASE}/companies/`, {
      headers: getHeaders(),
    });
    return handleResponse<CompanyItem[]>(res);
  },

  // Career
  async getCareerRecommendations(): Promise<any> {
    const res = await fetch(`${API_BASE}/career/recommendations`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getCareerPaths(): Promise<CareerPathItem[]> {
    const res = await fetch(`${API_BASE}/career/paths`, {
      headers: getHeaders(),
    });
    return handleResponse<CareerPathItem[]>(res);
  },

  // Gamification (Badges & Certificates)
  async getBadges(): Promise<any> {
    const res = await fetch(`${API_BASE}/badges/`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  async getCertificates(): Promise<any> {
    const res = await fetch(`${API_BASE}/certificates/`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  getLatestCertificatePdfUrl(): string {
    return `${API_BASE}/certificates/download/latest`;
  },

  // Progress
  async getProgress(): Promise<any> {
    const res = await fetch(`${API_BASE}/progress/`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },

  // Recommendations
  async getRecommendations(): Promise<any> {
    const res = await fetch(`${API_BASE}/recommendations/`, {
      headers: getHeaders(),
    });
    return handleResponse<any>(res);
  },
};
