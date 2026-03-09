import { useEffect, useState } from "react";
import ExportButtons from "../components/ExportButtons";
import IssueDataPanel from "../components/IssueDataPanel";
import JiraForm from "../components/JiraForm";
import LoadingOverlay from "../components/LoadingOverlay";
import LocatorForm from "../components/LocatorForm";
import LocatorResults from "../components/LocatorResults";
import TestCaseTable from "../components/TestCaseTable";
import ToastStack from "../components/ToastStack";
import {
  exportTestCases,
  generateFromJira,
  generateLocators,
  getLLMModels,
  manualGenerateTest,
  submitReviewedTestCases,
  pushToTestRail
} from "../services/api";

const TABS = [
  { id: "jira", label: "Jira Issue" },
  { id: "manual", label: "Manual Input" },
  { id: "locators", label: "Generate Locators" }
];
const THEME_KEY = "qa-automation-suite-theme";

const buildExportableCaseIds = (cases = []) =>
  (Array.isArray(cases) ? cases : [])
    .filter((item) => String(item?.review_status || "approved").toLowerCase() !== "rejected")
    .map((item) => String(item?.test_case_id || "").trim())
    .filter(Boolean);

function Home() {
  const [activeTab, setActiveTab] = useState("jira");
  const [loading, setLoading] = useState(false);
  const [pushLoading, setPushLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [locatorsLoading, setLocatorsLoading] = useState(false);
  const [issueKey, setIssueKey] = useState("");
  const [sourceData, setSourceData] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [reviewedTestCases, setReviewedTestCases] = useState([]);
  const [hasPendingEdits, setHasPendingEdits] = useState(false);
  const [models, setModels] = useState([]);
  const [defaultModelId, setDefaultModelId] = useState("gemini-2.5-flash");
  const [modelUsed, setModelUsed] = useState("");
  const [locatorResult, setLocatorResult] = useState(null);
  const [locatorLanguage, setLocatorLanguage] = useState("Python");
  const [toasts, setToasts] = useState([]);
  const [testrailLinks, setTestrailLinks] = useState([]);
  const [testrailSectionUrl, setTestrailSectionUrl] = useState("");
  const [selectedCaseIds, setSelectedCaseIds] = useState([]);
  const [testRailConfig, setTestRailConfig] = useState({
    project_id: "",
    suite_id: "",
    section_id: ""
  });
  const exportableCaseIds = buildExportableCaseIds(reviewedTestCases);
  const exportableCount = exportableCaseIds.length;
  const selectedExportableCaseIds = exportableCaseIds.filter((id) => selectedCaseIds.includes(id));
  const [theme, setTheme] = useState(() => {
    if (typeof window === "undefined") {
      return "light";
    }
    const stored = window.localStorage.getItem(THEME_KEY);
    if (stored === "light" || stored === "dark") {
      return stored;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
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
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await getLLMModels();
        setModels(Array.isArray(response?.models) ? response.models : []);
        setDefaultModelId(response?.default_model_id || "gemini-2.5-flash");
      } catch {
        setModels([]);
        setDefaultModelId("gemini-2.5-flash");
      }
    };
    loadModels();
  }, []);

  const handleSubmit = async (payload) => {
    try {
      setLoading(true);
      setTestrailLinks([]);
      setTestrailSectionUrl("");

      const response =
        payload.mode === "jira"
          ? await generateFromJira({
              issue_key: payload.issue_key,
              test_types: payload.test_types,
              model_id: payload.model_id
            })
          : await manualGenerateTest({
              description: payload.description,
              acceptance_criteria: payload.acceptance_criteria,
              custom_prompt: payload.custom_prompt,
              attachments_text: payload.attachments_text,
              attachment_files: payload.attachment_files,
              test_types: payload.test_types,
              model_id: payload.model_id
            });

      setIssueKey(response.issue_key || "");
      setSourceData(response.source_data || null);
      const generatedCases = response.test_cases || [];
      setTestCases(generatedCases);
      setReviewedTestCases(generatedCases);
      setSelectedCaseIds(buildExportableCaseIds(generatedCases));
      setHasPendingEdits(false);
      setModelUsed(response.model_used || "");
      addToast("Test cases generated successfully.", "success");
    } catch (err) {
      const message = err?.response?.data?.error || err.message || "Request failed";
      setTestCases([]);
      setReviewedTestCases([]);
      setSelectedCaseIds([]);
      setHasPendingEdits(false);
      addToast(message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    try {
      setExportLoading(true);
      if (reviewedTestCases.length) {
        await submitReviewedTestCases(reviewedTestCases);
      }
      const formatsToExport = format === "all" ? ["excel", "pdf", "gherkin", "plain"] : [format];

      for (const exportFormat of formatsToExport) {
        const { blob, filename } = await exportTestCases(exportFormat);
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = blobUrl;
        link.download = filename || `generated_test_cases.${exportFormat}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(blobUrl);
      }
      addToast(`Exported ${format === "all" ? "all formats" : format.toUpperCase()} successfully.`, "success");
    } catch (err) {
      let message = err?.message || "Export failed";
      if (err?.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const parsed = JSON.parse(text);
          message = parsed?.error || message;
        } catch {
          message = message || "Export failed";
        }
      } else if (err?.response?.data?.error) {
        message = err.response.data.error;
      }
      addToast(message, "error");
    } finally {
      setExportLoading(false);
    }
  };

  const handlePushToTestRail = async (repositoryMode, config = {}) => {
    try {
      if (!selectedExportableCaseIds.length) {
        addToast("Select at least one test case to push to TestRail.", "error");
        return;
      }
      setPushLoading(true);
      if (reviewedTestCases.length) {
        await submitReviewedTestCases(reviewedTestCases);
      }
      const result = await pushToTestRail({
        repository_mode: repositoryMode,
        project_id: String(config.project_id || "").trim(),
        suite_id: String(config.suite_id || "").trim(),
        section_id: String(config.section_id || "").trim(),
        selected_test_case_ids: selectedExportableCaseIds
      });
      const created = Number(result?.created || 0);
      const links = Array.isArray(result?.results)
        ? result.results
            .map((item) => ({
              id: item?.id,
              title: item?.title || `Test Case ${item?.id || ""}`,
              url: item?.case_url || ""
            }))
            .filter((item) => item.url)
        : [];
      setTestrailLinks(links);
      setTestrailSectionUrl(result?.section_url || "");
      addToast(`Push completed: ${created} case(s) created.`, "success");
    } catch (err) {
      const message = err?.response?.data?.error || err.message || "TestRail push failed";
      setTestrailLinks([]);
      setTestrailSectionUrl("");
      addToast(message, "error");
    } finally {
      setPushLoading(false);
    }
  };

  const handleGenerateLocators = async (payload) => {
    try {
      setLocatorsLoading(true);
      const response = await generateLocators(payload);
      setLocatorResult({
        locators: response?.locators || [],
        test_function: response?.test_function || "",
        automation_script: response?.automation_script || response?.test_template || ""
      });
      setModelUsed(response?.model_used || "");
      setLocatorLanguage(payload.language);
      addToast("Locators generated successfully.", "success");
    } catch (err) {
      const message = err?.response?.data?.error || err.message || "Locator generation failed";
      addToast(message, "error");
    } finally {
      setLocatorsLoading(false);
    }
  };

  const handleThemeToggle = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    window.localStorage.setItem(THEME_KEY, nextTheme);
  };

  const handleTestRailConfigChange = (field, value) => {
    setTestRailConfig((prev) => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTestCasesChange = (cases) => {
    const normalized = Array.isArray(cases) ? cases : [];
    setReviewedTestCases(normalized);
    const nextExportableIds = buildExportableCaseIds(normalized);
    setSelectedCaseIds((prev) => {
      const prevSet = new Set((Array.isArray(prev) ? prev : []).map((item) => String(item).trim()));
      const retained = nextExportableIds.filter((id) => prevSet.has(id));
      return retained.length ? retained : nextExportableIds;
    });
  };

  return (
    <main className="app-shell">
      <LoadingOverlay show={loading || exportLoading || pushLoading || locatorsLoading} label="Processing request..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <nav className="top-nav">
        <div className="brand-wrap">
          <h1>QA Automation Suite</h1>
          <p>Fetch Issues -&gt; Generate Intelligent Test Cases -&gt; Push to TestRail</p>
        </div>
        <button type="button" className="btn ghost small theme-toggle" onClick={handleThemeToggle}>
          {theme === "dark" ? "Light Mode" : "Dark Mode"}
        </button>
      </nav>

      <section className="workspace">
        <div className="tabs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeTab === "locators" ? (
          <>
            <LocatorForm
              onSubmit={handleGenerateLocators}
              loading={locatorsLoading}
              models={models}
              defaultModelId={defaultModelId}
              taskContext="locator_generation"
            />
            {modelUsed ? <div className="info-chip">Model used: {modelUsed}</div> : null}
            <LocatorResults data={locatorResult} language={locatorLanguage} />
          </>
        ) : (
          <>
            <JiraForm
              mode={activeTab}
              onSubmit={handleSubmit}
              loading={loading}
              models={models}
              defaultModelId={defaultModelId}
              taskContext="test_case_generation"
            />
            {issueKey && testCases.length ? <div className="info-chip">Last generated for: {issueKey}</div> : null}
            {modelUsed ? <div className="info-chip">Model used: {modelUsed}</div> : null}
            <IssueDataPanel sourceData={sourceData} />
            <ExportButtons
              exportDisabled={!exportableCount || hasPendingEdits}
              pushDisabled={!selectedExportableCaseIds.length || hasPendingEdits}
              onPushToTestRail={handlePushToTestRail}
              pushLoading={pushLoading}
              onExport={handleExport}
              exportLoading={exportLoading}
              testRailConfig={testRailConfig}
              onTestRailConfigChange={handleTestRailConfigChange}
            />
            {exportableCount ? (
              <div className="info-chip">
                Selected for TestRail push: {selectedExportableCaseIds.length} / {exportableCount}
              </div>
            ) : null}
            {(testrailLinks.length > 0 || testrailSectionUrl) && (
              <div className="card">
                <h3 className="section-title">Open In TestRail</h3>
                {testrailSectionUrl ? (
                  <div className="inline">
                    <a className="btn secondary" href={testrailSectionUrl} target="_blank" rel="noreferrer">
                      Open TestRail Section
                    </a>
                  </div>
                ) : null}
                {testrailLinks.length ? (
                  <ul className="testrail-links-list">
                    {testrailLinks.map((item) => (
                      <li key={`${item.id}-${item.url}`}>
                        <a className="testrail-link" href={item.url} target="_blank" rel="noreferrer">
                          {`C${item.id}: ${item.title}`}
                        </a>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            )}
            {hasPendingEdits ? <div className="info-chip">Save changes before export or TestRail push.</div> : null}
            <TestCaseTable
              testCases={reviewedTestCases}
              onSave={handleTestCasesChange}
              onDirtyChange={setHasPendingEdits}
              selectedCaseIds={selectedCaseIds}
              onSelectionChange={setSelectedCaseIds}
            />
          </>
        )}
      </section>
    </main>
  );
}

export default Home;
