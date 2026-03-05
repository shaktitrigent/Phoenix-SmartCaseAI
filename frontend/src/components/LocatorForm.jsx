import { useEffect, useMemo, useState } from "react";
import { buildModelSections, getModelOptions } from "../utils/modelOptions";

function LocatorForm({
  onSubmit,
  loading,
  models = [],
  defaultModelId = "",
  taskContext = "locator_generation"
}) {
  const [dom, setDom] = useState("");
  const [framework, setFramework] = useState("Selenium");
  const [language, setLanguage] = useState("Python");
  const [customPrompt, setCustomPrompt] = useState("");
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
    if (!dom.trim()) {
      next.dom = "DOM content is required.";
    }
    setErrors(next);
    return Object.keys(next).length === 0;
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
      model_id: modelId
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
        <button type="submit" className="btn" disabled={loading || !dom.trim()}>
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>
    </form>
  );
}

export default LocatorForm;
