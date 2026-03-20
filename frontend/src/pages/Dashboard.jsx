import { useEffect, useMemo, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { getDashboardMetrics } from "../services/api";
import { getFriendlyError } from "../utils/error";

const typeColorMap = {
  functional: "var(--blue)",
  regression: "var(--purple)",
  ui: "var(--amber)",
  security: "var(--red)",
  performance: "var(--green)",
  smoke: "var(--amber)"
};

const priorityColorMap = {
  high: "var(--red)",
  medium: "var(--amber)",
  low: "var(--txt3)"
};

function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id));
    }, 9000);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((item) => item.id !== id));
  };

  const loadMetrics = async ({ silent } = {}) => {
    try {
      if (!silent) setLoading(true);
      const response = await getDashboardMetrics();
      setMetrics(response || null);
    } catch (err) {
      if (!silent) {
        addToast(getFriendlyError(err, "Unable to load dashboard"), "error");
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics({ silent: false });
    const intervalId = window.setInterval(() => {
      loadMetrics({ silent: true });
    }, 15000);
    return () => window.clearInterval(intervalId);
  }, []);

  const counts = metrics?.counts || { total: 0, approved: 0, pending: 0, rejected: 0 };
  const total = Number(counts.total || 0) || 0;

  const typeBreakdown = useMemo(() => {
    const entries = Object.entries(metrics?.type_breakdown || {});
    return entries.map(([key, value]) => ({
      key,
      value: Number(value || 0),
      percent: total ? Math.round((Number(value || 0) / total) * 100) : 0,
      color: typeColorMap[key] || "var(--txt3)"
    }));
  }, [metrics, total]);

  const priorityBreakdown = useMemo(() => {
    const entries = Object.entries(metrics?.priority_breakdown || {});
    return entries.map(([key, value]) => ({
      key,
      value: Number(value || 0),
      percent: total ? Math.round((Number(value || 0) / total) * 100) : 0,
      color: priorityColorMap[key] || "var(--txt3)"
    }));
  }, [metrics, total]);

  const activity = Array.isArray(metrics?.recent_activity) ? metrics.recent_activity : [];

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Loading dashboard..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="page-header">
        <div>
          <h2 className="page-title">Dashboard</h2>
          <p className="page-subtitle">
            Platform overview - review throughput, approval rate, and coverage breakdowns.
          </p>
        </div>
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Test Cases Generated</div>
          <div className="stat-val">{counts.total}</div>
          <div className="stat-sub">Across Jira + manual sources</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Approval Rate</div>
          <div className="stat-val">{metrics?.approval_rate ?? 0}%</div>
          <div className="stat-sub">Approved / Total</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pending Review</div>
          <div className="stat-val text-warning">{counts.pending}</div>
          <div className="stat-sub">Awaiting QA sign-off</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Rejected</div>
          <div className="stat-val text-danger">{counts.rejected}</div>
          <div className="stat-sub">Excluded from export</div>
        </div>
      </div>

      <div className="chart-grid">
        <div className="card split">
          <div className="card-head">
            <div className="ch-icon">📊</div>
            <h3 className="section-title">Test Type Breakdown</h3>
          </div>
          <div className="card-body">
            {typeBreakdown.length ? (
              <div className="chart-bar-wrap">
                {typeBreakdown.map((row) => (
                  <div key={row.key} className="chart-bar-row">
                    <span className="chart-bar-label">{row.key}</span>
                    <div className="chart-bar-track">
                      <div
                        className="chart-bar-fill"
                        style={{ width: `${row.percent}%`, background: row.color }}
                      />
                    </div>
                    <span className="chart-bar-val">{row.percent}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-illustration" />
                <p>No test case data yet.</p>
              </div>
            )}
          </div>
        </div>

        <div className="card split">
          <div className="card-head">
            <div className="ch-icon">⚡</div>
            <h3 className="section-title">Priority Breakdown</h3>
          </div>
          <div className="card-body">
            {priorityBreakdown.length ? (
              <div className="chart-bar-wrap">
                {priorityBreakdown.map((row) => (
                  <div key={row.key} className="chart-bar-row">
                    <span className="chart-bar-label">{row.key}</span>
                    <div className="chart-bar-track">
                      <div
                        className="chart-bar-fill"
                        style={{ width: `${row.percent}%`, background: row.color }}
                      />
                    </div>
                    <span className="chart-bar-val">{row.percent}%</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-illustration" />
                <p>No priority data yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card split activity-card">
        <div className="card-head">
          <div className="ch-icon">🕒</div>
          <h3 className="section-title">Recent Activity</h3>
        </div>
        <div className="card-body">
          {!activity.length ? (
            <div className="empty-state">
              <div className="empty-illustration" />
              <p>No activity yet.</p>
            </div>
          ) : (
            <div className="activity-list">
              {activity.map((item, idx) => (
                <div key={`${item.message}-${idx}`} className="activity-row">
                  <span className={`activity-dot ${item.category || "system"}`} />
                  <div>
                    <div className="activity-message">{item.message}</div>
                    <div className="activity-meta">{item.category || "system"}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
