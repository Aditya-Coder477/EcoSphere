// Re-export all mocks from a single entry point
export { mockUserProfile } from './mockUser';
export { mockCarbonSummary } from './mockFootprint';
export { mockBreakdownData } from './mockBreakdown';
export { mockRecommendations } from './mockRecommendations';
export {
  mockJourneyMonths,
  mockMilestones,
  mockAchievements,
  mockCumulativeSavings,
  mockStreakMonths,
} from './mockJourney';
export {
  getWelcomeMessage,
  mockFallbackAnswers,
  getSimulatedAnswer,
} from './mockAssistant';

/**
 * Returns `realData` when it is non-null, non-empty, and the response succeeded.
 * Falls back to `mockData` otherwise.
 *
 * Usage (in services or hooks):
 *   const footprint = getDataOrFallback(apiResult?.data, mockCarbonSummary);
 */
export function getDataOrFallback<T>(
  realData: T | null | undefined,
  mockData: T
): { data: T; isDemo: boolean } {
  const isEmpty =
    realData === null ||
    realData === undefined ||
    (Array.isArray(realData) && (realData as unknown[]).length === 0) ||
    (typeof realData === 'object' &&
      !Array.isArray(realData) &&
      Object.keys(realData as object).length === 0);

  if (isEmpty) {
    return { data: mockData, isDemo: true };
  }
  return { data: realData, isDemo: false };
}
