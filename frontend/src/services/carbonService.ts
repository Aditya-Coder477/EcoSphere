import { apiClient, ApiResponse } from './api';
import { ENDPOINTS } from '../constants/api';
import { UserProfile, CarbonSummary, RecommendationItem } from '../types';

export const carbonService = {
  createUser: (profile: Partial<UserProfile>): Promise<ApiResponse<UserProfile>> => 
    apiClient.post(ENDPOINTS.USERS, profile),
    
  calculateCarbon: (userId: string, data: any): Promise<ApiResponse<CarbonSummary>> => 
    apiClient.post(ENDPOINTS.CARBON_CALCULATE, { user_id: userId, input_data: data }),
    
  getRecommendations: (userId: string): Promise<ApiResponse<{ recommendations: RecommendationItem[] }>> => 
    apiClient.post(ENDPOINTS.RECOMMENDATIONS, { user_id: userId })
};
