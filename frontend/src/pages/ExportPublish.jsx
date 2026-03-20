import { useEffect, useMemo, useRef, useState } from "react";
import LoadingOverlay from "../components/LoadingOverlay";
import ToastStack from "../components/ToastStack";
import { exportTestCases, getLatestTestCases, pushToTestRail } from "../services/api";
import { getFriendlyError } from "../utils/error";

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
  const [exportLoading, setExportLoading] = useState(false);
  const [pushLoading, setPushLoading] = useState(false);
  const [toasts, setToasts] = useState([]);
  const [message, setMessage] = useState("");
  const [testrailMenuOpen, setTestrailMenuOpen] = useState(false);
  const [projectId, setProjectId] = useState("");
  const [suiteId, setSuiteId] = useState("");
  const [sectionId, setSectionId] = useState("");
  const testrailRef = useRef(null);
  const repositoryOptions = [
    {
      value: "single_repository",
      label: "Use a single repository for all cases"
    },
    {
      value: "single_repository_with_baseline",
      label: "Use a single repository with baseline support"
    },
    {
      value: "multiple_test_suites",
      label: "Use multiple test suites to manage cases"
    }
  ];

  const loading = exportLoading || pushLoading;
  const addToast = (messageText, type = "info") => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
    setToasts((prev) => [...prev, { id, message: messageText, type }]);
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((item) => item.id !== id));
    }, 9000);
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
        addToast(getFriendlyError(err, "Unable to load summary"), "error");
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

  useEffect(() => {
    const onDocumentClick = (event) => {
      if (!testrailRef.current?.contains(event.target)) {
        setTestrailMenuOpen(false);
      }
    };
    document.addEventListener("click", onDocumentClick);
    return () => document.removeEventListener("click", onDocumentClick);
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
      setExportLoading(true);
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
      addToast(getFriendlyError(err, messageText), "error");
    } finally {
      setExportLoading(false);
    }
  };

  const handlePush = async (mode) => {
    try {
      if (!counts.total) {
        const messageText = "No test cases available to push. Generate test cases first.";
        setMessage(messageText);
        addToast(messageText, "error");
        return;
      }
      if (counts.pending > 0) {
        addToast("Review pending cases in Review Queue. Only approved cases will be pushed.", "info");
      }
      setPushLoading(true);
      setMessage("");
      const response = await pushToTestRail({
        repository_mode: mode,
        project_id: projectId,
        suite_id: suiteId,
        section_id: sectionId
      });
      if (response?.warning) {
        addToast(response.warning, "info");
      }
      const created = Number(response?.created || 0);
      const label = created ? `${created} case(s) created.` : "Push completed.";
      setMessage(label);
      addToast("Push to TestRail completed.", "success");
    } catch (err) {
      const messageText = err?.response?.data?.error || err?.message || "TestRail push failed";
      setMessage(messageText);
      addToast(getFriendlyError(err, messageText), "error");
    } finally {
      setPushLoading(false);
    }
  };

  return (
    <div className="pane active">
      <LoadingOverlay show={loading} label="Processing request..." />
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
            <div className="summary-note">
              Exports include only approved cases.
            </div>
          </div>
        </div>

      </div>

      <div className="card split export-format-card">
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
            <button type="button" className="btn secondary" onClick={handleExport} disabled={exportLoading || pushLoading}>
              Download {exportLabel || "Excel"}
            </button>
            <div className="export-menu" ref={testrailRef}>
              <button
                type="button"
                className="btn testrail"
                disabled={pushLoading || exportLoading}
                data-loading={pushLoading ? "true" : "false"}
                onClick={() => setTestrailMenuOpen((prev) => !prev)}
              >
                {pushLoading ? "Pushing to TestRail..." : "Push to TestRail"}
              </button>
              {testrailMenuOpen ? (
                <div className="export-dropdown testrail-dropdown">
                  <div className="testrail-config-grid">
                    <label>
                      Project ID
                      <input
                        value={projectId}
                        onChange={(event) => setProjectId(event.target.value)}
                        placeholder="Optional (uses backend default)"
                      />
                    </label>
                    <label>
                      Suite ID
                      <input
                        value={suiteId}
                        onChange={(event) => setSuiteId(event.target.value)}
                        placeholder="Optional (auto/ default)"
                      />
                    </label>
                    <label>
                      Section ID
                      <input
                        value={sectionId}
                        onChange={(event) => setSectionId(event.target.value)}
                        placeholder="Optional (uses backend default)"
                      />
                    </label>
                  </div>
                  <div className="testrail-divider" />
                  {repositoryOptions.map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => {
                        setTestrailMenuOpen(false);
                        handlePush(option.value);
                      }}
                      className="export-option"
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
          {message ? <div className="export-message">{message}</div> : null}
        </div>
      </div>
    </div>
  );
}

export default ExportPublish;
