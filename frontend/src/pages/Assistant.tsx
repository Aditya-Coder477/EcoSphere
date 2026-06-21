import React from 'react';
import { useNavigate } from 'react-router-dom';
import { AssistantChat } from '../components/assistant/AssistantChat';
import { useAppStore } from '../store/useAppStore';
import { mockUserProfile } from '../mocks';
import { Button } from '../components/ui/Button';
import { ROUTES } from '../constants/routes';

const Assistant = () => {
  const navigate = useNavigate();
  const { user, isDemoMode } = useAppStore();

  if (!user && !isDemoMode) {
    return (
      <div className="flex flex-col items-center justify-center h-[60vh] gap-4" role="alert">
        <h2 className="text-2xl font-bold">Onboarding Required</h2>
        <p className="text-text-muted">Please complete onboarding to talk with your AI Climate Coach.</p>
        <Button onClick={() => navigate(ROUTES.ONBOARDING)}>Get Started</Button>
      </div>
    );
  }

  const activeUserId = user?.id ?? mockUserProfile.id;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Climate Coach</h1>
        <p className="text-text-muted mt-1">Ask anything about climate science or your footprint.</p>
      </div>
      <AssistantChat userId={activeUserId} />
    </div>
  );
};

export default Assistant;
