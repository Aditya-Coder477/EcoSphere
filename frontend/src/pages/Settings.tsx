import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Moon, Sun, FlaskConical, RefreshCw, Bell, Globe } from 'lucide-react';

const ToggleRow: React.FC<{
  icon: React.ReactNode;
  title: string;
  description: string;
  checked: boolean;
  onChange: () => void;
  id: string;
}> = ({ icon, title, description, checked, onChange, id }) => (
  <div className="flex items-center justify-between gap-4 py-4 border-b border-border/50 last:border-0">
    <div className="flex items-start gap-3">
      <span className="text-primary mt-0.5">{icon}</span>
      <div>
        <label htmlFor={id} className="text-sm font-medium text-text-main cursor-pointer">{title}</label>
        <p className="text-xs text-text-muted leading-relaxed mt-0.5">{description}</p>
      </div>
    </div>
    <button
      id={id}
      role="switch"
      aria-checked={checked}
      onClick={onChange}
      className={`relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary/50 ${
        checked ? 'bg-primary border-primary' : 'bg-surface border-border'
      }`}
    >
      <span
        className={`pointer-events-none inline-block h-4 w-4 mt-0.5 rounded-full bg-white shadow transition-transform duration-200 ${
          checked ? 'translate-x-5' : 'translate-x-0.5'
        }`}
      />
    </button>
  </div>
);

const Settings = () => {
  const { isDemoMode, theme, toggleDemoMode, toggleTheme, logout, setUser, setFootprint } = useAppStore();
  const [notifications, setNotifications] = React.useState(true);

  const handleResetDemo = () => {
    setUser(null);
    setFootprint(null);
    window.location.href = '/';
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-text-muted mt-1">Manage your app preferences and demo data.</p>
      </div>

      {/* Appearance */}
      <Card>
        <CardHeader><CardTitle className="text-base">Appearance</CardTitle></CardHeader>
        <CardContent className="pt-0">
          <ToggleRow
            id="theme-toggle"
            icon={theme === 'dark' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            title={`${theme === 'dark' ? 'Dark' : 'Light'} Mode`}
            description="Switch between dark and light interface themes."
            checked={theme === 'dark'}
            onChange={toggleTheme}
          />
        </CardContent>
      </Card>

      {/* Demo & Data */}
      <Card>
        <CardHeader><CardTitle className="text-base">Data & Demo</CardTitle></CardHeader>
        <CardContent className="pt-0">
          <ToggleRow
            id="demo-toggle"
            icon={<FlaskConical className="w-4 h-4" />}
            title="Demo Mode"
            description="Show sample data across all pages. Useful for exploring the app without a backend connection."
            checked={isDemoMode}
            onChange={toggleDemoMode}
          />
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader><CardTitle className="text-base">Notifications</CardTitle></CardHeader>
        <CardContent className="pt-0">
          <ToggleRow
            id="notif-toggle"
            icon={<Bell className="w-4 h-4" />}
            title="Weekly Summary"
            description="Receive a weekly digest of your footprint progress and new recommendations."
            checked={notifications}
            onChange={() => setNotifications((p) => !p)}
          />
        </CardContent>
      </Card>

      {/* Language placeholder */}
      <Card>
        <CardHeader><CardTitle className="text-base">Language</CardTitle></CardHeader>
        <CardContent className="pt-0">
          <div className="flex items-center gap-3 py-3 text-sm text-text-muted">
            <Globe className="w-4 h-4 text-primary" aria-hidden="true" />
            <span>Language selection — coming soon.</span>
          </div>
        </CardContent>
      </Card>

      {/* Danger zone */}
      <Card className="border-red-500/20">
        <CardHeader><CardTitle className="text-base text-red-400">Account</CardTitle></CardHeader>
        <CardContent className="pt-0 flex flex-col sm:flex-row gap-3">
          <Button
            variant="outline"
            onClick={handleResetDemo}
            className="border-red-500/40 text-red-400 hover:bg-red-500/10 gap-2"
          >
            <RefreshCw className="w-4 h-4" aria-hidden="true" />
            Reset & Start Over
          </Button>
          <Button
            variant="outline"
            onClick={logout}
            className="border-border text-text-muted hover:text-red-400 hover:border-red-500/40"
          >
            Sign Out
          </Button>
        </CardContent>
      </Card>

      {/* About */}
      <p className="text-xs text-text-muted/50 text-center pb-4">
        EcoSphere v0.9.0 — Carbon Footprint Awareness Platform
      </p>
    </div>
  );
};

export default Settings;
