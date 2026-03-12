import { useEffect, useMemo, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { exportTestCases, getLatestTestCases, pushToTestRail } from "../services/api";

const EXPORT_FORMATS = [
  { id: "excel", label: "Excel" },
  { id: "pdf", label: "PDF" },
  { id: "gherkin", label: "Gherkin" },
  { id: "plain", label: "Plain Text" },
  { id: "json", label: "JSON" },
  { id: "csv", label: "CSV" }
];

function ExportPublish() {
  const [selectedFormats, setSelectedFormats] = useState(["excel"]);
  const [counts, setCounts] = useState({ total: 0, approved: 0, pending: 0, rejected: 0 });
  const [loading, setLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [message, setMessage] = useState("");
  const [repositoryMode, setRepositoryMode] = useState("single_repository");
  const [projectId, setProjectId] = useState("");
  const [suiteId, setSuiteId] = useState("");
  const [sectionId, setSectionId] = useState("");

  const addToast = (messageText, type = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { id, message: messageText, type }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id));
    }, 4500);
  };

  const dismissToast = (id) => {
    setToasts((prev) => prev.filter((item) => item.id !== id));
  };

  const fetchCounts = async ({ silent } = {}) => {
    try {
      const response = await getLatestTestCases();
      setCounts(response?.counts || { total: 0, approved: 0, pending: 0, rejected: 0 });
    } catch (err) {
      if (!silent) {
        addToast(err?.response?.data?.error || err?.message || "Unable to load summary", "error");
      }
    }
  };

  useEffect(() => {
    fetchCounts({ silent: false });
    const intervalId = window.setInterval(() => {
      fetchCounts({ silent: true });
    }, 15000);
    return () => window.clearInterval(intervalId);
  }, []);

  const handleToggleFormat = (formatId) => {
    setSelectedFormats((prev) => {
      if (prev.includes(formatId)) {
        return prev.filter((item) => item !== formatId);
      }
      return [...prev, formatId];
    });
  };

  const exportLabel = useMemo(() => selectedFormats.join(", ") || "Excel", [selectedFormats]);

  const handleExport = async () => {
    const formats = selectedFormats.length ? selectedFormats : ["excel"];
    try {
      if (!counts.total) {
        const messageText = "No test cases available to export. Generate test cases first.";
        setMessage(messageText);
        addToast(messageText, "error");
        return;
      }
      setLoading(true);
      setMessage("");
      for (const exportFormat of formats) {
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
      setMessage(`Exported ${formats.join(", ").toUpperCase()} successfully.`);
      addToast("Export completed.", "success");
    } catch (err) {
      let messageText = err?.message || "Export failed";
      if (err?.response?.data instanceof Blob) {
        try {
          const text = await err.response.data.text();
          const parsed = JSON.parse(text);
          messageText = parsed?.error || messageText;
        } catch {
          messageText = messageText || "Export failed";
        }
      } else if (err?.response?.data?.error) {
        messageText = err.response.data.error;
      }
      setMessage(messageText);
      addToast(messageText, "error");
    } finally {
      setLoading(false);
    }
  };

  const handlePush = async () => {
    try {
      if (!counts.total) {
        const messageText = "No test cases available to push. Generate test cases first.";
        setMessage(messageText);
        addToast(messageText, "error");
        return;
      }
      setLoading(true);
      setMessage("");
      const response = await pushToTestRail({
        repository_mode: repositoryMode,
        project_id: projectId,
        suite_id: suiteId,
        section_id: sectionId
      });
      const created = Number(response?.created || 0);
      const label = created ? `${created} case(s) created.` : "Push completed.";
      setMessage(label);
      addToast("Push to TestRail completed.", "success");
    } catch (err) {
      const messageText = err?.response?.data?.error || err?.message || "TestRail push failed";
      setMessage(messageText);
      addToast(messageText, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Processing export..." />
      <ToastStack toasts={toasts} onDismiss={dismissToast} />

      <div className="page-header">
        <div>
          <h2 className="page-title">Export & Publish</h2>
          <p className="page-subtitle">
            Export approved test cases in your preferred format or push directly to TestRail.
          </p>
        </div>
      </div>

      <div className="export-grid">
        <div className="card split export-summary">
          <div className="card-head">
            <div className="ch-icon">📈</div>
            <h3 className="section-title">Case Summary</h3>
          </div>
          <div className="card-body">
            <div className="summary-row">
              <span>Total Generated</span>
              <strong>{counts.total}</strong>
            </div>
            <div className="summary-row">
              <span>Approved</span>
              <strong className="text-success">{counts.approved}</strong>
            </div>
            <div className="summary-row">
              <span>Rejected</span>
              <strong className="text-danger">{counts.rejected}</strong>
            </div>
            <div className="summary-row">
              <span>Pending</span>
              <strong className="text-warning">{counts.pending}</strong>
            </div>
            <div className="summary-note">
              Rejected cases will not be included in exports or TestRail pushes.
            </div>
          </div>
        </div>

        <div className="card split">
          <div className="card-head">
            <div className="ch-icon">🚀</div>
            <h3 className="section-title">TestRail Configuration</h3>
          </div>
          <div className="card-body">
            <div className="field">
              <label>Repository Mode</label>
              <select value={repositoryMode} onChange={(event) => setRepositoryMode(event.target.value)}>
                <option value="single_repository">Single Suite</option>
                <option value="single_repository_with_baseline">Baseline Suite</option>
                <option value="multiple_test_suites">Multi-Suite</option>
              </select>
            </div>
            <div className="form-grid">
              <div className="field">
                <label>Project ID</label>
                <input value={projectId} onChange={(event) => setProjectId(event.target.value)} />
              </div>
              <div className="field">
                <label>Suite ID</label>
                <input value={suiteId} onChange={(event) => setSuiteId(event.target.value)} />
              </div>
            </div>
            <div className="field">
              <label>Section ID</label>
              <input value={sectionId} onChange={(event) => setSectionId(event.target.value)} />
            </div>
            <div className="helper-note">
              Single Suite: All test cases pushed into one flat suite. Best for small projects.
            </div>
          </div>
        </div>
      </div>

      <div className="card split">
        <div className="card-head">
          <div className="ch-icon">📦</div>
          <h3 className="section-title">Export Format</h3>
        </div>
        <div className="card-body">
          <div className="export-row">
            {EXPORT_FORMATS.map((format) => (
              <button
                key={format.id}
                type="button"
                className={`export-fmt ${selectedFormats.includes(format.id) ? "sel" : ""}`}
                onClick={() => handleToggleFormat(format.id)}
              >
                {format.label}
              </button>
            ))}
          </div>
          <div className="btn-row export-actions">
            <button type="button" className="btn secondary" onClick={handleExport}>
              Download {exportLabel || "Excel"}
            </button>
            <button type="button" className="btn testrail" onClick={handlePush}>
              Push to TestRail
            </button>
          </div>
          {message ? <div className="export-message">{message}</div> : null}
        </div>
      </div>
    </div>
  );
}

export default ExportPublish;
