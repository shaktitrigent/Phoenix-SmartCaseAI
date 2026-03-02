import { getExportUrl } from "../services/api";

function ExportButtons({ disabled, onPushToTestRail, pushLoading }) {
  return (
    <div className="panel">
      <h3>Export</h3>
      <div className="inline export-row">
        <button
          className="btn secondary"
          disabled={disabled}
          onClick={() => window.open(getExportUrl("excel"), "_blank")}
          type="button"
        >
          Export Excel
        </button>
        <button
          className="btn secondary"
          disabled={disabled}
          onClick={() => window.open(getExportUrl("pdf"), "_blank")}
          type="button"
        >
          Export PDF
        </button>
        <button
          className="btn secondary"
          disabled={disabled}
          onClick={() => window.open(getExportUrl("gherkin"), "_blank")}
          type="button"
        >
          Export Gherkin
        </button>
        <button
          className="btn testrail"
          disabled={disabled || pushLoading}
          onClick={onPushToTestRail}
          type="button"
        >
          {pushLoading ? "Pushing..." : "Push To TestRail"}
        </button>
      </div>
    </div>
  );
}

export default ExportButtons;
