import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/generate-from-jira": "http://localhost:5000",
      "/manual-generate-test": "http://localhost:5000",
      "/testrail": "http://localhost:5000",
      "/attachment": "http://localhost:5000",
      "/export": "http://localhost:5000",
      "/health": "http://localhost:5000"
    }
  }
});
