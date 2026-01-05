/** @type {import("prettier").Config} */
export default {
  semi: false,
  arrowParens: "avoid",
  trailingComma: "all",
  sortingMethod: "alphabetical",
  plugins: [
    "prettier-plugin-astro",
    "prettier-plugin-tailwindcss",
    "prettier-plugin-sort-imports",
  ],
  tailwindStylesheet: "./src/styles/global.css",
  overrides: [
    {
      files: "*.astro",
      options: {
        parser: "astro",
      },
    },
  ],
}
