const target = process.env.VITE_PROXY_TARGET ?? "http://127.0.0.1:8000";
export default defineConfig({
  plugins: [react()],
  server: { host: true, proxy: { "/api": target } },
});