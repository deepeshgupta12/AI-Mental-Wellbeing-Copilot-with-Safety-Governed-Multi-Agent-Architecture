import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import LandingPage from "./pages/Landing";
import AuthPage from "./pages/Auth";
import OnboardingPage from "./pages/Onboarding";
import DashboardPage from "./pages/Dashboard";
import CheckInPage from "./pages/CheckIn";
import ChatPage from "./pages/Chat";
import JournalPage from "./pages/Journal";
import InsightsPage from "./pages/Insights";
import PlansPage from "./pages/Plans";
import SafetyPage from "./pages/Safety";
import SettingsPage from "./pages/Settings";
import AdminDashboard from "./pages/admin/AdminDashboard";
import CaseReviewPage from "./pages/admin/CaseReview";
import FlaggedSessionsPage from "./pages/admin/FlaggedSessions";
import SessionLogsPage from "./pages/admin/SessionLogs";
import AuditLogsPage from "./pages/admin/AuditLogs";
import PolicyViewerPage from "./pages/admin/PolicyViewer";
import NotFound from "./pages/NotFound";

import { AppLayout } from "./components/layout/AppLayout";
import { AdminLayout } from "./components/layout/AdminLayout";

const App = () => (
  <TooltipProvider>
    <Toaster />
    <Sonner />
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/onboarding" element={<OnboardingPage />} />

        <Route path="/app" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="checkin" element={<CheckInPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="journal" element={<JournalPage />} />
          <Route path="insights" element={<InsightsPage />} />
          <Route path="plans" element={<PlansPage />} />
          <Route path="safety" element={<SafetyPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="flagged" element={<FlaggedSessionsPage />} />
          <Route path="sessions" element={<SessionLogsPage />} />
          <Route path="cases" element={<CaseReviewPage />} />
          <Route path="audit" element={<AuditLogsPage />} />
          <Route path="policy" element={<PolicyViewerPage />} />
        </Route>

        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  </TooltipProvider>
);

export default App;