import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import { useAppStore } from '../../store/useAppStore';
import { ROUTES } from '../../constants/routes';

const AppShell = () => {
  const user = useAppStore((state) => state.user);

  if (!user) {
    return <Navigate to={ROUTES.HOME} replace />;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-auto p-6 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AppShell;
