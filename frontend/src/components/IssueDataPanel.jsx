import { getAttachmentUrl } from "../services/api";

function IssueDataPanel({ sourceData }) {
  if (!sourceData) {
    return null;
  }

  const attachments = sourceData.attachments || [];
  const formatBytes = (size) => {
    const num = Number(size || 0);
    if (!Number.isFinite(num) || num <= 0) {
      return "0 B";
    }
    if (num < 1024) {
      return `${num} B`;
    }
    if (num < 1024 * 1024) {
      return `${(num / 1024).toFixed(1)} KB`;
    }
    return `${(num / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleOpenAttachment = (item) => {
    if (!item?.content_url) {
      return;
    }
    const url = getAttachmentUrl({
      contentUrl: item.content_url,
      filename: item.filename,
      mimeType: item.mime_type,
      download: false
    });
    window.open(url, "_blank", "noopener,noreferrer");
  };

  const handleDownloadAttachment = (item) => {
    if (!item?.content_url) {
      return;
    }
    const url = getAttachmentUrl({
      contentUrl: item.content_url,
      filename: item.filename,
      mimeType: item.mime_type,
      download: true
    });
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="panel">
      <h3>Fetched Jira Data</h3>
      <div className="field">
        <label>Issue Key</label>
        <div className="read-box">{sourceData.issue_key || "-"}</div>
      </div>
      <div className="field">
        <label>Issue Type</label>
        <div className="read-box">{sourceData.issue_type || "-"}</div>
      </div>
      <div className="field">
        <label>Summary</label>
        <div className="read-box">{sourceData.summary || "-"}</div>
      </div>
      <div className="field">
        <label>Description</label>
        <pre className="read-box pre-wrap">{sourceData.description || "-"}</pre>
      </div>
      <div className="field">
        <label>Acceptance Criteria</label>
        <pre className="read-box pre-wrap">{sourceData.acceptance_criteria || "-"}</pre>
      </div>

      <div className="field">
        <label>Attachments ({attachments.length})</label>
        {!attachments.length ? (
          <div className="read-box">No attachments found.</div>
        ) : (
          <div className="attachments-grid">
            {attachments.map((item, idx) => (
              <article
                key={`${item.source_issue_key || "ISSUE"}-${item.filename || "file"}-${idx}`}
                className="attachment-card"
              >
                <div className="attachment-header">
                  <strong className="attachment-name">{item.filename || "-"}</strong>
                  <span className="attachment-issue">{item.source_issue_key || "-"}</span>
                </div>
                <div className="attachment-meta">
                  <span>{item.mime_type || "-"}</span>
                  <span>{formatBytes(item.size_bytes)}</span>
                </div>
                <div className="attachment-status">
                  <span className="status-pill">Download: {item.download_status || "-"}</span>
                  <span className="status-pill">Parse: {item.parse_status || "-"}</span>
                </div>
                <div className="attachment-actions">
                  <button
                    type="button"
                    className="btn ghost small"
                    onClick={() => handleOpenAttachment(item)}
                    disabled={!item.content_url}
                  >
                    Open
                  </button>
                  <button
                    type="button"
                    className="btn ghost small"
                    onClick={() => handleDownloadAttachment(item)}
                    disabled={!item.content_url}
                  >
                    Download
                  </button>
                </div>
                {item.preview_data_url ? (
                  <div className="attachment-image-wrap">
                    <img
                      className="attachment-image"
                      src={item.preview_data_url}
                      alt={item.filename || "Attachment preview"}
                      loading="lazy"
                    />
                  </div>
                ) : null}
                <details className="attachment-details">
                  <summary>{item.preview_data_url ? "Parsed text (if available)" : "Parsed text preview"}</summary>
                  <pre className="pre-wrap attachment-preview">{item.parsed_text || "-"}</pre>
                </details>
              </article>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default IssueDataPanel;
