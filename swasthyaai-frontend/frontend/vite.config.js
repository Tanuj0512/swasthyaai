import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    },
    server: {
        port: 5173,
        host: true,
    },
    build: {
        outDir: "dist",
        sourcemap: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    "vendor-react": ["react", "react-dom", "react-router-dom"],
                    "vendor-charts": ["recharts"],
                    "vendor-radix": [
                        "@radix-ui/react-avatar",
                        "@radix-ui/react-dialog",
                        "@radix-ui/react-dropdown-menu",
                        "@radix-ui/react-label",
                        "@radix-ui/react-progress",
                        "@radix-ui/react-select",
                        "@radix-ui/react-separator",
                        "@radix-ui/react-slot",
                        "@radix-ui/react-switch",
                        "@radix-ui/react-tabs",
                        "@radix-ui/react-toast",
                    ],
                    "vendor-supabase": ["@supabase/supabase-js"],
                    "vendor-query": ["@tanstack/react-query"],
                    "vendor-forms": ["react-hook-form", "@hookform/resolvers", "zod"],
                },
            },
        },
    },
});
