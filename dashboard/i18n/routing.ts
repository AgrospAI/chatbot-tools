import { defaultLocale, locales } from "@/config"
import { defineRouting } from "next-intl/routing"

export const routing = defineRouting({
  locales,
  defaultLocale,
})
