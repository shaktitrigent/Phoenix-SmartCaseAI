import { useMemo } from "react";

function LocatorResults({ data, language }) {
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

  const locators = Array.isArray(data.locators) ? data.locators : [];
  const template = String(data.test_template || "");

  const copy = async (text) => {
    if (!text) {
      return;
    }
    await navigator.clipboard.writeText(text);
  };

  const downloadTemplate = () => {
    if (!template) {
      return;
    }
    const blob = new Blob([template], { type: "text/plain;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `generated_locator_template.${extension}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="results-stack">
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
          <span>Generated Test Template</span>
        </summary>
        {template ? (
          <>
            <div className="inline actions-row">
              <button className="btn ghost small" type="button" onClick={() => copy(template)}>
                Copy
              </button>
              <button className="btn secondary small" type="button" onClick={downloadTemplate}>
                Download .{extension}
              </button>
            </div>
            <pre className="code-block">{template}</pre>
          </>
        ) : (
          <p>No template was returned.</p>
        )}
      </details>
    </div>
  );
}

export default LocatorResults;
