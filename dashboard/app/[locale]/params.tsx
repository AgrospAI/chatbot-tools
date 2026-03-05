// Returns an object with valid params or null if any are invalid
export function parseSearchParams(
  params: Record<string, any>,
): DashboardQuery | null {
  try {
    return DashboardQuerySchema.parse(params)
  } catch {
    return null
  }
}

export function getDashboardRedirectUrl(
  params: Record<string, string | string[] | undefined>,
): QueryParams {
  return {}
}

import { QueryParams } from "next-intl/navigation"
import z from "zod"

export const FROM_DATE_PARAM = [
  "now-5min",
  "now-15min",
  "now-30min",
  "now-1h",
  "now-6h",
  "now-12h",
  "now-24h",
  "now-7d",
] as const
export const DEFAULT_FROM_DATE = "now-5min"

export const TO_DATE_PARAM = ["now"] as const
export const DEFAULT_TO_DATE = "now"

export const REFRESH_INTERVALS = ["5s", "10s", "30s"] as const
export const DEFAULT_REFRESH_INTERVAL = "5s"

export type RefreshInterval = (typeof REFRESH_INTERVALS)[number]

export const DashboardQuerySchema = z.object({
  from: z
    .union([z.enum(FROM_DATE_PARAM), z.iso.datetime()])
    .default("now-5min"),
  to: z.union([z.enum(TO_DATE_PARAM), z.iso.datetime()]).default("now"),
  refresh: z.enum(REFRESH_INTERVALS).default("5s"),
})

export type DashboardQuery = z.infer<typeof DashboardQuerySchema>

export function parseFromParam(from: string): Date {
  if (FROM_DATE_PARAM.includes(from as any)) {
    switch (from) {
      case "now-5min":
        return new Date(Date.now() - 5 * 60 * 1000)
      case "now-15min":
        return new Date(Date.now() - 15 * 60 * 1000)
      case "now-30min":
        return new Date(Date.now() - 30 * 60 * 1000)
      case "now-1h":
        return new Date(Date.now() - 60 * 60 * 1000)
      case "now-6h":
        return new Date(Date.now() - 6 * 60 * 60 * 1000)
      case "now-12h":
        return new Date(Date.now() - 12 * 60 * 60 * 1000)
      case "now-24h":
        return new Date(Date.now() - 24 * 60 * 60 * 1000)
      case "now-7d":
        return new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      default:
        return new Date(from)
    }
  }
  return new Date(from)
}

export function parseToParam(to: string): Date {
  if (TO_DATE_PARAM.includes(to as any)) {
    switch (to) {
      case "now":
        return new Date()
      default:
        return new Date(to)
    }
  }
  return new Date(to)
}

export function parseRefreshParam(refresh: RefreshInterval): number {
  switch (refresh) {
    case "5s":
      return 5
    case "10s":
      return 10
    case "30s":
      return 30
    default:
      return 5
  }
}
