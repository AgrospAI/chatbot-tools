/** @type {import("prettier").Config} */
export default {
  semi: false,
  arrowParens: "avoid",
  trailingComma: "all",
  sortingMethod: "alphabetical",
  plugins: ["prettier-plugin-tailwindcss", "prettier-plugin-sort-imports"],
  tailwindStylesheet: "./styles/globals.css",
}
