import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import ErrorBoundary from "./components/ErrorBoundary";
import Dashboard from "./pages/Dashboard";
import ExportPublish from "./pages/ExportPublish";
import Home from "./pages/Home";
import ReviewQueue from "./pages/ReviewQueue";
import Settings from "./pages/Settings";

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<Navigate to="/generate" replace />} />
            <Route path="generate" element={<Home />} />
            <Route path="review" element={<ReviewQueue />} />
            <Route path="export" element={<ExportPublish />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          <Route path="*" element={<Navigate to="/generate" replace />} />
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;

