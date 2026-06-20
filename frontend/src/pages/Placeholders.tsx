import React from 'react';

const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="space-y-6">
    <div>
      <h1 className="text-3xl font-bold tracking-tight">{title}</h1>
      <p className="text-text-muted mt-1">This page is under construction.</p>
    </div>
    <div className="h-64 glass-panel flex items-center justify-center text-text-muted">
      Coming Soon
    </div>
  </div>
);

export const CarbonBreakdown = () => <PlaceholderPage title="Carbon Breakdown" />;
export const History = () => <PlaceholderPage title="Carbon Journey" />;
export const Profile = () => <PlaceholderPage title="User Profile" />;
export const Settings = () => <PlaceholderPage title="Settings" />;
