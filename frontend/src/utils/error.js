export const getFriendlyError = (err, fallback = "Request failed") => {
  const raw =
    err?.response?.data?.error ||
    err?.message ||
    fallback;
  const message = String(raw || fallback);
  const lower = message.toLowerCase();

  if (lower.includes("network error") || lower.includes("failed to fetch")) {
    return "Network error. Ensure the backend is running at http://localhost:5000.";
  }
  if (lower.includes("missing jira credentials")) {
    return "Jira is not configured. Set Jira Base URL, username, and API token in Settings.";
  }
  if (lower.includes("jira authentication failed") || lower.includes("(401)")) {
    return "Jira authentication failed. Check Jira username/email and API token in Settings.";
  }
  if (lower.includes("jira issue not found")) {
    return "Jira issue not found. Verify the issue key and access permissions.";
  }
  if (lower.includes("invalid issue_key format") || lower.includes("issue_key is required")) {
    return "Enter a valid Jira issue key like PROJ-123.";
  }
  if (lower.includes("no exportable test cases")) {
    return "No approved test cases to export. Approve at least one case.";
  }
  if (lower.includes("pending review cases must be approved")) {
    return "Pending cases must be approved or rejected before exporting or pushing.";
  }
  if (lower.includes("testrail configuration is incomplete")) {
    return "TestRail is not configured. Add base URL, username, API key, and section ID in Settings.";
  }
  if (lower.includes("no approved test cases available to push")) {
    return "No approved test cases to push. Approve at least one case first.";
  }
  if (lower.includes("test case not found")) {
    return "Selected test case was not found. Refresh and try again.";
  }

  return message;
};
