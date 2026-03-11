import { useEffect, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { getSettings, updateSettings } from "../services/api";

const SETTINGS_TABS = [
  { id: "jira", label: "Jira" },
  { id: "llm", label: "LLM Models" },
  { id: "testrail", label: "TestRail" },
  { id: "behavior", label: "Behavior" }
];

const DEFAULT_SETTINGS = {
  jira: {
    base_url: "",
    username: "",
    attachment_download_enabled: true,
    attachment_parse_enabled: true
  },
  llm: {
    default_model_id: "",
    auto_fallback: true,
    cache_enabled: true
  },
  testrail: {
    base_url: "",
    username: "",
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

function Settings() {
  const [activeTab, setActiveTab] = useState("jira");
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
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

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Saving settings..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="page-header">
        <div>
          <h2 className="page-title">Settings</h2>
          <p className="page-subtitle">Manage Jira, LLM, and TestRail integrations.</p>
        </div>
      </div>

      <div className="card">
        <div className="settings-tabs">
          {SETTINGS_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`settings-tab ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "jira" ? (
          <div className="settings-section">
            <div className="settings-info">
              <h3>Jira Connection</h3>
              <p>Configure your Jira workspace to fetch issues and attachments.</p>
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
              <div className="field">
                <label>Username / Email</label>
                <input
                  value={settings.jira.username || ""}
                  onChange={(event) => updateSection("jira", { username: event.target.value })}
                  placeholder="user@company.com"
                />
              </div>
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Enable attachment download</div>
                  <div className="toggle-sub">Fetch attachments for preview and export context.</div>
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
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Parse text from attachments</div>
                  <div className="toggle-sub">Extract text from supported files for LLM context.</div>
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
              <div className="btn-row">
                <button type="button" className="btn secondary small" onClick={() => handleSave("jira")}>
                  Save Jira Settings
                </button>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "llm" ? (
          <div className="settings-section">
            <div className="settings-info">
              <h3>Default Model</h3>
              <p>Set the model Phoenix uses when no model is explicitly selected.</p>
            </div>
            <div className="settings-fields">
              <div className="field">
                <label>Default Model ID</label>
                <input
                  value={settings.llm.default_model_id || ""}
                  onChange={(event) => updateSection("llm", { default_model_id: event.target.value })}
                  placeholder="gemini-2.5-flash"
                />
              </div>
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Auto fallback</div>
                  <div className="toggle-sub">Switch to another model on failure.</div>
                </div>
                <button
                  type="button"
                  className={`toggle ${settings.llm.auto_fallback ? "on" : ""}`}
                  onClick={() => updateSection("llm", { auto_fallback: !settings.llm.auto_fallback })}
                  aria-label="Toggle auto fallback"
                />
              </div>
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Cache enabled</div>
                  <div className="toggle-sub">Skip LLM calls on cache hit.</div>
                </div>
                <button
                  type="button"
                  className={`toggle ${settings.llm.cache_enabled ? "on" : ""}`}
                  onClick={() => updateSection("llm", { cache_enabled: !settings.llm.cache_enabled })}
                  aria-label="Toggle cache"
                />
              </div>
              <div className="btn-row">
                <button type="button" className="btn secondary small" onClick={() => handleSave("llm")}>
                  Save LLM Settings
                </button>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "testrail" ? (
          <div className="settings-section">
            <div className="settings-info">
              <h3>TestRail Connection</h3>
              <p>Configure TestRail credentials and push behavior.</p>
            </div>
            <div className="settings-fields">
              <div className="field">
                <label>TestRail Base URL</label>
                <input
                  value={settings.testrail.base_url || ""}
                  onChange={(event) => updateSection("testrail", { base_url: event.target.value })}
                  placeholder="https://yourcompany.testrail.io"
                />
              </div>
              <div className="field">
                <label>Username</label>
                <input
                  value={settings.testrail.username || ""}
                  onChange={(event) => updateSection("testrail", { username: event.target.value })}
                  placeholder="qa@company.com"
                />
              </div>
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Push only approved cases</div>
                  <div className="toggle-sub">Skip rejected or pending cases automatically.</div>
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
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Overwrite duplicates</div>
                  <div className="toggle-sub">Update existing cases with the same title.</div>
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
              <div className="btn-row">
                <button type="button" className="btn secondary small" onClick={() => handleSave("testrail")}>
                  Save TestRail Settings
                </button>
              </div>
            </div>
          </div>
        ) : null}

        {activeTab === "behavior" ? (
          <div className="settings-section">
            <div className="settings-info">
              <h3>Generation Defaults</h3>
              <p>Control default test types and output structure.</p>
            </div>
            <div className="settings-fields">
              <div className="field">
                <label>Default Test Types</label>
                <div className="multi-select-list">
                  {TEST_TYPES.map((type) => (
                    <label key={type} className="multi-select-item">
                      <input
                        type="checkbox"
                        checked={settings.behavior.default_test_types.includes(type)}
                        onChange={() => toggleDefaultType(type)}
                      />
                      <span>{type}</span>
                    </label>
                  ))}
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
                  <input
                    value={settings.behavior.output_language}
                    onChange={(event) => updateSection("behavior", { output_language: event.target.value })}
                  />
                </div>
              </div>
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Require review before export</div>
                  <div className="toggle-sub">Block export/push while cases are pending.</div>
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
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Auto approve on regenerate</div>
                  <div className="toggle-sub">Auto-approve regenerated cases that match.</div>
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
              <div className="toggle-row">
                <div>
                  <div className="toggle-label">Show duplicate hints</div>
                  <div className="toggle-sub">Highlight semantically similar cases.</div>
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
              <div className="btn-row">
                <button type="button" className="btn secondary small" onClick={() => handleSave("behavior")}>
                  Save Behavior Settings
                </button>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default Settings;
