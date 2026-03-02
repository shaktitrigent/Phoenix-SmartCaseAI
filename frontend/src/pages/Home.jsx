import { useEffect, useState } from "react";
import ExportButtons from "../components/ExportButtons";
import IssueDataPanel from "../components/IssueDataPanel";
import JiraForm from "../components/JiraForm";
import TestCaseTable from "../components/TestCaseTable";
import { generateFromJira, manualGenerateTest, previewJira, pushToTestRail } from "../services/api";

const THEME_KEY = "jira-ui-theme";

function Home() {
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState("");
  const [testrailMessage, setTestrailMessage] = useState("");
  const [testrailError, setTestrailError] = useState("");
  const [testrailLinks, setTestrailLinks] = useState([]);
  const [testrailSectionUrl, setTestrailSectionUrl] = useState("");
  const [pushLoading, setPushLoading] = useState(false);
  const [issueKey, setIssueKey] = useState("");
  const [sourceData, setSourceData] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [previewReady, setPreviewReady] = useState(false);
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

  const handleThemeToggle = () => {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    window.localStorage.setItem(THEME_KEY, nextTheme);
  };

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const handleSubmit = async (payload) => {
    try {
      setLoading(true);
      setError("");
      setTestrailMessage("");
      setTestrailError("");
      setTestrailLinks([]);
      setTestrailSectionUrl("");

      let response;
      if (payload.mode === "jira") {
        response = await generateFromJira({
          issue_key: payload.issue_key,
          test_types: payload.test_types
        });
      } else {
        response = await manualGenerateTest({
          description: payload.description,
          acceptance_criteria: payload.acceptance_criteria,
          attachments_text: payload.attachments_text,
          test_types: payload.test_types
        });
      }

      setIssueKey(response.issue_key || "");
      setSourceData(response.source_data || null);
      setTestCases(response.test_cases || []);
      setPreviewReady(false);
    } catch (err) {
      const apiMessage = err?.response?.data?.error || err.message || "Request failed";
      setError(apiMessage);
      setTestCases([]);
    } finally {
      setLoading(false);
    }
  };

  const handlePreview = async (jiraIssueKey) => {
    try {
      setPreviewLoading(true);
      setError("");
      setTestrailMessage("");
      setTestrailError("");
      setTestrailLinks([]);
      setTestrailSectionUrl("");
      const response = await previewJira({ issue_key: jiraIssueKey });
      setIssueKey(response.issue_key || jiraIssueKey);
      setSourceData(response.source_data || null);
      setTestCases([]);
      setPreviewReady(true);
    } catch (err) {
      const apiMessage = err?.response?.data?.error || err.message || "Preview failed";
      setError(apiMessage);
      setIssueKey("");
      setTestCases([]);
      setPreviewReady(false);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handlePushToTestRail = async () => {
    try {
      setPushLoading(true);
      setTestrailMessage("");
      setTestrailError("");
      setTestrailLinks([]);
      setTestrailSectionUrl("");

      const result = await pushToTestRail({});
      const mode = result?.mode === "live" ? "Live" : "Mock";
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
      setTestrailMessage(`${mode} TestRail push completed. ${created} test case(s) created.`);
    } catch (err) {
      const apiMessage = err?.response?.data?.error || err.message || "TestRail push failed";
      setTestrailError(apiMessage);
      setTestrailLinks([]);
      setTestrailSectionUrl("");
    } finally {
      setPushLoading(false);
    }
  };

  return (
    <main className="container">
      <header className="hero">
        <div className="hero-top">
          <div>
            <h1>Jira to Test Case Generator</h1>
            <p>
              Convert Jira ticket content into structured, ready-to-execute QA test cases.
            </p>
          </div>
          <button type="button" className="btn ghost small" onClick={handleThemeToggle}>
            {theme === "dark" ? "Switch to Light" : "Switch to Dark"}
          </button>
        </div>
      </header>

      <JiraForm
        onSubmit={handleSubmit}
        onPreview={handlePreview}
        loading={loading}
        previewLoading={previewLoading}
      />

      {error ? <div className="error">{error}</div> : null}
      {issueKey && testCases.length ? (
        <div className="hint">Last generated for: {issueKey}</div>
      ) : null}
      {issueKey && previewReady && !testCases.length ? (
        <div className="hint">
          {`Preview loaded for: ${issueKey}. Verify attachments, then click Generate.`}
        </div>
      ) : null}

      <IssueDataPanel sourceData={sourceData} />
      <ExportButtons
        disabled={!testCases.length}
        onPushToTestRail={handlePushToTestRail}
        pushLoading={pushLoading}
      />
      {testrailMessage ? <div className="success">{testrailMessage}</div> : null}
      {testrailError ? <div className="error">{testrailError}</div> : null}
      {testrailLinks.length || testrailSectionUrl ? (
        <div className="panel testrail-links-panel">
          <h3>Open In TestRail</h3>
          {testrailSectionUrl ? (
            <div className="testrail-actions">
              <a className="btn secondary" href={testrailSectionUrl} target="_blank" rel="noreferrer">
                Open TestRail Section
              </a>
            </div>
          ) : null}
          <ul className="testrail-links-list">
            {testrailLinks.map((item) => (
              <li key={`${item.id}-${item.url}`}>
                <a className="testrail-link" href={item.url} target="_blank" rel="noreferrer">
                  {`C${item.id}: ${item.title}`}
                </a>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <TestCaseTable testCases={testCases} />
    </main>
  );
}

export default Home;
