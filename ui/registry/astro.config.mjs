// @ts-check
import starlight from "@astrojs/starlight"
import tailwindcss from "@tailwindcss/vite"
import { defineConfig } from "astro/config"

import react from "@astrojs/react"
import { pluginLineNumbers } from "@expressive-code/plugin-line-numbers"

// https://astro.build/config
export default defineConfig({
  site: "https://agrospai.github.io",
  base: "/chatbot-tools",
  vite: {
    plugins: [tailwindcss(), pluginLineNumbers()],
  },
  integrations: [
    starlight({
      title: "fastRAG UI",
      logo: {
        light: "/src/assets/light-logo.svg",
        dark: "/src/assets/dark-logo.svg",
      },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/AgrospAI/chatbot-tools",
        },
      ],
      sidebar: [
        {
          label: "Components",
          autogenerate: { directory: "components" },
        },
      ],
      customCss: ["./src/styles/global.css"],
      favicon: "/favicon.svg",
    }),
    react(),
  ],
})
