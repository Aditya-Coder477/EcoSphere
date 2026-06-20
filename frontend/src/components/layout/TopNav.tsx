import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { Menu } from 'lucide-react';

const TopNav = () => {
  const user = useAppStore((state) => state.user);

  return (
    <header className="h-16 border-b border-border bg-surface/50 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-10">
      <div className="flex items-center gap-4">
        <button className="md:hidden text-text-muted hover:text-text-main">
          <Menu className="w-6 h-6" />
        </button>
      </div>
      <div className="flex items-center gap-4">
        {user ? (
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium">{user.name}</span>
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
          </div>
        ) : null}
      </div>
    </header>
  );
};

export default TopNav;
