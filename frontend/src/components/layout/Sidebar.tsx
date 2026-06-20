import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, PieChart, Lightbulb, MessageSquare,
  History, User, Settings,
} from 'lucide-react';
import { ROUTES } from '../../constants/routes';

const Sidebar = () => {
  const links = [
    { to: ROUTES.DASHBOARD,       icon: LayoutDashboard, label: 'Dashboard' },
    { to: ROUTES.BREAKDOWN,       icon: PieChart,         label: 'Breakdown' },
    { to: ROUTES.RECOMMENDATIONS, icon: Lightbulb,        label: 'Actions' },
    { to: ROUTES.ASSISTANT,       icon: MessageSquare,    label: 'Assistant' },
    { to: ROUTES.HISTORY,         icon: History,          label: 'Journey' },
    { to: ROUTES.PROFILE,         icon: User,             label: 'Profile' },
    { to: ROUTES.SETTINGS,        icon: Settings,         label: 'Settings' },
  ];

  return (
    <aside className="w-64 border-r border-border bg-surface/50 backdrop-blur-sm hidden md:flex flex-col">
      <div className="h-16 flex items-center px-6 border-b border-border">
        <span className="font-bold text-xl text-gradient">EcoSphere</span>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-1" aria-label="Main navigation">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors text-sm font-medium ${
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-text-muted hover:text-text-main hover:bg-surface'
                }`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" aria-hidden="true" />
              {link.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
};

export default Sidebar;
