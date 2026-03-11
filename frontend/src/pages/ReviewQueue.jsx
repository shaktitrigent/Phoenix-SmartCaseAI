import { useEffect, useMemo, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { approveAllPending, getReviewQueue, updateReviewStatus } from "../services/api";

const FILTERS = [
  { id: "all", label: "All" },
  { id: "pending", label: "Pending" },
  { id: "approved", label: "Approved" },
  { id: "rejected", label: "Rejected" }
];

const statusIcon = (status) => {
  if (status === "approved") return "✅";
  if (status === "rejected") return "❌";
  return "⏳";
};

function ReviewQueue() {
  const [activeFilter, setActiveFilter] = useState("all");
  const [cases, setCases] = useState([]);
  const [counts, setCounts] = useState({ total: 0, pending: 0, approved: 0, rejected: 0 });
  const [openRows, setOpenRows] = useState({});
  const [noteDrafts, setNoteDrafts] = useState({});
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { id, message, type }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id));
    }, 4500);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((item) => item.id !== id));
  };

  const loadQueue = async (filter = "all") => {
    try {
      setLoading(true);
      const response = await getReviewQueue(filter);
      const items = Array.isArray(response?.test_cases) ? response.test_cases : [];
      setCases(items);
      setCounts(response?.counts || { total: items.length, pending: 0, approved: 0, rejected: 0 });
      setNoteDrafts((prev) => {
        const next = { ...prev };
        items.forEach((item) => {
          const key = String(item?.test_case_id || item?.id || "");
          if (!next[key]) {
            next[key] = item?.review_note || "";
          }
        });
        return next;
      });
    } catch (err) {
      addToast(err?.response?.data?.error || err?.message || "Unable to load review queue", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue(activeFilter);
  }, [activeFilter]);

  const toggleRow = (rowKey) => {
    setOpenRows((prev) => ({ ...prev, [rowKey]: !prev[rowKey] }));
  };

  const handleReviewUpdate = async (item, status) => {
    const testCaseId = String(item?.test_case_id || "").trim();
    if (!testCaseId) {
      addToast("Missing test_case_id for this row.", "error");
      return;
    }
    try {
      setLoading(true);
      const response = await updateReviewStatus({
        test_case_id: testCaseId,
        review_status: status,
        note: noteDrafts[testCaseId] || ""
      });
      const updatedCase = response?.updated || {};
      setCases((prev) =>
        prev.map((row) => (row.test_case_id === updatedCase.test_case_id ? updatedCase : row))
      );
      if (response?.counts) {
        setCounts(response.counts);
      }
      addToast(`Marked ${testCaseId} as ${status}.`, "success");
    } catch (err) {
      addToast(err?.response?.data?.error || err?.message || "Update failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleApproveAll = async () => {
    try {
      setLoading(true);
      const response = await approveAllPending();
      if (response?.counts) {
        setCounts(response.counts);
      }
      await loadQueue(activeFilter);
      addToast("Approved all pending cases.", "success");
    } catch (err) {
      addToast(err?.response?.data?.error || err?.message || "Approve all failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const emptyMessage = useMemo(() => {
    if (activeFilter === "approved") return "No approved cases yet.";
    if (activeFilter === "rejected") return "No rejected cases yet.";
    if (activeFilter === "pending") return "No pending cases yet.";
    return "No review cases available.";
  }, [activeFilter]);

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Updating review queue..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="page-header">
        <div>
          <h2 className="page-title">Review Queue</h2>
          <p className="page-subtitle">
            QA leads review generated test cases before export or TestRail publish.
          </p>
        </div>
        <div className="inline">
          <button type="button" className="btn secondary small" onClick={handleApproveAll}>
            Approve All Pending
          </button>
        </div>
      </div>

      <div className="rq-filters">
        {FILTERS.map((filter) => (
          <button
            key={filter.id}
            type="button"
            className={`rq-filter ${activeFilter === filter.id ? "active" : ""}`}
            onClick={() => setActiveFilter(filter.id)}
          >
            {filter.label}
            <span className="cnt">{counts[filter.id] ?? counts.total ?? 0}</span>
          </button>
        ))}
      </div>

      <div className="rq-list">
        {!cases.length ? (
          <div className="empty-state">
            <div className="empty-illustration" />
            <p>{emptyMessage}</p>
          </div>
        ) : (
          cases.map((item) => {
            const rowKey = String(item?.test_case_id || item?.id || "");
            const isOpen = Boolean(openRows[rowKey]);
            const reviewStatus = String(item?.review_status || "pending").toLowerCase();
            return (
              <div key={rowKey} className={`rq-item ${reviewStatus}-item`}>
                <div className="rq-head" onClick={() => toggleRow(rowKey)} role="button" tabIndex={0}>
                  <div className="rq-status-icon">{statusIcon(reviewStatus)}</div>
                  <div className="rq-info">
                    <div className="rq-title">
                      {item.test_case_id} — {item.title}
                    </div>
                    <div className="rq-meta">
                      <span className={`pill type-pill type-${String(item.test_type || "").toLowerCase()}`}>
                        {item.test_type || "Unspecified"}
                      </span>
                      <span className={`pill priority-pill priority-${String(item.priority || "").toLowerCase()}`}>
                        {item.priority || "Priority"}
                      </span>
                      <span className={`status-tag ${reviewStatus}`}>
                        {reviewStatus.charAt(0).toUpperCase() + reviewStatus.slice(1)}
                      </span>
                    </div>
                  </div>
                  <div className="rq-caret">{isOpen ? "▲" : "▼"}</div>
                </div>
                {isOpen ? (
                  <div className="rq-body">
                    <div className="rq-section">
                      <div className="rq-section-label">Preconditions</div>
                      <div className="rq-text">{item.preconditions || "-"}</div>
                    </div>
                    <div className="rq-section">
                      <div className="rq-section-label">Steps</div>
                      <div className="rq-text pre-wrap">
                        {(item.steps || []).length ? (item.steps || []).join("\n") : "-"}
                      </div>
                    </div>
                    <div className="rq-section">
                      <div className="rq-section-label">Expected Result</div>
                      <div className="rq-text">{item.expected_result || "-"}</div>
                    </div>
                    <div className="rq-section rq-note">
                      <div className="rq-section-label">Reviewer Note (optional)</div>
                      <textarea
                        rows={2}
                        value={noteDrafts[rowKey] || ""}
                        onChange={(event) =>
                          setNoteDrafts((prev) => ({ ...prev, [rowKey]: event.target.value }))
                        }
                        placeholder="Add review notes for this case..."
                      />
                    </div>
                    <div className="rq-actions">
                      <button
                        type="button"
                        className="btn testrail small"
                        onClick={() => handleReviewUpdate(item, "approved")}
                      >
                        Approve
                      </button>
                      <button
                        type="button"
                        className="btn ghost small"
                        onClick={() => handleReviewUpdate(item, "pending")}
                      >
                        Mark Pending
                      </button>
                      <button
                        type="button"
                        className="btn secondary small"
                        onClick={() => handleReviewUpdate(item, "rejected")}
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default ReviewQueue;
