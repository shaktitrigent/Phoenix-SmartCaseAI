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

export const getLLMModels = async () => {
  const { data } = await api.get("/llm-models");
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
  const files = Array.isArray(payload?.attachment_files) ? payload.attachment_files : [];

  if (files.length) {
    const formData = new FormData();
    formData.append("description", payload.description || "");
    formData.append("acceptance_criteria", payload.acceptance_criteria || "");
    formData.append("custom_prompt", payload.custom_prompt || "");
    formData.append("attachments_text", payload.attachments_text || "");
    formData.append("model_id", payload.model_id || "");
    formData.append("test_types", (payload.test_types || []).join(","));
    files.forEach((file) => formData.append("attachments", file));

    const { data } = await api.post("/manual-generate-test", formData, {
      headers: { "Content-Type": "multipart/form-data" }
    });
    return data;
  }

  const { attachment_files, ...jsonPayload } = payload || {};
  const { data } = await api.post("/manual-generate-test", jsonPayload);
  return data;
};

export const pushToTestRail = async (payload = {}) => {
  const { data } = await api.post("/testrail/push", payload);
  return data;
};

export const submitReviewedTestCases = async (testCases = []) => {
  const { data } = await api.post("/review-testcases", { test_cases: testCases });
  return data;
};

export const generateLocators = async (payload) => {
  const { data } = await api.post("/generate-locators", payload);
  return data;
};

export const getExportUrl = (type) =>
  `${apiBaseUrl}/export/${type}`;

export const exportTestCases = async (format) => {
  const response = await api.post(
    "/export-testcases",
    { format },
    { responseType: "blob" }
  );

  const disposition = response?.headers?.["content-disposition"] || "";
  const match = disposition.match(/filename="?([^"]+)"?/i);
  return {
    blob: response.data,
    filename: match?.[1] || `generated_test_cases.${format}`
  };
};

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
