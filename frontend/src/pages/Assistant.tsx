import React from 'react';
import { AssistantChat } from '../components/assistant/AssistantChat';
import { useAppStore } from '../store/useAppStore';

const Assistant = () => {
  const user = useAppStore(state => state.user);

  if (!user) return null;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">AI Climate Coach</h1>
        <p className="text-text-muted mt-1">Ask anything about climate science or your footprint.</p>
      </div>
      <AssistantChat userId={user.id} />
    </div>
  );
};

export default Assistant;
