import { NavLink, Outlet, Link, useLocation } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import { useTheme } from "../context/ThemeContext";
import { getReviewQueue } from "../services/api";

const NAV_LABELS = {
  "/generate": "Generate",
  "/review": "Review Queue",
  "/export": "Export & Publish",
  "/dashboard": "Dashboard",
  "/settings": "Settings"
};

const getTabFromSearch = (search) => {
  const params = new URLSearchParams(search);
  const tab = params.get("tab");
  return tab === "manual" || tab === "locators" || tab === "jira" ? tab : "jira";
};

function AppLayout() {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const [pendingCount, setPendingCount] = useState(0);
  const [navError, setNavError] = useState("");
  const activeTab = getTabFromSearch(location.search);

  const breadcrumbLabel = useMemo(() => {
    if (location.pathname.startsWith("/generate")) {
      return "Generate";
    }
    return NAV_LABELS[location.pathname] || "Generate";
  }, [location.pathname]);

  useEffect(() => {
    const loadPending = async () => {
      try {
        const response = await getReviewQueue("pending");
        setPendingCount(Number(response?.counts?.pending || 0));
        setNavError("");
      } catch (err) {
        setPendingCount(0);
        setNavError(err?.message || "Unable to load review counts");
      }
    };
    loadPending();
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <nav className="topnav">
        <div className="logo">
          <div className="logo-icon">🔥</div>
          Phoenix SmartCaseAI
        </div>
        <div className="breadcrumb">
          <span className="sep">&gt;</span>
          <span className="crumb-active">{breadcrumbLabel}</span>
        </div>
        <div className="nav-right">
          <span className="badge">🟢 Live</span>
          <button type="button" className="theme-btn" onClick={toggleTheme}>
            {theme === "dark" ? "☀ Light" : "🌙 Dark"}
          </button>
          <div className="avatar" aria-label="User profile">
            HU
          </div>
        </div>
      </nav>

      <div className="layout">
        <aside className="sidebar">
          <div className="sidebar-label">Generate</div>
          <Link
            to="/generate?tab=jira"
            className={`sidebar-item ${location.pathname === "/generate" && activeTab === "jira" ? "active" : ""}`}
          >
            <span className="si">🎯</span> Jira Issue
          </Link>
          <Link
            to="/generate?tab=manual"
            className={`sidebar-item ${location.pathname === "/generate" && activeTab === "manual" ? "active" : ""}`}
          >
            <span className="si">✏️</span> Manual Input
          </Link>
          <Link
            to="/generate?tab=locators"
            className={`sidebar-item ${location.pathname === "/generate" && activeTab === "locators" ? "active" : ""}`}
          >
            <span className="si">🔎</span> Locators
          </Link>
          <div className="sidebar-divider" />
          <div className="sidebar-label">Output</div>
          <NavLink
            to="/review"
            className={({ isActive }) => `sidebar-item ${isActive ? "active" : ""}`}
          >
            <span className="si">📋</span> Review Queue
            {pendingCount ? <span className="s-badge">{pendingCount}</span> : null}
          </NavLink>
          <NavLink
            to="/export"
            className={({ isActive }) => `sidebar-item ${isActive ? "active" : ""}`}
          >
            <span className="si">📤</span> Export & Publish
          </NavLink>
          <div className="sidebar-divider" />
          <div className="sidebar-label">Platform</div>
          <NavLink
            to="/dashboard"
            className={({ isActive }) => `sidebar-item ${isActive ? "active" : ""}`}
          >
            <span className="si">📊</span> Dashboard
          </NavLink>
          <NavLink
            to="/settings"
            className={({ isActive }) => `sidebar-item ${isActive ? "active" : ""}`}
          >
            <span className="si">⚙️</span> Settings
          </NavLink>
          {navError ? <div className="sidebar-note">{navError}</div> : null}
        </aside>

        <main className="main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default AppLayout;
