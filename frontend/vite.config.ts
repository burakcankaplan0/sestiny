// defineConfig'i vitest/config'ten alıyoruz; "vite"den gelen sürüm `test` alanını tanımıyor.
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    // Tarayıcı API'lerini taklit eden testler birbirinin global durumunu bozmasın.
    restoreMocks: true,
  },
});
