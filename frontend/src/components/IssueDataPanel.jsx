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
    <div className="card jira-panel-card">
      <div className="card-head">
        <div className="ch-icon">J</div>
        <h3 className="section-title">Fetched Jira Data</h3>
      </div>
      <div className="card-body">
        <div className="jira-field-grid">
          <div className="jira-field">
            <div className="jira-label">Issue Key</div>
            <div className="jira-value jira-key">{sourceData.issue_key || "-"}</div>
          </div>
          <div className="jira-field">
            <div className="jira-label">Issue Type</div>
            <div className="jira-value">
              <span className="jira-type-pill">{sourceData.issue_type || "-"}</span>
            </div>
          </div>
        </div>

        <div className="jira-field">
          <div className="jira-label">Summary</div>
          <div className="jira-value">{sourceData.summary || "-"}</div>
        </div>
        <div className="jira-field">
          <div className="jira-label">Description</div>
          <div className="jira-value pre-wrap">{sourceData.description || "-"}</div>
        </div>
        <div className="jira-field">
          <div className="jira-label">Acceptance Criteria</div>
          <div className="jira-value jira-muted">{sourceData.acceptance_criteria || "Not specified"}</div>
        </div>

        <div className="jira-attachments">
          <div className="jira-label">Attachments ({attachments.length})</div>
          {!attachments.length ? (
            <div className="jira-empty">No attachments found.</div>
          ) : (
            <div className="attachments-grid">
              {attachments.map((item, idx) => (
                <article
                  key={`${item.source_issue_key || "ISSUE"}-${item.filename || "file"}-${idx}`}
                  className="attachment-card"
                >
                  <div className="attachment-header">
                    <strong className="attachment-name">{item.filename || "-"}</strong>
                  </div>
                  <div className="attachment-meta">
                    <span>{item.mime_type || "-"}</span>
                    <span>{formatBytes(item.size_bytes)}</span>
                    <span>{item.source_issue_key || "-"}</span>
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
    </div>
  );
}

export default IssueDataPanel;
