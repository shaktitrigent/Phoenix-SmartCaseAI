import axios from "axios";

const apiBaseUrl = import.meta.env.DEV
  ? ""
  : (import.meta.env.VITE_API_BASE_URL || "");

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 45000
});

export const generateFromJira = async (payload) => {
  const { data } = await api.post("/generate-from-jira", payload);
  return data;
};

export const previewJira = async (payload) => {
  const { data } = await api.post("/generate-from-jira", {
    issue_key: payload.issue_key,
    preview_only: true
  });
  return data;
};

export const manualGenerateTest = async (payload) => {
  const { data } = await api.post("/manual-generate-test", payload);
  return data;
};

export const pushToTestRail = async (payload = {}) => {
  const { data } = await api.post("/testrail/push", payload);
  return data;
};

export const getExportUrl = (type) =>
  `${apiBaseUrl}/export/${type}`;

export const getAttachmentUrl = ({
  contentUrl,
  filename,
  mimeType,
  download = false
}) => {
  const params = new URLSearchParams({
    content_url: contentUrl || "",
    filename: filename || "attachment.bin",
    mime_type: mimeType || "application/octet-stream",
    download: download ? "1" : "0"
  });
  return `${apiBaseUrl}/attachment/file?${params.toString()}`;
};

export default api;
