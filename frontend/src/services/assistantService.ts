import { apiClient, ApiResponse } from './api';
import { ENDPOINTS } from '../constants/api';

interface ExplanationResponse {
  explanation_text: string;
  model_used: string;
  sources?: string[];
}

interface AssistantResponse {
  answer: string;
  sources: string[];
  confidence: 'low' | 'medium' | 'high';
  fallback_mode: 'none' | 'demo' | 'weak_rag' | 'missing_data' | 'clarification';
  response_source: 'rag' | 'rag_profile' | 'profile' | 'recommendations' | 'demo' | 'clarification';
  suggested_follow_up_questions: string[];
  used_demo_data: boolean;
  grounded_facts: string[];
}

export const assistantService = {
  explainFootprint: (userId: string, data: any): Promise<ApiResponse<ExplanationResponse>> => 
    apiClient.post(ENDPOINTS.LLM_EXPLAIN, {
      user_id: userId,
      context_type: 'footprint',
      context_data: data
    }),
    
  explainRecommendation: (userId: string, data: any): Promise<ApiResponse<ExplanationResponse>> => 
    apiClient.post(ENDPOINTS.LLM_EXPLAIN, {
      user_id: userId,
      context_type: 'recommendation',
      context_data: data
    }),
    
  queryAssistant: (userId: string, query: string): Promise<ApiResponse<AssistantResponse>> => 
    apiClient.post(ENDPOINTS.RAG_QUERY, {
      user_id: userId,
      query
    })
};
