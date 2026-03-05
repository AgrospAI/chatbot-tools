"use client"

import {
  DEFAULT_FROM_DATE,
  DEFAULT_REFRESH_INTERVAL,
  FROM_DATE_PARAM,
  REFRESH_INTERVALS,
} from "@/app/[locale]/params"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useExtracted } from "next-intl"

import { useQueryState } from "nuqs"

export function FilterSection() {
  const [from, setFrom] = useQueryState("from")
  const [refresh, setRefresh] = useQueryState("refresh")

  const t = useExtracted()

  function getFromDateTranslation(from: string): string {
    const translations: Record<string, string> = {
      "now-5min": t("Last 5 minutes"),
      "now-15min": t("Last 15 minutes"),
      "now-30min": t("Last 30 minutes"),
      "now-1h": t("Last 1 hour"),
      "now-6h": t("Last 6 hours"),
      "now-12h": t("Last 12 hours"),
      "now-24h": t("Last 24 hours"),
      "now-7d": t("Last 7 days"),
    }

    return translations[from]
  }

  function getRefreshIntervalTranslation(refresh: string): string {
    const translations: Record<string, string> = {
      "5s": t("5s"),
      "10s": t("10s"),
      "30s": t("30s"),
    }

    return translations[refresh]
  }

  return (
    <div className="flex flex-wrap gap-6 items-start">
      <div className="flex flex-col min-w-[180px]">
        <label
          htmlFor="from"
          className="mb-2 font-medium text-sm text-gray-700 dark:text-gray-200 capitalize"
        >
          From Date
        </label>
        <Select
          value={from || DEFAULT_FROM_DATE}
          onValueChange={e => setFrom(e)}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue>
              {getFromDateTranslation(from || DEFAULT_FROM_DATE)}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {FROM_DATE_PARAM.map((option: string) => (
              <SelectItem key={option} value={option}>
                {getFromDateTranslation(option)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col min-w-[120px]">
        <label
          htmlFor="refresh"
          className="mb-2 font-medium text-sm text-gray-700 dark:text-gray-200 capitalize"
        >
          Refresh Interval
        </label>
        <Select
          value={refresh || DEFAULT_REFRESH_INTERVAL}
          onValueChange={e => setRefresh(e)}
        >
          <SelectTrigger className="w-[120px]">
            <SelectValue>
              {getRefreshIntervalTranslation(
                refresh || DEFAULT_REFRESH_INTERVAL,
              )}
            </SelectValue>
          </SelectTrigger>
          <SelectContent>
            {REFRESH_INTERVALS.map((option: string) => (
              <SelectItem key={option} value={option}>
                {getRefreshIntervalTranslation(option)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
