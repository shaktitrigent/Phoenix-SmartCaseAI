import { useEffect, useMemo, useRef, useState } from "react";

function LocatorResults({ data, language }) {
  const [functionExportOpen, setFunctionExportOpen] = useState(false);
  const [automationExportOpen, setAutomationExportOpen] = useState(false);
  const actionMenusRef = useRef(null);

  const extension = useMemo(() => {
    const value = String(language || "").toLowerCase();
    if (value === "java") {
      return "java";
    }
    if (value === "typescript") {
      return "ts";
    }
    return "py";
  }, [language]);

  const locators = Array.isArray(data?.locators) ? data.locators : [];
  const testFunction = String(data?.test_function || "");
  const automationScript = String(data?.automation_script || data?.test_template || "");

  const copy = async (text) => {
    if (!text) {
      return;
    }
    try {
      if (!navigator?.clipboard?.writeText) {
        throw new Error("Clipboard is not available.");
      }
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  const downloadBlob = (content, filename, type = "text/plain;charset=utf-8") => {
    if (!content) {
      return;
    }
    const blob = new Blob([content], { type });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  const downloadAutomationScript = () => {
    downloadBlob(automationScript, `generated_automation_script.${extension}`);
  };

  const downloadTestFunction = () => {
    downloadBlob(testFunction, `generated_test_function.${extension}`);
  };

  const exportAutomationAsText = () => {
    downloadBlob(automationScript, "generated_automation_script.txt");
  };

  const exportFunctionAsText = () => {
    downloadBlob(testFunction, "generated_test_function.txt");
  };

  const exportAutomationAsMarkdown = () => {
    const markdown = [
      "# Generated Automation Script",
      "",
      "```",
      automationScript,
      "```"
    ].join("\n");
    downloadBlob(markdown, "generated_automation_script.md", "text/markdown;charset=utf-8");
  };

  const exportFunctionAsMarkdown = () => {
    const markdown = [
      "# Generated Test Function",
      "",
      "```",
      testFunction,
      "```"
    ].join("\n");
    downloadBlob(markdown, "generated_test_function.md", "text/markdown;charset=utf-8");
  };

  const exportLocatorsJson = () => {
    const payload = JSON.stringify({ locators }, null, 2);
    downloadBlob(payload, "generated_locators.json", "application/json;charset=utf-8");
  };

  const exportFullLocatorBundle = () => {
    const payload = JSON.stringify(
        {
          language,
          locators,
          test_function: testFunction,
          automation_script: automationScript
        },
        null,
        2
    );
    downloadBlob(payload, "generated_locator_bundle.json", "application/json;charset=utf-8");
  };

  useEffect(() => {
    const onDocumentClick = (event) => {
      if (!actionMenusRef.current?.contains(event.target)) {
        setFunctionExportOpen(false);
        setAutomationExportOpen(false);
      }
    };
    document.addEventListener("click", onDocumentClick);
    return () => document.removeEventListener("click", onDocumentClick);
  }, []);

  if (!data) {
    return (
      <div className="card">
        <h3 className="section-title">Locator Output</h3>
        <div className="empty-state">
          <div className="empty-illustration" />
          <p>Generated locators and template will appear here.</p>
        </div>
      </div>
    );
  }

  const handleFunctionExport = (option) => {
    setFunctionExportOpen(false);
    if (option === "all") {
      downloadTestFunction();
      exportFunctionAsText();
      exportFunctionAsMarkdown();
      return;
    }
    if (option === "native") {
      downloadTestFunction();
      return;
    }
    if (option === "txt") {
      exportFunctionAsText();
      return;
    }
    if (option === "md") {
      exportFunctionAsMarkdown();
    }
  };

  const handleAutomationExport = (option) => {
    setAutomationExportOpen(false);
    if (option === "all") {
      downloadAutomationScript();
      exportAutomationAsText();
      exportAutomationAsMarkdown();
      exportLocatorsJson();
      exportFullLocatorBundle();
      return;
    }
    if (option === "native") {
      downloadAutomationScript();
      return;
    }
    if (option === "txt") {
      exportAutomationAsText();
      return;
    }
    if (option === "md") {
      exportAutomationAsMarkdown();
      return;
    }
    if (option === "locators-json") {
      exportLocatorsJson();
      return;
    }
    if (option === "bundle") {
      exportFullLocatorBundle();
    }
  };

  return (
    <div className="results-stack" ref={actionMenusRef}>
      <details className="card collapsible" open>
        <summary>
          <span>Generated Locators</span>
        </summary>
        {locators.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Element</th>
                  <th>Primary Locator</th>
                  <th>Alternate Locator</th>
                  <th>Strategy</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {locators.map((item, idx) => (
                  <tr key={`${item.element}-${idx}`}>
                    <td>{item.element}</td>
                    <td>{item.primary_locator}</td>
                    <td>{item.alternate_locator}</td>
                    <td>{item.strategy}</td>
                    <td>
                      <button className="btn ghost small" type="button" onClick={() => copy(item.primary_locator)}>
                        Copy
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No locators were returned.</p>
        )}
      </details>

      <details className="card collapsible" open>
        <summary>
          <span>Generated Test Function</span>
        </summary>
        {testFunction ? (
          <>
            <div className="inline actions-row">
              <button className="btn ghost small" type="button" onClick={() => copy(testFunction)}>
                Copy
              </button>
              <div className="export-menu">
                <button
                  className="btn secondary small"
                  type="button"
                  onClick={() => setFunctionExportOpen((prev) => !prev)}
                >
                  Export
                </button>
                {functionExportOpen ? (
                  <div className="export-dropdown">
                    <button type="button" className="export-option" onClick={() => handleFunctionExport("all")}>
                      Export All
                    </button>
                    <button type="button" className="export-option" onClick={() => handleFunctionExport("native")}>
                      Download .{extension}
                    </button>
                    <button type="button" className="export-option" onClick={() => handleFunctionExport("txt")}>
                      Export .txt
                    </button>
                    <button type="button" className="export-option" onClick={() => handleFunctionExport("md")}>
                      Export .md
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
            <pre className="code-block">{testFunction}</pre>
          </>
        ) : (
          <p>No test function was returned.</p>
        )}
      </details>

      <details className="card collapsible" open>
        <summary>
          <span>Generated Automation Script</span>
        </summary>
        {automationScript ? (
          <>
            <div className="inline actions-row">
              <button className="btn ghost small" type="button" onClick={() => copy(automationScript)}>
                Copy
              </button>
              <div className="export-menu">
                <button
                  className="btn secondary small"
                  type="button"
                  onClick={() => setAutomationExportOpen((prev) => !prev)}
                >
                  Export
                </button>
                {automationExportOpen ? (
                  <div className="export-dropdown">
                    <button type="button" className="export-option" onClick={() => handleAutomationExport("all")}>
                      Export All
                    </button>
                    <button type="button" className="export-option" onClick={() => handleAutomationExport("native")}>
                      Download .{extension}
                    </button>
                    <button type="button" className="export-option" onClick={() => handleAutomationExport("txt")}>
                      Export .txt
                    </button>
                    <button type="button" className="export-option" onClick={() => handleAutomationExport("md")}>
                      Export .md
                    </button>
                    <button
                      type="button"
                      className="export-option"
                      onClick={() => handleAutomationExport("locators-json")}
                    >
                      Export Locators JSON
                    </button>
                    <button type="button" className="export-option" onClick={() => handleAutomationExport("bundle")}>
                      Export Full Bundle
                    </button>
                  </div>
                ) : null}
              </div>
            </div>
            <pre className="code-block">{automationScript}</pre>
          </>
        ) : (
          <p>No automation script was returned.</p>
        )}
      </details>
    </div>
  );
}

export default LocatorResults;
