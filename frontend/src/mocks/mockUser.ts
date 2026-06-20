import { UserProfile } from '../types';

export const mockUserProfile: UserProfile = {
  id: 'mock_user_aditya',
  name: 'Aditya Raj',
  email: 'aditya.raj@example.com',
  occupation: 'Software Engineer',
  preferences: {
    country: 'IND',
    household_size: 2,
    diet: 'average',
    commute_mode: 'car',
    budget_level: 'medium',
    electricity_source: 'grid',
    electricity_kwh_per_year: 4200,
  },
};
