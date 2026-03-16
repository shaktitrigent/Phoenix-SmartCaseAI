import { useEffect, useMemo, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { approveAllPending, getReviewQueue, updateReviewStatus } from "../services/api";
import { getFriendlyError } from "../utils/error";

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
  const [showRejectionModal, setShowRejectionModal] = useState(false);
  const [rejectionTestCase, setRejectionTestCase] = useState(null);
  const [rejectionReason, setRejectionReason] = useState("");

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

  const loadQueue = async (filter = "all", { silent } = {}) => {
    try {
      if (!silent) setLoading(true);
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
      if (!silent) {
        addToast(getFriendlyError(err, "Unable to load review queue"), "error");
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue(activeFilter, { silent: false });
  }, [activeFilter]);

  useEffect(() => {
    const intervalId = window.setInterval(() => {
      loadQueue(activeFilter, { silent: true });
    }, 15000);
    return () => window.clearInterval(intervalId);
  }, [activeFilter]);

  const toggleRow = (rowKey) => {
    setOpenRows((prev) => ({ ...prev, [rowKey]: !prev[rowKey] }));
  };

  const handleReviewUpdate = async (item, status, customNote = null) => {
    const testCaseId = String(item?.test_case_id || "").trim();
    if (!testCaseId) {
      addToast("Missing test_case_id for this row.", "error");
      return;
    }
    try {
      setLoading(true);
      const note = customNote !== null ? customNote : (noteDrafts[testCaseId] || "");
      const response = await updateReviewStatus({
        test_case_id: testCaseId,
        review_status: status,
        note
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
      addToast(getFriendlyError(err, "Update failed"), "error");
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
      addToast(getFriendlyError(err, "Approve all failed"), "error");
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
                        onClick={() => {
                          setRejectionTestCase(item);
                          setRejectionReason(noteDrafts[rowKey] || "");
                          setShowRejectionModal(true);
                        }}
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

      {showRejectionModal && rejectionTestCase && (
        <div className="modal-overlay" onClick={() => setShowRejectionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Reject Test Case</h3>
              <button
                type="button"
                className="modal-close"
                onClick={() => setShowRejectionModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>Provide a reason for rejecting test case <strong>{rejectionTestCase.test_case_id}</strong>:</p>
              <textarea
                rows={4}
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
                placeholder="Enter rejection reason..."
                required
              />
            </div>
            <div className="modal-footer">
              <button
                type="button"
                className="btn ghost"
                onClick={() => setShowRejectionModal(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="btn secondary"
                onClick={async () => {
                  if (!rejectionReason.trim()) {
                    addToast("Rejection reason is required.", "error");
                    return;
                  }
                  await handleReviewUpdate(rejectionTestCase, "rejected", rejectionReason);
                  setShowRejectionModal(false);
                  setRejectionTestCase(null);
                  setRejectionReason("");
                }}
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReviewQueue;
