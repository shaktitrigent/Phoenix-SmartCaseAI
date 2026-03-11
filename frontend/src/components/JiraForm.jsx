import { useEffect, useMemo, useState } from "react";
import { buildModelSections, getModelOptions } from "../utils/modelOptions";

const ALL_TYPES = ["functional", "regression", "ui", "security", "performance", "create", "update", "edge"];
const DEFAULT_JIRA_FIELDS = [
  "summary",
  "description",
  "acceptance_criteria",
  "attachments",
  "custom_fields",
  "issue_type"
];
const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
const BASE_UPLOAD_FORMATS = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".xml", ".csv", ".xlsx"];
const MORE_UPLOAD_FORMATS = [".json", ".md", ".log", ".yaml", ".yml", ".html", ".htm", ".rtf", ".xls", ".oc"];
const SUPPORTED_EXTENSIONS = [...BASE_UPLOAD_FORMATS, ...MORE_UPLOAD_FORMATS];

function JiraForm({
  mode = "jira",
  onSubmit,
  loading,
  models = [],
  defaultModelId = "",
  taskContext = "test_case_generation"
}) {
  const [issueKey, setIssueKey] = useState("");
  const [description, setDescription] = useState("");
  const [acceptanceCriteria, setAcceptanceCriteria] = useState("");
  const [customPrompt, setCustomPrompt] = useState("");
  const [attachmentFiles, setAttachmentFiles] = useState([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const [fileError, setFileError] = useState("");
  const [testTypes, setTestTypes] = useState(["functional", "regression", "ui"]);
  const [includeFields, setIncludeFields] = useState(DEFAULT_JIRA_FIELDS);
  const [modelId, setModelId] = useState(defaultModelId || "gemini-2.5-flash");
  const modelOptions = useMemo(() => getModelOptions(models), [models]);
  const modelSections = useMemo(
    () => buildModelSections(modelOptions, taskContext),
    [modelOptions, taskContext]
  );

  useEffect(() => {
    if (!models.length) {
      return;
    }
    const requested = defaultModelId || "gemini-2.5-flash";
    const exists = modelOptions.some((m) => m.id === requested);
    if (exists) {
      setModelId(requested);
      return;
    }
    setModelId(modelOptions[0].id);
  }, [defaultModelId, modelOptions, models.length]);

  const toggleTestType = (value) => {
    setTestTypes((prev) => (prev.includes(value) ? prev.filter((type) => type !== value) : [...prev, value]));
  };
  const toggleIncludeField = (value) => {
    setIncludeFields((prev) => (prev.includes(value) ? prev.filter((field) => field !== value) : [...prev, value]));
  };

  const isSupportedFile = (name = "") => {
    const lower = name.toLowerCase();
    return SUPPORTED_EXTENSIONS.some((ext) => lower.endsWith(ext));
  };

  const addFiles = (files) => {
    const incoming = Array.from(files || []);
    if (!incoming.length) {
      return;
    }

    const validFiles = [];
    const errors = [];

    incoming.forEach((file) => {
      if (!isSupportedFile(file.name)) {
        errors.push(`${file.name}: unsupported format`);
        return;
      }
      if (file.size > MAX_FILE_SIZE_BYTES) {
        errors.push(`${file.name}: exceeds 10MB`);
        return;
      }
      validFiles.push(file);
    });

    setAttachmentFiles((prev) => {
      const keys = new Set(prev.map((f) => `${f.name}-${f.size}-${f.lastModified}`));
      const deduped = validFiles.filter((f) => !keys.has(`${f.name}-${f.size}-${f.lastModified}`));
      return [...prev, ...deduped];
    });
    setFileError(errors.length ? errors.join("; ") : "");
  };

  const removeFile = (target) => {
    setAttachmentFiles((prev) => prev.filter((file) => `${file.name}-${file.size}-${file.lastModified}` !== target));
  };

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
      custom_prompt: customPrompt.trim(),
      include_fields: includeFields,
      attachments_text: "",
      attachment_files: attachmentFiles,
      test_types: testTypes,
      model_id: modelId
    });
  };

  const hasManualContent = Boolean(
    description.trim() || acceptanceCriteria.trim() || customPrompt.trim() || attachmentFiles.length
  );

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2 className="section-title">{mode === "jira" ? "Generate From Jira Issue" : "Generate From Manual Input"}</h2>
      {mode === "jira" ? (
        <>
          <div className="field">
            <label>Jira Issue Key</label>
            <div className="input-with-icon jira-key">
              <span className="input-icon" aria-hidden="true" />
              <input
                className="jira-input"
                value={issueKey}
                onChange={(e) => setIssueKey(e.target.value)}
                placeholder="PROJ-123"
              />
            </div>
          </div>
          <div className="field">
            <details className="collapsible prompt-collapsible">
              <summary>Custom Prompt (Optional)</summary>
              <textarea
                rows={4}
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Add any additional instructions for generation."
              />
            </details>
          </div>
          <div className="field">
            <label>Jira Fields to Include</label>
            <details className="multi-select">
              <summary className="multi-select-summary">
                {includeFields.length ? includeFields.join(", ") : "Select fields"}
              </summary>
              <div className="multi-select-list">
                {DEFAULT_JIRA_FIELDS.map((field) => (
                  <label key={field} className="multi-select-item">
                    <input
                      type="checkbox"
                      checked={includeFields.includes(field)}
                      onChange={() => toggleIncludeField(field)}
                    />
                    <span>{field}</span>
                  </label>
                ))}
              </div>
            </details>
            {!includeFields.length ? <div className="field-note">Select at least one field.</div> : null}
          </div>
        </>
      ) : (
        <>
          <div className="field">
            <label>Description</label>
            <textarea
              rows={5}
              className="mono-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Feature description..."
            />
          </div>
          <div className="field">
            <label>Acceptance Criteria</label>
            <textarea
              rows={4}
              className="mono-textarea"
              value={acceptanceCriteria}
              onChange={(e) => setAcceptanceCriteria(e.target.value)}
              placeholder="Given/When/Then or bullet list..."
            />
          </div>
          <div className="field">
            <details className="collapsible prompt-collapsible">
              <summary>Custom Prompt (Optional)</summary>
              <textarea
                rows={4}
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Add any additional instructions for generation."
              />
            </details>
          </div>
          <div className="field">
            <label className="label-with-info">
              <span>Attachments</span>
              <span className="info-wrap">
                <span className="info-icon" aria-label="Supported document formats" tabIndex={0}>
                  i
                </span>
                <span className="info-tooltip" role="tooltip">
                  Supported formats: PDF, DOCX, TXT, PNG, JPG, JPEG, GIF, XML, CSV, XLSX, JSON, MD, LOG, YAML,
                  YML, HTML, HTM, RTF, XLS, OC
                </span>
              </span>
            </label>
            <div
              className={`dropzone ${isDragActive ? "drag-active" : ""}`}
              onDragOver={(event) => {
                event.preventDefault();
                setIsDragActive(true);
              }}
              onDragLeave={(event) => {
                event.preventDefault();
                setIsDragActive(false);
              }}
              onDrop={(event) => {
                event.preventDefault();
                setIsDragActive(false);
                addFiles(event.dataTransfer?.files);
              }}
            >
              <input
                id="manual-attachments"
                type="file"
                multiple
                accept={SUPPORTED_EXTENSIONS.join(",")}
                onChange={(event) => addFiles(event.target.files)}
              />
              <label htmlFor="manual-attachments" className="btn ghost small dropzone-upload" role="button">
                Upload Files
              </label>
              <p className="dropzone-text">Drag and drop files here, or use Upload Files.</p>
            </div>
            {fileError ? <div className="field-note">{fileError}</div> : null}
            {attachmentFiles.length ? (
              <div className="uploaded-files">
                {attachmentFiles.map((file) => {
                  const key = `${file.name}-${file.size}-${file.lastModified}`;
                  return (
                    <div key={key} className="uploaded-file-row">
                      <span>{file.name}</span>
                      <span>{Math.max(1, Math.round(file.size / 1024))} KB</span>
                      <button type="button" className="btn ghost small" onClick={() => removeFile(key)}>
                        Remove
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : null}
          </div>
        </>
      )}

      <div className="form-grid">
        <div className="field">
          <label>LLM Model</label>
          <select value={modelId} onChange={(e) => setModelId(e.target.value)}>
            {modelSections.recommended.length ? (
              <optgroup label={modelSections.recommendedTitle}>
                {modelSections.recommended.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.displayLabel}
                  </option>
                ))}
              </optgroup>
            ) : null}
            {modelSections.openrouter.length ? (
              <optgroup label="OpenRouter Models">
                {modelSections.openrouter.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.displayLabel}
                  </option>
                ))}
              </optgroup>
            ) : null}
            {modelSections.others.length ? (
              <optgroup label="Other Models">
                {modelSections.others.map((model) => (
                  <option key={model.id} value={model.id}>
                    {model.displayLabel}
                  </option>
                ))}
              </optgroup>
            ) : null}
          </select>
        </div>
        <div className="field">
          <label>Test Types</label>
          <details className="multi-select">
            <summary className="multi-select-summary">{testTypes.length ? testTypes.join(", ") : "Select test types"}</summary>
            <div className="multi-select-list">
              {ALL_TYPES.map((t) => (
                <label key={t} className="multi-select-item">
                  <input type="checkbox" checked={testTypes.includes(t)} onChange={() => toggleTestType(t)} />
                  <span>{t}</span>
                </label>
              ))}
            </div>
          </details>
          {!testTypes.length ? <div className="field-note">Select at least one test type.</div> : null}
        </div>
      </div>

      <div className="inline actions-row">
        <button
          type="submit"
          className="btn primary-cta"
          disabled={
            loading ||
            (mode === "jira" && (!issueKey.trim() || !includeFields.length)) ||
            (mode === "manual" && !hasManualContent)
          }
        >
          {loading ? "Generating..." : "Generate Test Cases"}
        </button>
      </div>
      {mode === "manual" && !hasManualContent ? (
        <div className="field-note">Provide description, acceptance criteria, custom prompt, or attachments to continue.</div>
      ) : null}
    </form>
  );
}

export default JiraForm;
