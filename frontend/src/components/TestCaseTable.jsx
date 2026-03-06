import { Fragment, useEffect, useMemo, useState } from "react";

const editableFields = ["title", "preconditions", "expected_result", "test_type", "priority", "steps"];

const timestampNow = () => new Date().toISOString();
const DIFF_FIELDS = ["title", "preconditions", "expected_result", "test_type", "priority", "steps"];
const DUPLICATE_THRESHOLD = 0.72;

const normalizeText = (value = "") =>
  String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const tokenize = (value = "") => {
  const normalized = normalizeText(value);
  if (!normalized) {
    return [];
  }
  return normalized.split(" ").filter(Boolean);
};

const jaccardSimilarity = (left = "", right = "") => {
  const a = new Set(tokenize(left));
  const b = new Set(tokenize(right));
  if (!a.size || !b.size) {
    return 0;
  }
  let intersection = 0;
  a.forEach((token) => {
    if (b.has(token)) {
      intersection += 1;
    }
  });
  const union = new Set([...a, ...b]).size;
  return union ? intersection / union : 0;
};

const caseSignature = (item = {}) =>
  [
    item?.title || "",
    item?.preconditions || "",
    item?.expected_result || "",
    Array.isArray(item?.steps) ? item.steps.join(" ") : ""
  ].join(" ");

const stringifySteps = (steps = []) => (Array.isArray(steps) ? steps.join("\n") : "");

const normalizeCases = (cases = []) =>
  (Array.isArray(cases) ? cases : []).map((item) => ({
    ...item,
    review_status: item?.review_status || "approved",
    is_edited: Boolean(item?.is_edited),
    edited_fields: Array.isArray(item?.edited_fields) ? item.edited_fields : [],
    last_edited_at: item?.last_edited_at || "",
    last_edited_by: item?.last_edited_by || ""
  }));

function TestCaseTable({ testCases, onSave, onDirtyChange }) {
  const [baselineCases, setBaselineCases] = useState([]);
  const [draftCases, setDraftCases] = useState([]);
  const [isEditMode, setIsEditMode] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [openDiffRows, setOpenDiffRows] = useState({});

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

  const duplicates = useMemo(() => {
    const matches = [];
    for (let i = 0; i < draftCases.length; i += 1) {
      for (let j = i + 1; j < draftCases.length; j += 1) {
        const left = draftCases[i];
        const right = draftCases[j];
        const score = jaccardSimilarity(caseSignature(left), caseSignature(right));
        if (score >= DUPLICATE_THRESHOLD) {
          matches.push({
            leftId: left?.test_case_id || `#${i + 1}`,
            rightId: right?.test_case_id || `#${j + 1}`,
            score
          });
        }
      }
    }
    return matches.sort((a, b) => b.score - a.score);
  }, [draftCases]);

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
        <h3 className="section-title">Generated Test Cases ({draftCases.length})</h3>
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
      {duplicates.length ? (
        <div className="duplicate-warning">
          <strong>Potential duplicate test cases detected:</strong>
          <ul className="duplicate-list">
            {duplicates.slice(0, 6).map((item) => (
              <li key={`${item.leftId}-${item.rightId}`}>
                {item.leftId} and {item.rightId} are {(item.score * 100).toFixed(0)}% similar
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {isEditMode && !hasUnsavedChanges ? (
        <div className="field-muted">Edit mode enabled. Update any field, then click Save Changes.</div>
      ) : null}
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
              {isEditMode ? <th>Diff</th> : null}
            </tr>
          </thead>
          <tbody>
            {draftCases.map((item, caseIndex) => {
              const rowKey = item.test_case_id || `${caseIndex}`;
              const diffRows = getDiffRows(caseIndex);
              const showDiff = Boolean(openDiffRows[rowKey]);
              const colSpan = isEditMode ? 8 : 7;
              return (
                <Fragment key={rowKey}>
                  <tr key={rowKey}>
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
                                className="btn ghost small"
                                onClick={() => removeStep(caseIndex, idx)}
                                disabled={(item.steps || []).length <= 1}
                              >
                                Remove
                              </button>
                            ) : null}
                          </li>
                        ))}
                      </ol>
                      {isEditMode ? (
                        <button type="button" className="btn ghost small" onClick={() => addStep(caseIndex)}>
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
                        item.test_type
                      )}
                    </td>
                    <td>
                      {isEditMode ? (
                        <input
                          value={item.priority || ""}
                          onChange={(event) => updateField(caseIndex, "priority", event.target.value)}
                        />
                      ) : (
                        item.priority
                      )}
                    </td>
                    {isEditMode ? (
                      <td>
                        <button
                          type="button"
                          className="btn ghost small"
                          onClick={() => toggleDiff(rowKey)}
                          disabled={!diffRows.length}
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
