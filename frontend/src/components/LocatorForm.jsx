import { useEffect, useMemo, useState } from "react";
import { buildModelSections, getModelOptions } from "../utils/modelOptions";

function LocatorForm({
  onSubmit,
  loading,
  models = [],
  defaultModelId = "",
  taskContext = "locator_generation"
}) {
  const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;
  const SUPPORTED_EXTENSIONS = [
    ".pdf", ".docx", ".txt", ".md", ".log", ".png", ".jpg", ".jpeg", ".gif", ".xml",
    ".json", ".yaml", ".yml", ".html", ".htm", ".rtf", ".csv", ".xlsx", ".xls", ".oc"
  ];
  const [dom, setDom] = useState("");
  const [framework, setFramework] = useState("Selenium");
  const [language, setLanguage] = useState("Python");
  const [customPrompt, setCustomPrompt] = useState("");
  const [attachmentFiles, setAttachmentFiles] = useState([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const [fileError, setFileError] = useState("");
  const [modelId, setModelId] = useState(defaultModelId || "gemini-2.5-flash");
  const [errors, setErrors] = useState({});
  const modelOptions = useMemo(() => getModelOptions(models), [models]);
  const modelSections = useMemo(
    () => buildModelSections(modelOptions, taskContext),
    [modelOptions, taskContext]
  );

  useEffect(() => {
    if (!modelOptions.length) {
      return;
    }
    const requested = defaultModelId || "gemini-2.5-flash";
    const exists = modelOptions.some((m) => m.id === requested);
    if (exists) {
      setModelId(requested);
      return;
    }
    setModelId(modelOptions[0].id);
  }, [defaultModelId, modelOptions]);

  const validate = () => {
    const next = {};
    if (!dom.trim() && !attachmentFiles.length) {
      next.dom = "Provide DOM content or upload at least one file.";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
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
    const errorsFound = [];
    incoming.forEach((file) => {
      if (!isSupportedFile(file.name)) {
        errorsFound.push(`${file.name}: unsupported format`);
        return;
      }
      if (file.size > MAX_FILE_SIZE_BYTES) {
        errorsFound.push(`${file.name}: exceeds 10MB`);
        return;
      }
      validFiles.push(file);
    });

    setAttachmentFiles((prev) => {
      const keys = new Set(prev.map((f) => `${f.name}-${f.size}-${f.lastModified}`));
      const deduped = validFiles.filter((f) => !keys.has(`${f.name}-${f.size}-${f.lastModified}`));
      return [...prev, ...deduped];
    });
    setFileError(errorsFound.length ? errorsFound.join("; ") : "");
  };

  const removeFile = (target) => {
    setAttachmentFiles((prev) => prev.filter((file) => `${file.name}-${file.size}-${file.lastModified}` !== target));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    onSubmit({
      dom: dom.trim(),
      framework,
      language,
      custom_prompt: customPrompt.trim(),
      model_id: modelId,
      attachment_files: attachmentFiles
    });
  };

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2 className="section-title">Generate Locators</h2>
      <div className="field">
        <label>Paste Page Source / DOM</label>
        <textarea
          rows={12}
          className="dom-input"
          value={dom}
          onChange={(e) => setDom(e.target.value)}
          placeholder="Paste full HTML page source or DOM structure here..."
        />
        {errors.dom ? <div className="field-note">{errors.dom}</div> : null}
      </div>

      <div className="field">
        <label className="label-with-info">
          <span>Upload Documents (Optional)</span>
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
            id="locator-attachments"
            type="file"
            multiple
            accept={SUPPORTED_EXTENSIONS.join(",")}
            onChange={(event) => addFiles(event.target.files)}
          />
          <label htmlFor="locator-attachments" className="btn ghost small dropzone-upload" role="button">
            Upload Files
          </label>
          <p className="dropzone-text">Upload files containing DOM/spec details for locator generation.</p>
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
          <label>Automation Framework</label>
          <select value={framework} onChange={(e) => setFramework(e.target.value)}>
            <option value="Selenium">Selenium</option>
            <option value="Playwright">Playwright</option>
          </select>
        </div>
        <div className="field">
          <label>Programming Language</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="TypeScript">TypeScript</option>
            <option value="Java">Java</option>
            <option value="Python">Python</option>
          </select>
        </div>
      </div>

      <div className="field">
        <label>Custom Locator Instructions (Optional)</label>
        <textarea
          rows={4}
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder="Example: Prefer data-testid attributes, avoid XPath unless necessary, prioritize CSS selectors, etc."
        />
      </div>

      <div className="actions-row inline">
        <button type="submit" className="btn" disabled={loading || (!dom.trim() && !attachmentFiles.length)}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
    </form>
  );
}

export default LocatorForm;
