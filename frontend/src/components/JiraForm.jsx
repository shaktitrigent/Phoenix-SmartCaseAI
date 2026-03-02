import { useState } from "react";

const ALL_TYPES = ["positive", "negative", "edge", "create", "update"];

function JiraForm({ onSubmit, onPreview, loading, previewLoading }) {
  const [mode, setMode] = useState("jira");
  const [issueKey, setIssueKey] = useState("");
  const [description, setDescription] = useState("");
  const [acceptanceCriteria, setAcceptanceCriteria] = useState("");
  const [attachmentsText, setAttachmentsText] = useState("");
  const [testTypes, setTestTypes] = useState(["positive", "negative", "edge"]);

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!testTypes.length) {
      return;
    }
    onSubmit({
      mode,
      issue_key: issueKey.trim(),
      description: description.trim(),
      acceptance_criteria: acceptanceCriteria.trim(),
      attachments_text: attachmentsText.trim(),
      test_types: testTypes
    });
  };

  const toggleTestType = (value) => {
    setTestTypes((prev) =>
      prev.includes(value) ? prev.filter((type) => type !== value) : [...prev, value]
    );
  };

  const handlePreview = () => {
    if (!issueKey.trim() || !onPreview) {
      return;
    }
    onPreview(issueKey.trim());
  };

  return (
    <form className="panel" onSubmit={handleSubmit}>
      <h2>Generate Test Cases</h2>
      <div className="inline">
        <label>
          <input
            type="radio"
            checked={mode === "jira"}
            onChange={() => setMode("jira")}
          />
          Jira Issue
        </label>
        <label>
          <input
            type="radio"
            checked={mode === "manual"}
            onChange={() => setMode("manual")}
          />
          Manual Input
        </label>
      </div>

      {mode === "jira" ? (
        <div className="field">
          <label>Jira Issue Key</label>
          <input
            value={issueKey}
            onChange={(e) => setIssueKey(e.target.value)}
            placeholder="PROJ-123"
          />
        </div>
      ) : (
        <>
          <div className="field">
            <label>Description</label>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Feature description..."
            />
          </div>
          <div className="field">
            <label>Acceptance Criteria</label>
            <textarea
              rows={3}
              value={acceptanceCriteria}
              onChange={(e) => setAcceptanceCriteria(e.target.value)}
              placeholder="Given/When/Then or bullet list..."
            />
          </div>
          <div className="field">
            <label>Attachment Extracted Text</label>
            <textarea
              rows={3}
              value={attachmentsText}
              onChange={(e) => setAttachmentsText(e.target.value)}
              placeholder="Paste parsed attachment content..."
            />
          </div>
        </>
      )}

      <div className="field">
        <label>Test Types</label>
        <details className="multi-select">
          <summary className="multi-select-summary">
            {testTypes.length ? testTypes.join(", ") : "Select test types"}
          </summary>
          <div className="multi-select-list">
            {ALL_TYPES.map((t) => (
              <label key={t} className="multi-select-item">
                <input
                  type="checkbox"
                  checked={testTypes.includes(t)}
                  onChange={() => toggleTestType(t)}
                />
                <span>{t}</span>
              </label>
            ))}
          </div>
        </details>
        {!testTypes.length ? <div className="field-note">Select at least one test type.</div> : null}
      </div>

      <div className="inline actions-row">
        {mode === "jira" ? (
          <button
            type="button"
            className="btn ghost"
            disabled={loading || previewLoading || !issueKey.trim()}
            onClick={handlePreview}
          >
            {previewLoading ? "Loading Attachments..." : "Preview Attachments"}
          </button>
        ) : null}

        <button type="submit" className="btn" disabled={loading || previewLoading}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
    </form>
  );
}

export default JiraForm;
