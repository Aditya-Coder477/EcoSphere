import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserProfile, CarbonSummary } from '../types';

interface AppState {
  // Core data
  user: UserProfile | null;
  footprint: CarbonSummary | null;

  // UI preferences (persisted across refreshes)
  isDemoMode: boolean;
  theme: 'dark' | 'light';

  // Actions
  setUser: (user: UserProfile | null) => void;
  setFootprint: (footprint: CarbonSummary | null) => void;
  logout: () => void;
  toggleDemoMode: () => void;
  toggleTheme: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      user: null,
      footprint: null,
      isDemoMode: false,
      theme: 'dark',

      setUser: (user) => set({ user }),
      setFootprint: (footprint) => set({ footprint }),

      logout: () =>
        set({
          user: null,
          footprint: null,
          isDemoMode: false,
        }),

      toggleDemoMode: () =>
        set((state) => ({ isDemoMode: !state.isDemoMode })),

      toggleTheme: () => {
        const next = get().theme === 'dark' ? 'light' : 'dark';
        // Apply theme class to <html> immediately
        document.documentElement.classList.toggle('light-mode', next === 'light');
        set({ theme: next });
      },
    }),
    {
      name: 'ecosphere-app-state',
      // Only persist preferences and user identity, not live footprint data
      partialize: (state) => ({
        user: state.user,
        isDemoMode: state.isDemoMode,
        theme: state.theme,
      }),
      onRehydrateStorage: () => (state) => {
        // Reapply theme class when store rehydrates from localStorage
        if (state?.theme === 'light') {
          document.documentElement.classList.add('light-mode');
        }
      },
    }
  )
);
