export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 15000,
} as const;

export const ENDPOINTS = {
  HEALTH: '/health',
  USERS: '/users',
  CARBON_CALCULATE: '/carbon/calculate',
  RECOMMENDATIONS: '/recommendations',
  LLM_EXPLAIN: '/llm/explain',
  RAG_QUERY: '/rag/query',
  METADATA: '/metadata',
} as const;
