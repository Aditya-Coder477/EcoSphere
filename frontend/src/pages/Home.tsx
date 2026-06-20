import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Leaf } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { ROUTES } from '../constants/routes';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-accent/20 blur-[120px] rounded-full pointer-events-none"></div>

      <header className="px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <Leaf className="w-8 h-8 text-primary" />
          <span className="font-bold text-2xl text-gradient">EcoSphere</span>
        </div>
        <Button onClick={() => navigate(ROUTES.ONBOARDING)} variant="outline" className="rounded-full">
          Get Started
        </Button>
      </header>

      <main className="flex-1 flex items-center justify-center p-6 z-10">
        <div className="max-w-3xl text-center space-y-8">
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-text-main leading-tight">
            Track your impact.<br />
            <span className="text-gradient">Transform the future.</span>
          </h1>
          <p className="text-xl text-text-muted md:px-12 leading-relaxed">
            Discover your carbon footprint, get personalized AI-driven insights, and take actionable steps to live a more sustainable lifestyle.
          </p>
          <div className="pt-8">
            <Button size="lg" className="rounded-full text-lg px-8 py-6 shadow-lg shadow-primary/25" onClick={() => navigate(ROUTES.ONBOARDING)}>
              Calculate Your Footprint Now
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Home;
