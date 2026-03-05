import { useEffect, useMemo, useState } from "react";

const editableFields = ["title", "preconditions", "expected_result", "test_type", "priority", "steps"];

const timestampNow = () => new Date().toISOString();

function TestCaseTable({ testCases, onChange }) {
  const [draftCases, setDraftCases] = useState([]);

  useEffect(() => {
    const normalized = Array.isArray(testCases)
      ? testCases.map((item) => ({
          ...item,
          review_status: item?.review_status || "approved",
          is_edited: Boolean(item?.is_edited),
          edited_fields: Array.isArray(item?.edited_fields) ? item.edited_fields : [],
          last_edited_at: item?.last_edited_at || "",
          last_edited_by: item?.last_edited_by || ""
        }))
      : [];
    setDraftCases(normalized);
  }, [testCases]);

  const summary = useMemo(() => {
    const approved = draftCases.filter((x) => x.review_status === "approved").length;
    const rejected = draftCases.filter((x) => x.review_status === "rejected").length;
    const pending = draftCases.filter((x) => x.review_status === "pending").length;
    const edited = draftCases.filter((x) => x.is_edited).length;
    return { approved, rejected, pending, edited };
  }, [draftCases]);

  const updateCases = (nextCases) => {
    setDraftCases(nextCases);
    onChange?.(nextCases);
  };

  const markEdited = (caseItem, field) => {
    const tracked = new Set(Array.isArray(caseItem.edited_fields) ? caseItem.edited_fields : []);
    if (field && editableFields.includes(field)) {
      tracked.add(field);
    }
    return {
      ...caseItem,
      is_edited: true,
      edited_fields: Array.from(tracked),
      last_edited_at: timestampNow(),
      last_edited_by: "manual"
    };
  };

  const updateField = (index, field, value) => {
    const next = draftCases.map((item, idx) => {
      if (idx !== index) {
        return item;
      }
      const updated = { ...item, [field]: value };
      return markEdited(updated, field);
    });
    updateCases(next);
  };

  const updateStatus = (index, status) => {
    const next = draftCases.map((item, idx) => {
      if (idx !== index) {
        return item;
      }
      return { ...item, review_status: status };
    });
    updateCases(next);
  };

  const updateStep = (caseIndex, stepIndex, value) => {
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = Array.isArray(item.steps) ? [...item.steps] : [];
      steps[stepIndex] = value;
      return markEdited({ ...item, steps }, "steps");
    });
    updateCases(next);
  };

  const addStep = (caseIndex) => {
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = Array.isArray(item.steps) ? [...item.steps, ""] : [""];
      return markEdited({ ...item, steps }, "steps");
    });
    updateCases(next);
  };

  const removeStep = (caseIndex, stepIndex) => {
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = (Array.isArray(item.steps) ? item.steps : []).filter((_, i) => i !== stepIndex);
      return markEdited({ ...item, steps }, "steps");
    });
    updateCases(next);
  };

  if (!testCases?.length) {
    return (
      <div className="card">
        <h3 className="section-title">Test Cases</h3>
        <div className="empty-state">
          <div className="empty-illustration" />
          <p>No test cases generated yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="section-title">Generated Test Cases ({draftCases.length})</h3>
      <div className="inline review-summary">
        <span className="status-pill">Approved: {summary.approved}</span>
        <span className="status-pill">Pending: {summary.pending}</span>
        <span className="status-pill">Rejected: {summary.rejected}</span>
        <span className="status-pill">Edited: {summary.edited}</span>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Preconditions</th>
              <th>Steps</th>
              <th>Expected Result</th>
              <th>Type</th>
              <th>Priority</th>
              <th>Review</th>
            </tr>
          </thead>
          <tbody>
            {draftCases.map((item, caseIndex) => (
              <tr key={item.test_case_id || item.title}>
                <td>{item.test_case_id}</td>
                <td>
                  <textarea
                    rows={3}
                    value={item.title || ""}
                    onChange={(event) => updateField(caseIndex, "title", event.target.value)}
                  />
                </td>
                <td>
                  <textarea
                    rows={3}
                    value={item.preconditions || ""}
                    onChange={(event) => updateField(caseIndex, "preconditions", event.target.value)}
                  />
                </td>
                <td>
                  <ol>
                    {(item.steps || []).map((s, idx) => (
                      <li key={`${item.test_case_id}-${idx}`} className="step-edit-item">
                        <textarea
                          rows={2}
                          value={s}
                          onChange={(event) => updateStep(caseIndex, idx, event.target.value)}
                        />
                        <button
                          type="button"
                          className="btn ghost small"
                          onClick={() => removeStep(caseIndex, idx)}
                          disabled={(item.steps || []).length <= 1}
                        >
                          Remove
                        </button>
                      </li>
                    ))}
                  </ol>
                  <button type="button" className="btn ghost small" onClick={() => addStep(caseIndex)}>
                    Add Step
                  </button>
                </td>
                <td>
                  <textarea
                    rows={3}
                    value={item.expected_result || ""}
                    onChange={(event) => updateField(caseIndex, "expected_result", event.target.value)}
                  />
                </td>
                <td>
                  <input
                    value={item.test_type || ""}
                    onChange={(event) => updateField(caseIndex, "test_type", event.target.value)}
                  />
                </td>
                <td>
                  <input
                    value={item.priority || ""}
                    onChange={(event) => updateField(caseIndex, "priority", event.target.value)}
                  />
                </td>
                <td>
                  <div className="review-actions">
                    <button
                      type="button"
                      className={`btn small ${item.review_status === "approved" ? "" : "ghost"}`}
                      onClick={() => updateStatus(caseIndex, "approved")}
                    >
                      Approve
                    </button>
                    <button
                      type="button"
                      className={`btn small ${item.review_status === "pending" ? "" : "ghost"}`}
                      onClick={() => updateStatus(caseIndex, "pending")}
                    >
                      Pending
                    </button>
                    <button
                      type="button"
                      className={`btn small ${item.review_status === "rejected" ? "" : "ghost"}`}
                      onClick={() => updateStatus(caseIndex, "rejected")}
                    >
                      Reject
                    </button>
                    {item.is_edited ? (
                      <div className="field-muted">
                        Edited ({(item.edited_fields || []).join(", ") || "fields"})
                      </div>
                    ) : null}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TestCaseTable;
