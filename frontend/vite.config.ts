import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), "");
	return {
		plugins: [react()],
		server: {
			port: 5173,
			proxy: {
				"/api": {
					target: env.VITE_BACKEND_URL || "http://localhost:8000",
					changeOrigin: true,
				},
				"/ws": {
					target: env.VITE_WS_URL || "ws://localhost:8000",
					ws: true,
				},
			},
		},
	};
});
