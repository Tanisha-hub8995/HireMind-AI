export interface User {
  id: number;
  name: string;
  email: string;
  role?: string;
  education?: string | null;
  experience?: string | null;
  career_goal?: string | null;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface QuestionCandidate {
  id?: number;
  question_text: string;
  topic?: string;
  difficulty?: string;
  section?: string;
  expected_keywords?: string[];
  sample_answer?: string;
  hint?: string;
}

export interface InterviewSession {
  interview_id: number;
  interview_type: string;
  status: string;
  target_role?: string;
  target_company?: string;
  current_difficulty: string;
  questions: QuestionCandidate[];
  created_at: string;
}

export interface RubricEvaluation {
  answer_id?: number;
  question_id?: number;
  score: number;
  correctness?: number;
  technical_accuracy?: number;
  reasoning_depth?: number;
  relevance?: number;
  completeness?: number;
  communication_clarity?: number;
  feedback?: string;
  keywords_detected?: string[];
  time_taken_seconds?: number;
  adapted_difficulty?: string;
  followup_question?: QuestionCandidate | null;
}

export interface InterviewReport {
  interview_id: number;
  status: string;
  overall_score: number;
  technical_score: number;
  problem_solving_score: number;
  communication_score: number;
  confidence_score: number;
  summary: string;
  overall_performance?: string;
  technical_knowledge?: string;
  problem_solving?: string;
  communication?: string;
  strong_areas: string[];
  weak_areas: string[];
  topics_needing_improvement: string[];
  question_wise_performance: any[];
  recommended_preparation_topics: string[];
  strengths: string[];
  improvements: string[];
  completed_at: string;
}

export interface DashboardData {
  candidate: {
    id: number;
    name: string;
    email: string;
    education?: string | null;
    career_goal?: string | null;
    has_resume: boolean;
    skills: string[];
  };
  level_info: {
    current_level: number;
    level_title: string;
    stars_earned: number;
    xp: number;
    next_level_xp: number;
  };
  badges: Array<{
    id: number;
    title: string;
    description: string;
    star_level: number;
    icon: string;
    unlocked: boolean;
  }>;
  certificates: Array<{
    id: number;
    title: string;
    issued_at: string;
    score: number;
    verification_code: string;
  }>;
  stats: {
    interviews_total: number;
    interviews_completed: number;
    assessments_total: number;
    average_interview_score: number;
    unread_recommendations: number;
    stars_earned: number;
    current_level: number;
    level_title: string;
  };
  recent_interviews: Array<{
    id: number;
    interview_type: string;
    status: string;
    score?: number | null;
    created_at: string;
  }>;
  recent_jobs: Array<{
    id: number;
    title: string;
    company_id: number;
    location: string;
    salary_range: string;
  }>;
}

export interface JobItem {
  id: number;
  title: string;
  company_name?: string;
  company_id: number;
  description: string;
  required_skills: string[] | string;
  location: string;
  salary_range: string;
  job_type: string;
  status: string;
  created_at: string;
}

export interface CompanyItem {
  id: number;
  name: string;
  industry: string;
  website: string;
  location: string;
  description: string;
  size: string;
  jobs?: JobItem[];
}

export interface CareerPathItem {
  id: number;
  target_role: string;
  current_level: string;
  target_level: string;
  skills_required: string[];
  skills_acquired: string[];
  estimated_time_months: number;
  created_at: string;
}

export interface AssessmentSectionInstruction {
  section: string;
  duration_minutes: number;
  number_of_questions: number;
  positive_mark: number;
  negative_mark: number;
  skipped_mark: number;
}
