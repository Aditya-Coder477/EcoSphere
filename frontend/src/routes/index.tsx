import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ROUTES } from '../constants/routes';

import Home from '../pages/Home';
import Onboarding from '../pages/Onboarding';
import AppShell from '../components/layout/AppShell';
import Dashboard from '../pages/Dashboard';
import CarbonBreakdown from '../pages/CarbonBreakdown';
import Recommendations from '../pages/Recommendations';
import Assistant from '../pages/Assistant';
import Journey from '../pages/Journey';
import Profile from '../pages/Profile';
import Settings from '../pages/Settings';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path={ROUTES.HOME} element={<Home />} />
      <Route path={ROUTES.ONBOARDING} element={<Onboarding />} />

      <Route element={<AppShell />}>
        <Route path={ROUTES.DASHBOARD}       element={<Dashboard />} />
        <Route path={ROUTES.BREAKDOWN}       element={<CarbonBreakdown />} />
        <Route path={ROUTES.RECOMMENDATIONS} element={<Recommendations />} />
        <Route path={ROUTES.ASSISTANT}       element={<Assistant />} />
        <Route path={ROUTES.HISTORY}         element={<Journey />} />
        <Route path={ROUTES.PROFILE}         element={<Profile />} />
        <Route path={ROUTES.SETTINGS}        element={<Settings />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
