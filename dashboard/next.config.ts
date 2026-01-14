import { defaultLocale } from "./config"
import { NextConfig } from "next"
import createNextIntlPlugin from "next-intl/plugin"

/** @type {import('next').NextConfig} */
const nextConfig: NextConfig = {
  typedRoutes: true,
  output: "standalone",
}

const withNextIntl = createNextIntlPlugin({
  experimental: {
    // Relative path(s) to source files
    srcPath: ".",

    extract: {
      // Defines which locale to extract to
      sourceLocale: defaultLocale,
    },

    messages: {
      // Relative path to the directory
      path: "./messages",

      // Either 'json', 'po', or a custom format (see below)
      format: "json",

      // Either 'infer' to automatically detect locales based on
      // matching files in `path` or an explicit array of locales
      locales: "infer",
    },
  },
})
export default withNextIntl(nextConfig)
