import { useEffect, useRef, useState } from "react";

function ExportButtons({
  exportDisabled,
  pushDisabled,
  onPushToTestRail,
  pushLoading,
  onExport,
  exportLoading,
  testRailConfig,
  onTestRailConfigChange
}) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [testrailMenuOpen, setTestrailMenuOpen] = useState(false);
  const containerRef = useRef(null);
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

  useEffect(() => {
    const onDocumentClick = (event) => {
      if (!containerRef.current?.contains(event.target)) {
        setMenuOpen(false);
        setTestrailMenuOpen(false);
      }
    };
    document.addEventListener("click", onDocumentClick);
    return () => document.removeEventListener("click", onDocumentClick);
  }, []);

  const handleExport = (format) => {
    setMenuOpen(false);
    onExport?.(format);
  };

  const handleTestrailPush = (mode) => {
    setTestrailMenuOpen(false);
    onPushToTestRail?.(mode, testRailConfig || {});
  };

  return (
    <div className="card export-card">
      <h3 className="section-title">Export & Publish</h3>
      <div className="inline export-actions" ref={containerRef}>
        <div className="export-menu">
          <button
            className="btn secondary"
            disabled={exportDisabled || exportLoading}
            data-loading={exportLoading ? "true" : "false"}
            onClick={() => setMenuOpen((prev) => !prev)}
            type="button"
          >
            {exportLoading ? "Exporting..." : "Export"}
          </button>
          {menuOpen ? (
            <div className="export-dropdown">
              <button type="button" onClick={() => handleExport("all")} className="export-option">
                Export All
              </button>
              <button type="button" onClick={() => handleExport("plain")} className="export-option">
                Export as Plain Text
              </button>
              <button type="button" onClick={() => handleExport("gherkin")} className="export-option">
                Export as Gherkin
              </button>
              <button type="button" onClick={() => handleExport("pdf")} className="export-option">
                Export as PDF
              </button>
              <button type="button" onClick={() => handleExport("excel")} className="export-option">
                Export as Excel
              </button>
            </div>
          ) : null}
        </div>
        <div className="export-menu">
          <button
            className="btn testrail"
            disabled={pushDisabled || pushLoading}
            data-loading={pushLoading ? "true" : "false"}
            onClick={() => setTestrailMenuOpen((prev) => !prev)}
            type="button"
          >
            {pushLoading ? "Pushing to TestRail..." : "Push to TestRail"}
          </button>
          {testrailMenuOpen ? (
            <div className="export-dropdown testrail-dropdown">
              <div className="testrail-config-grid">
                <label>
                  Project ID
                  <input
                    value={testRailConfig?.project_id || ""}
                    onChange={(event) => onTestRailConfigChange?.("project_id", event.target.value)}
                    placeholder="Optional (uses backend default)"
                  />
                </label>
                <label>
                  Suite ID
                  <input
                    value={testRailConfig?.suite_id || ""}
                    onChange={(event) => onTestRailConfigChange?.("suite_id", event.target.value)}
                    placeholder="Optional (auto/ default)"
                  />
                </label>
                <label>
                  Section ID
                  <input
                    value={testRailConfig?.section_id || ""}
                    onChange={(event) => onTestRailConfigChange?.("section_id", event.target.value)}
                    placeholder="Optional (uses backend default)"
                  />
                </label>
              </div>
              <div className="testrail-divider" />
              {repositoryOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleTestrailPush(option.value)}
                  className="export-option"
                >
                  {option.label}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default ExportButtons;
