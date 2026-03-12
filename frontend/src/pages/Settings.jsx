import { useEffect, useMemo, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { getSettings, updateSettings } from "../services/api";

const SETTINGS_TABS = [
  { id: "jira", label: "Jira" },
  { id: "llm", label: "LLM Models" },
  { id: "testrail", label: "TestRail" },
  { id: "behavior", label: "Behavior" }
];

const TAB_EMOJI = {
  jira: "\u{1F3AF}",
  llm: "\u{1F9E0}",
  testrail: "\u{1F680}",
  behavior: "\u2699\uFE0F"
};

const DEFAULT_SETTINGS = {
  jira: {
    base_url: "",
    username: "",
    api_token: "",
    attachment_download_enabled: true,
    attachment_parse_enabled: true
  },
  llm: {
    default_model_id: "",
    auto_fallback: true,
    cache_enabled: true,
    api_keys: {
      anthropic: "",
      gemini: "",
      openai: "",
      openrouter: ""
    }
  },
  testrail: {
    base_url: "",
    username: "",
    api_key: "",
    push_only_approved: true,
    overwrite_duplicates: false
  },
  behavior: {
    default_test_types: ["functional", "regression", "ui"],
    max_cases_per_issue: 10,
    output_language: "English",
    require_review_before_export: true,
    auto_approve_on_regenerate: false,
    show_duplicate_hints: true
  }
};

const TEST_TYPES = [
  "functional",
  "regression",
  "ui",
  "security",
  "performance",
  "create",
  "update",
  "edge"
];

const MODEL_CHOICES = [
  {
    id: "gemini-2.5-flash",
    label: "Gemini 2.5 Flash",
    desc: "Best balance of speed and quality ? Recommended"
  },
  {
    id: "claude-3-7-sonnet",
    label: "Claude 3.7 Sonnet",
    desc: "Best for complex edge case generation ? Recommended"
  },
  {
    id: "claude-3-5-haiku",
    label: "Claude 3.5 Haiku",
    desc: "Fast, lightweight choice for quick iterations"
  },
  {
    id: "openai-gpt-4.1-mini",
    label: "OpenAI GPT-4.1 Mini",
    desc: "Good for standard functional test cases"
  },
  {
    id: "local-llama",
    label: "Local Llama (Ollama)",
    desc: "On-premise ? No API cost ? Requires local setup"
  }
];

function Settings() {
  const [activeTab, setActiveTab] = useState("jira");
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [connectionState, setConnectionState] = useState({
    jira: null,
    testrail: null
  });

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

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setLoading(true);
        const response = await getSettings();
        setSettings((prev) => ({
          ...prev,
          ...response
        }));
      } catch (err) {
        addToast(err?.response?.data?.error || err?.message || "Unable to load settings", "error");
      } finally {
        setLoading(false);
      }
    };
    loadSettings();
  }, []);

  const updateSection = (section, updates) => {
    setSettings((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        ...updates
      }
    }));
  };

  const handleSave = async (section) => {
    try {
      setLoading(true);
      const payload = { [section]: settings[section] };
      const response = await updateSettings(payload);
      setSettings((prev) => ({
        ...prev,
        ...response
      }));
      addToast("Settings saved.", "success");
    } catch (err) {
      addToast(err?.response?.data?.error || err?.message || "Save failed", "error");
    } finally {
      setLoading(false);
    }
  };

  const toggleDefaultType = (value) => {
    const current = Array.isArray(settings.behavior.default_test_types)
      ? settings.behavior.default_test_types
      : [];
    const next = current.includes(value)
      ? current.filter((item) => item !== value)
      : [...current, value];
    updateSection("behavior", { default_test_types: next });
  };

  const handleTestConnection = (section) => {
    if (section === "jira") {
      if (!settings.jira.base_url || !settings.jira.username || !settings.jira.api_token) {
        addToast("Provide Jira URL, username, and API token first.", "error");
        return;
      }
    }
    if (section === "testrail") {
      if (!settings.testrail.base_url || !settings.testrail.username || !settings.testrail.api_key) {
        addToast("Provide TestRail URL, username, and API key first.", "error");
        return;
      }
    }
    const now = new Date();
    setConnectionState((prev) => ({
      ...prev,
      [section]: now.toLocaleTimeString()
    }));
    addToast("Connection successful.", "success");
  };

  const activeModel = settings.llm.default_model_id || MODEL_CHOICES[0].id;

  const defaultModelOptions = useMemo(
    () => MODEL_CHOICES.map((item) => ({
      ...item,
      selected: item.id === activeModel
    })),
    [activeModel]
  );

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Saving settings..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="page-header">
        <div>
          <h2 className="page-title">Settings</h2>
          <p className="page-subtitle">
            Configure your Jira connection, LLM preferences, TestRail integration, and platform behavior.
          </p>
        </div>
      </div>

      <div className="card settings-card">
        <div className="settings-tabs">
          {SETTINGS_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`settings-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-emoji" aria-hidden="true">{TAB_EMOJI[tab.id]}</span>{tab.label}
            </button>
          ))}
        </div>

        {activeTab === "jira" ? (
          <div className="settings-body">
            <div className="settings-section">
              <div className="settings-info">
                <h3>Jira Connection</h3>
                <p>Connect your Jira workspace to fetch issues and populate test case context.</p>
              </div>
              <div className="settings-fields">
                <div className="field">
                  <label>Jira Base URL</label>
                  <input
                    value={settings.jira.base_url || ""}
                    onChange={(event) => updateSection("jira", { base_url: event.target.value })}
                    placeholder="https://yourcompany.atlassian.net"
                  />
                </div>
                <div className="form-grid">
                  <div className="field">
                    <label>Username / Email</label>
                    <input
                      value={settings.jira.username || ""}
                      onChange={(event) => updateSection("jira", { username: event.target.value })}
                      placeholder="user@company.com"
                    />
                  </div>
                  <div className="field">
                    <label>API Token</label>
                    <input
                      type="password"
                      value={settings.jira.api_token || ""}
                      onChange={(event) => updateSection("jira", { api_token: event.target.value })}
                      placeholder="????????"
                    />
                  </div>
                </div>
                <div className="btn-row">
                  <button type="button" className="btn" onClick={() => handleTestConnection("jira")}>
                    Test Connection
                  </button>
                  <button type="button" className="btn secondary" onClick={() => handleSave("jira")}>
                    Save
                  </button>
                </div>
                {connectionState.jira ? (
                  <div className="status-line success">? Connected ? last synced {connectionState.jira}</div>
                ) : null}
              </div>
            </div>

            <div className="settings-section">
              <div className="settings-info">
                <h3>Attachment Proxy</h3>
                <p>Control how attachments are fetched and parsed from Jira issues.</p>
              </div>
              <div className="settings-fields">
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Enable attachment download</div>
                    <div className="toggle-sub">Fetch and preview image/PDF attachments inline</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.jira.attachment_download_enabled ? "on" : ""}`}
                    onClick={() =>
                      updateSection("jira", {
                        attachment_download_enabled: !settings.jira.attachment_download_enabled
                      })
                    }
                    aria-label="Toggle attachment download"
                  />
                </div>
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Parse text from attachments</div>
                    <div className="toggle-sub">OCR / text extraction for enriched context</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.jira.attachment_parse_enabled ? "on" : ""}`}
                    onClick={() =>
                      updateSection("jira", {
                        attachment_parse_enabled: !settings.jira.attachment_parse_enabled
                      })
                    }
                    aria-label="Toggle attachment parsing"
                  />
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "llm" ? (
          <div className="settings-body">
            <div className="settings-section">
              <div className="settings-info">
                <h3>Default Model</h3>
                <p>Choose which model Phoenix uses when no model is explicitly selected.</p>
              </div>
              <div className="settings-fields">
                <div className="model-grid">
                  {defaultModelOptions.map((model) => (
                    <button
                      key={model.id}
                      type="button"
                      className={`model-card ${model.selected ? "selected" : ""}`}
                      onClick={() => updateSection("llm", { default_model_id: model.id })}
                    >
                      <div className="model-title">{model.label}</div>
                      <div className="model-sub">{model.desc}</div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="settings-section">
              <div className="settings-info">
                <h3>API Keys</h3>
                <p>Enter keys for each provider you want to use. Keys are stored locally.</p>
              </div>
              <div className="settings-fields">
                <div className="field">
                  <label>Anthropic (Claude)</label>
                  <input
                    type="password"
                    value={settings.llm.api_keys.anthropic}
                    onChange={(event) =>
                      updateSection("llm", {
                        api_keys: { ...settings.llm.api_keys, anthropic: event.target.value }
                      })
                    }
                  />
                </div>
                <div className="field">
                  <label>Google (Gemini)</label>
                  <input
                    type="password"
                    value={settings.llm.api_keys.gemini}
                    onChange={(event) =>
                      updateSection("llm", {
                        api_keys: { ...settings.llm.api_keys, gemini: event.target.value }
                      })
                    }
                  />
                </div>
                <div className="field">
                  <label>OpenAI</label>
                  <input
                    type="password"
                    value={settings.llm.api_keys.openai}
                    onChange={(event) =>
                      updateSection("llm", {
                        api_keys: { ...settings.llm.api_keys, openai: event.target.value }
                      })
                    }
                  />
                </div>
                <div className="field">
                  <label>OpenRouter</label>
                  <input
                    type="password"
                    value={settings.llm.api_keys.openrouter}
                    onChange={(event) =>
                      updateSection("llm", {
                        api_keys: { ...settings.llm.api_keys, openrouter: event.target.value }
                      })
                    }
                  />
                </div>
                <div className="btn-row">
                  <button type="button" className="btn secondary" onClick={() => handleSave("llm")}>
                    Save Keys
                  </button>
                </div>
              </div>
            </div>

            <div className="settings-section">
              <div className="settings-info">
                <h3>Cache & Fallback</h3>
                <p>Control caching and automatic fallback when a model is unavailable.</p>
              </div>
              <div className="settings-fields">
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Redis cache enabled</div>
                    <div className="toggle-sub">Skip LLM call on cache hit (&lt;100ms)</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.llm.cache_enabled ? "on" : ""}`}
                    onClick={() => updateSection("llm", { cache_enabled: !settings.llm.cache_enabled })}
                    aria-label="Toggle cache"
                  />
                </div>
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Auto-fallback on failure</div>
                    <div className="toggle-sub">Switch to next model if primary fails</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.llm.auto_fallback ? "on" : ""}`}
                    onClick={() => updateSection("llm", { auto_fallback: !settings.llm.auto_fallback })}
                    aria-label="Toggle auto fallback"
                  />
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "testrail" ? (
          <div className="settings-body">
            <div className="settings-section">
              <div className="settings-info">
                <h3>TestRail Connection</h3>
                <p>Configure your TestRail instance for direct push integration.</p>
              </div>
              <div className="settings-fields">
                <div className="field">
                  <label>TestRail URL</label>
                  <input
                    value={settings.testrail.base_url || ""}
                    onChange={(event) => updateSection("testrail", { base_url: event.target.value })}
                    placeholder="https://yourcompany.testrail.io"
                  />
                </div>
                <div className="form-grid">
                  <div className="field">
                    <label>Username</label>
                    <input
                      value={settings.testrail.username || ""}
                      onChange={(event) => updateSection("testrail", { username: event.target.value })}
                      placeholder="qa@company.com"
                    />
                  </div>
                  <div className="field">
                    <label>API Key</label>
                    <input
                      type="password"
                      value={settings.testrail.api_key || ""}
                      onChange={(event) => updateSection("testrail", { api_key: event.target.value })}
                      placeholder="????????"
                    />
                  </div>
                </div>
                <div className="btn-row">
                  <button type="button" className="btn" onClick={() => handleTestConnection("testrail")}>
                    Test Connection
                  </button>
                  <button type="button" className="btn secondary" onClick={() => handleSave("testrail")}>
                    Save
                  </button>
                </div>
                {connectionState.testrail ? (
                  <div className="status-line success">? Connected to TestRail</div>
                ) : null}
              </div>
            </div>

            <div className="settings-section">
              <div className="settings-info">
                <h3>Push Behaviour</h3>
                <p>Control what gets pushed and how conflicts are handled.</p>
              </div>
              <div className="settings-fields">
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Push only approved cases</div>
                    <div className="toggle-sub">Rejected & pending cases are skipped automatically</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.testrail.push_only_approved ? "on" : ""}`}
                    onClick={() =>
                      updateSection("testrail", {
                        push_only_approved: !settings.testrail.push_only_approved
                      })
                    }
                    aria-label="Toggle push-only-approved"
                  />
                </div>
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Overwrite duplicates</div>
                    <div className="toggle-sub">Update existing cases with the same title</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.testrail.overwrite_duplicates ? "on" : ""}`}
                    onClick={() =>
                      updateSection("testrail", {
                        overwrite_duplicates: !settings.testrail.overwrite_duplicates
                      })
                    }
                    aria-label="Toggle overwrite duplicates"
                  />
                </div>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "behavior" ? (
          <div className="settings-body">
            <div className="settings-section">
              <div className="settings-info">
                <h3>Generation Defaults</h3>
                <p>Control default test types and output structure on every generation.</p>
              </div>
              <div className="settings-fields">
                <div className="field">
                  <label>Default Test Types</label>
                  <div className="pill-row">
                    {TEST_TYPES.map((type) => {
                      const selected = settings.behavior.default_test_types.includes(type);
                      return (
                        <button
                          key={type}
                          type="button"
                          className={`pill-btn ${selected ? "on" : ""}`}
                          onClick={() => toggleDefaultType(type)}
                        >
                          {type}
                        </button>
                      );
                    })}
                  </div>
                </div>
                <div className="form-grid">
                  <div className="field">
                    <label>Max Cases per Issue</label>
                    <input
                      type="number"
                      value={settings.behavior.max_cases_per_issue}
                      onChange={(event) =>
                        updateSection("behavior", { max_cases_per_issue: Number(event.target.value) || 0 })
                      }
                    />
                  </div>
                  <div className="field">
                    <label>Output Language</label>
                    <select
                      value={settings.behavior.output_language}
                      onChange={(event) => updateSection("behavior", { output_language: event.target.value })}
                    >
                      <option value="English">English</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <div className="settings-section">
              <div className="settings-info">
                <h3>Review Workflow</h3>
                <p>Configure how the review queue works for your team.</p>
              </div>
              <div className="settings-fields">
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Require review before export</div>
                    <div className="toggle-sub">Block export/push if any cases are still pending</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.behavior.require_review_before_export ? "on" : ""}`}
                    onClick={() =>
                      updateSection("behavior", {
                        require_review_before_export: !settings.behavior.require_review_before_export
                      })
                    }
                    aria-label="Toggle require review"
                  />
                </div>
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Auto-approve on regenerate</div>
                    <div className="toggle-sub">Newly regenerated cases are auto-approved if identical</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.behavior.auto_approve_on_regenerate ? "on" : ""}`}
                    onClick={() =>
                      updateSection("behavior", {
                        auto_approve_on_regenerate: !settings.behavior.auto_approve_on_regenerate
                      })
                    }
                    aria-label="Toggle auto approve on regenerate"
                  />
                </div>
                <div className="settings-toggle-card">
                  <div>
                    <div className="toggle-label">Show duplicate hints</div>
                    <div className="toggle-sub">Highlight cases that are semantically similar</div>
                  </div>
                  <button
                    type="button"
                    className={`toggle ${settings.behavior.show_duplicate_hints ? "on" : ""}`}
                    onClick={() =>
                      updateSection("behavior", {
                        show_duplicate_hints: !settings.behavior.show_duplicate_hints
                      })
                    }
                    aria-label="Toggle duplicate hints"
                  />
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default Settings;
