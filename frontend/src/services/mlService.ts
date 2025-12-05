/**
 * ML Service - API calls for ML-powered scheduling features
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with auth
const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface MLScheduleRequest {
  start_date: string;
  end_date: string;
}

export interface MLPrediction {
  assignment_id: number;
  assignment_title: string;
  predicted_hours: number;
  confidence: number;
  confidence_interval: [number, number];
  feature_importance: Record<string, any>;
}

export interface MLScheduleResponse {
  study_sessions: any[];
  predictions: MLPrediction[];
  total_hours_scheduled: number;
  ml_insights: {
    avg_confidence: number;
    assignments_analyzed: number;
    model_version: string;
  };
}

export interface CourseInsight {
  source: string;
  difficulty_score: number;
  avg_hours_per_week: number;
  last_updated: string;
}

export interface ProfessorRating {
  professor_name: string;
  overall_rating: number;
  difficulty_rating: number;
  would_take_again: number;
  source: string;
}

export interface CourseInsightsResponse {
  course_code: string;
  course_insights: CourseInsight[];
  professor_ratings: ProfessorRating[];
  avg_difficulty: number | null;
  avg_hours_per_week: number | null;
}

export interface StudySessionFeedback {
  session_id: number;
  actual_hours: number;
  productivity: number;
  difficulty: number;
  was_sufficient: boolean;
  comments?: string;
}

export const mlService = {
  /**
   * Generate ML-powered study schedule
   */
  generateMLSchedule: async (request: MLScheduleRequest): Promise<MLScheduleResponse> => {
    const response = await api.post('/schedules/generate-ml', request);
    return response.data;
  },

  /**
   * Get course insights from web scraping
   */
  getCourseInsights: async (courseCode: string): Promise<CourseInsightsResponse> => {
    const response = await api.get(`/schedules/insights/${encodeURIComponent(courseCode)}`);
    return response.data;
  },

  /**
   * Submit feedback on a study session
   */
  submitFeedback: async (feedback: StudySessionFeedback): Promise<{ message: string; id: number }> => {
    const response = await api.post('/schedules/feedback', {
      session_id: feedback.session_id,
      actual_hours: feedback.actual_hours,
      productivity: feedback.productivity,
      difficulty: feedback.difficulty,
      was_sufficient: feedback.was_sufficient,
      comments: feedback.comments || ''
    });
    return response.data;
  }
};

export default mlService;
