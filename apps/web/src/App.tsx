import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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
import NotFound from "./pages/NotFound";

import { AppLayout } from "./components/layout/AppLayout";
import { AdminLayout } from "./components/layout/AdminLayout";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/onboarding" element={<OnboardingPage />} />

          {/* User app */}
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

          {/* Admin */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="cases" element={<CaseReviewPage />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
