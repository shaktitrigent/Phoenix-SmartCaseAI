import { Fragment, useEffect, useMemo, useRef, useState } from "react";

const editableFields = ["title", "preconditions", "expected_result", "test_type", "priority", "steps"];

const timestampNow = () => new Date().toISOString();
const DIFF_FIELDS = ["title", "preconditions", "expected_result", "test_type", "priority", "steps"];

const stringifySteps = (steps = []) => (Array.isArray(steps) ? steps.join("\n") : "");
const normalizeLabel = (value) => String(value || "").trim().toLowerCase();
const getTypeBadgeClass = (value) => {
  const normalized = normalizeLabel(value);
  if (!normalized) {
    return "type-unknown";
  }
  if (normalized.includes("regression")) {
    return "type-regression";
  }
  if (normalized.includes("smoke")) {
    return "type-smoke";
  }
  if (normalized.includes("functional")) {
    return "type-functional";
  }
  return "type-generic";
};
const getPriorityBadgeClass = (value) => {
  const normalized = normalizeLabel(value);
  if (!normalized) {
    return "priority-unknown";
  }
  if (normalized.includes("high")) {
    return "priority-high";
  }
  if (normalized.includes("medium")) {
    return "priority-medium";
  }
  if (normalized.includes("low")) {
    return "priority-low";
  }
  return "priority-generic";
};

const normalizeCases = (cases = []) =>
  (Array.isArray(cases) ? cases : []).map((item) => ({
    ...item,
    review_status: item?.review_status || "approved",
    is_edited: Boolean(item?.is_edited),
    edited_fields: Array.isArray(item?.edited_fields) ? item.edited_fields : [],
    last_edited_at: item?.last_edited_at || "",
    last_edited_by: item?.last_edited_by || ""
  }));

function TestCaseTable({ testCases, onSave, onDirtyChange, selectedCaseIds = [], onSelectionChange }) {
  const [baselineCases, setBaselineCases] = useState([]);
  const [draftCases, setDraftCases] = useState([]);
  const [isEditMode, setIsEditMode] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [openDiffRows, setOpenDiffRows] = useState({});
  const selectAllRef = useRef(null);

  useEffect(() => {
    const normalized = normalizeCases(testCases);
    setBaselineCases(normalized);
    setDraftCases(normalized);
    setIsEditMode(false);
    setHasUnsavedChanges(false);
    setOpenDiffRows({});
    onDirtyChange?.(false);
  }, [testCases, onDirtyChange]);

  const summary = useMemo(() => {
    const edited = draftCases.filter((x) => x.is_edited).length;
    return { edited };
  }, [draftCases]);

  const selectedIdSet = useMemo(
    () => new Set((Array.isArray(selectedCaseIds) ? selectedCaseIds : []).map((item) => String(item).trim()).filter(Boolean)),
    [selectedCaseIds]
  );

  const selectableCaseIds = useMemo(
    () =>
      draftCases
        .filter((item) => String(item?.review_status || "approved").toLowerCase() !== "rejected")
        .map((item) => String(item?.test_case_id || "").trim())
        .filter(Boolean),
    [draftCases]
  );

  const allSelectableSelected =
    selectableCaseIds.length > 0 && selectableCaseIds.every((id) => selectedIdSet.has(id));
  const someSelectableSelected =
    selectableCaseIds.length > 0 && selectableCaseIds.some((id) => selectedIdSet.has(id));

  useEffect(() => {
    if (selectAllRef.current) {
      selectAllRef.current.indeterminate = !allSelectableSelected && someSelectableSelected;
    }
  }, [allSelectableSelected, someSelectableSelected]);

  const updateDraft = (nextCases) => {
    setDraftCases(nextCases);
    const changed = JSON.stringify(nextCases) !== JSON.stringify(baselineCases);
    setHasUnsavedChanges(changed);
    onDirtyChange?.(changed);
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
    if (!isEditMode) {
      return;
    }
    const next = draftCases.map((item, idx) => {
      if (idx !== index) {
        return item;
      }
      const updated = { ...item, [field]: value };
      return markEdited(updated, field);
    });
    updateDraft(next);
  };

  const updateStep = (caseIndex, stepIndex, value) => {
    if (!isEditMode) {
      return;
    }
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = Array.isArray(item.steps) ? [...item.steps] : [];
      steps[stepIndex] = value;
      return markEdited({ ...item, steps }, "steps");
    });
    updateDraft(next);
  };

  const addStep = (caseIndex) => {
    if (!isEditMode) {
      return;
    }
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = Array.isArray(item.steps) ? [...item.steps, ""] : [""];
      return markEdited({ ...item, steps }, "steps");
    });
    updateDraft(next);
  };

  const removeStep = (caseIndex, stepIndex) => {
    if (!isEditMode) {
      return;
    }
    const next = draftCases.map((item, idx) => {
      if (idx !== caseIndex) {
        return item;
      }
      const steps = (Array.isArray(item.steps) ? item.steps : []).filter((_, i) => i !== stepIndex);
      return markEdited({ ...item, steps }, "steps");
    });
    updateDraft(next);
  };

  const handleCancel = () => {
    setDraftCases(baselineCases);
    setIsEditMode(false);
    setHasUnsavedChanges(false);
    setOpenDiffRows({});
    onDirtyChange?.(false);
  };

  const handleSave = () => {
    setBaselineCases(draftCases);
    setIsEditMode(false);
    setHasUnsavedChanges(false);
    setOpenDiffRows({});
    onDirtyChange?.(false);
    onSave?.(draftCases);
  };

  const getDiffRows = (caseIndex) => {
    const before = baselineCases[caseIndex] || {};
    const after = draftCases[caseIndex] || {};
    const rows = [];
    DIFF_FIELDS.forEach((field) => {
      const left = field === "steps" ? stringifySteps(before[field]) : String(before[field] || "");
      const right = field === "steps" ? stringifySteps(after[field]) : String(after[field] || "");
      if (left !== right) {
        rows.push({
          field,
          before: left,
          after: right
        });
      }
    });
    return rows;
  };

  const toggleDiff = (rowKey) => {
    setOpenDiffRows((prev) => ({
      ...prev,
      [rowKey]: !prev[rowKey]
    }));
  };

  const handleToggleSelectAll = (checked) => {
    onSelectionChange?.(checked ? selectableCaseIds : []);
  };

  const handleToggleRowSelection = (testCaseId, checked) => {
    const normalizedId = String(testCaseId || "").trim();
    if (!normalizedId) {
      return;
    }
    const next = new Set((Array.isArray(selectedCaseIds) ? selectedCaseIds : []).map((item) => String(item).trim()));
    if (checked) {
      next.add(normalizedId);
    } else {
      next.delete(normalizedId);
    }
    onSelectionChange?.(Array.from(next).filter(Boolean));
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
      <div className="inline review-summary">
        <h3 className="section-title">
          Test Cases <span className="table-count">{draftCases.length}</span>
        </h3>
        <span className="status-pill">Edited: {summary.edited}</span>
        {!isEditMode ? (
          <button type="button" className="btn secondary small" onClick={() => setIsEditMode(true)}>
            Edit Mode
          </button>
        ) : (
          <>
            <button type="button" className="btn small" onClick={handleSave} disabled={!hasUnsavedChanges}>
              Save Changes
            </button>
            <button type="button" className="btn ghost small" onClick={handleCancel}>
              Cancel
            </button>
          </>
        )}
      </div>
      {isEditMode && !hasUnsavedChanges ? (
        <div className="field-muted">Edit mode enabled. Update any field, then click Save Changes.</div>
      ) : null}
      <div className="table-wrap">
        <table className="data-table">
          <thead>
            <tr>
              <th className="select-col">
                <input
                  ref={selectAllRef}
                  type="checkbox"
                  checked={allSelectableSelected}
                  onChange={(event) => handleToggleSelectAll(event.target.checked)}
                  aria-label="Select all exportable test cases"
                />
              </th>
              <th>ID</th>
              <th>Title</th>
              <th>Preconditions</th>
              <th>Steps</th>
              <th>Expected Result</th>
              <th>Type</th>
              <th>Priority</th>
              {isEditMode ? <th>Diff</th> : null}
            </tr>
          </thead>
          <tbody>
            {draftCases.map((item, caseIndex) => {
              const rowKey = item.test_case_id || `${caseIndex}`;
              const normalizedTestCaseId = String(item?.test_case_id || "").trim();
              const isRejected = String(item?.review_status || "approved").toLowerCase() === "rejected";
              const isRowSelectable = Boolean(normalizedTestCaseId) && !isRejected;
              const diffRows = getDiffRows(caseIndex);
              const showDiff = Boolean(openDiffRows[rowKey]);
              const colSpan = isEditMode ? 9 : 8;
              return (
                <Fragment key={rowKey}>
                  <tr key={rowKey} style={{ "--row-index": caseIndex }}>
                    <td className="select-col">
                      <input
                        type="checkbox"
                        checked={isRowSelectable && selectedIdSet.has(normalizedTestCaseId)}
                        disabled={!isRowSelectable}
                        onChange={(event) => handleToggleRowSelection(normalizedTestCaseId, event.target.checked)}
                        aria-label={`Select ${normalizedTestCaseId || "test case"}`}
                      />
                    </td>
                    <td>{item.test_case_id}</td>
                    <td>
                      {isEditMode ? (
                        <textarea
                          rows={3}
                          value={item.title || ""}
                          onChange={(event) => updateField(caseIndex, "title", event.target.value)}
                        />
                      ) : (
                        item.title
                      )}
                    </td>
                    <td>
                      {isEditMode ? (
                        <textarea
                          rows={3}
                          value={item.preconditions || ""}
                          onChange={(event) => updateField(caseIndex, "preconditions", event.target.value)}
                        />
                      ) : (
                        item.preconditions
                      )}
                    </td>
                    <td>
                      <ol>
                        {(item.steps || []).map((s, idx) => (
                          <li key={`${rowKey}-${idx}`} className={isEditMode ? "step-edit-item" : ""}>
                            {isEditMode ? (
                              <textarea
                                rows={2}
                                value={s}
                                onChange={(event) => updateStep(caseIndex, idx, event.target.value)}
                              />
                            ) : (
                              s
                            )}
                            {isEditMode ? (
                              <button
                                type="button"
                                className="btn ghost small icon-btn"
                                data-icon="remove"
                                onClick={() => removeStep(caseIndex, idx)}
                                disabled={(item.steps || []).length <= 1}
                                aria-label="Remove step"
                                title="Remove step"
                              >
                                Remove
                              </button>
                            ) : null}
                          </li>
                        ))}
                      </ol>
                      {isEditMode ? (
                        <button
                          type="button"
                          className="btn ghost small icon-btn"
                          data-icon="add"
                          onClick={() => addStep(caseIndex)}
                          aria-label="Add step"
                          title="Add step"
                        >
                          Add Step
                        </button>
                      ) : null}
                    </td>
                    <td>
                      {isEditMode ? (
                        <textarea
                          rows={3}
                          value={item.expected_result || ""}
                          onChange={(event) => updateField(caseIndex, "expected_result", event.target.value)}
                        />
                      ) : (
                        item.expected_result
                      )}
                    </td>
                    <td>
                      {isEditMode ? (
                        <input
                          value={item.test_type || ""}
                          onChange={(event) => updateField(caseIndex, "test_type", event.target.value)}
                        />
                      ) : (
                        <span className={`pill type-pill ${getTypeBadgeClass(item.test_type)}`}>
                          {item.test_type || "Unspecified"}
                        </span>
                      )}
                    </td>
                    <td>
                      {isEditMode ? (
                        <input
                          value={item.priority || ""}
                          onChange={(event) => updateField(caseIndex, "priority", event.target.value)}
                        />
                      ) : (
                        <span className={`pill priority-pill ${getPriorityBadgeClass(item.priority)}`}>
                          {item.priority || "Unspecified"}
                        </span>
                      )}
                    </td>
                    {isEditMode ? (
                      <td>
                        <button
                          type="button"
                          className="btn ghost small icon-btn"
                          data-icon="diff"
                          onClick={() => toggleDiff(rowKey)}
                          disabled={!diffRows.length}
                          aria-label={showDiff ? "Hide differences" : "View differences"}
                          title={showDiff ? "Hide differences" : "View differences"}
                        >
                          {showDiff ? "Hide Diff" : "View Diff"}
                        </button>
                      </td>
                    ) : null}
                  </tr>
                  {isEditMode && showDiff ? (
                    <tr>
                      <td colSpan={colSpan}>
                        {diffRows.length ? (
                          <div className="diff-panel">
                            {diffRows.map((row) => (
                              <div key={`${rowKey}-${row.field}`} className="diff-row">
                                <div className="diff-field">{row.field}</div>
                                <div className="diff-before">
                                  <strong>Before</strong>
                                  <pre>{row.before || "-"}</pre>
                                </div>
                                <div className="diff-after">
                                  <strong>After</strong>
                                  <pre>{row.after || "-"}</pre>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <span className="field-muted">No differences for this row.</span>
                        )}
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default TestCaseTable;
