import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// All port settings live in frontend/.env — edit them THERE, not here.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, __dirname, "");
  return {
    plugins: [react()],
    server: {
      port: Number(env.VITE_PORT) || 5173,
      // Fail with an explicit error if the port is taken, instead of
      // silently hopping to 5174/5175 (which breaks CORS and bookmarks).
      strictPort: true,
    },
  };
});
