import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { ClientDetailPage } from "./pages/ClientDetailPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { VersionDetailPage } from "./pages/VersionDetailPage";
import { ADRListPage } from "./pages/ADRListPage";
import { ADRDetailPage } from "./pages/ADRDetailPage";
import { QuestionListPage } from "./pages/QuestionListPage";
import { ComparisonPage } from "./pages/ComparisonPage";
import { KnowledgePage } from "./pages/KnowledgePage";

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/clients/:clientId" element={<ClientDetailPage />} />
            <Route path="/clients/:clientId/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/clients/:clientId/projects/:projectId/versions/:versionId" element={<VersionDetailPage />} />
            <Route path="/clients/:clientId/projects/:projectId/versions/:versionId/adrs" element={<ADRListPage />} />
            <Route path="/clients/:clientId/projects/:projectId/versions/:versionId/adrs/:adrId" element={<ADRDetailPage />} />
            <Route path="/clients/:clientId/projects/:projectId/versions/:versionId/questions" element={<QuestionListPage />} />
            <Route path="/clients/:clientId/projects/:projectId/compare" element={<ComparisonPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
