import { AnswerLengthSection } from "@/app/[locale]/_components/answer-length-section"
import { ModelUsageSection } from "@/app/[locale]/_components/model-usage-section"
import { QuestionLengthSection } from "@/app/[locale]/_components/question-length-section"
import { RateLimitingSection } from "@/app/[locale]/_components/rate-limiting-section"
import { ServiceHealthSection } from "@/app/[locale]/_components/service-health-section"
import { TimeToFirstTokenSection } from "@/app/[locale]/_components/time-to-first-token-section"
import { TimeToLastTokenSection } from "@/app/[locale]/_components/time-to-last-token-section"
import { TrafficSection } from "@/app/[locale]/_components/traffic-section"
import { PageHeader } from "@/components/page-header"

import { FilterSection } from "./_components/filter-section"
import {
  getDashboardRedirectUrl,
  parseFromParam,
  parseRefreshParam,
  parseSearchParams,
  parseToParam,
} from "./params"
import { route } from "@/config/site"
import { redirect } from "@/i18n/navigation"
import { getDashboardMetrics } from "@/lib/metrics/prometheus"
import { getExtracted } from "next-intl/server"

interface Props {
  params: Promise<{ locale: string }>
  searchParams: Promise<Record<string, string | string[] | undefined>>
}

export default async function Home({
  params: rawParams,
  searchParams: rawSearchParams,
}: Props) {
  const params = await rawParams
  const resolvedSearchParams = await rawSearchParams
  const searchParams = parseSearchParams(resolvedSearchParams)

  if (searchParams === null) {
    const query = getDashboardRedirectUrl(resolvedSearchParams)
    redirect({
      href: { pathname: route.home, query },
      locale: params.locale,
    })
    return
  }

  const fromDate = parseFromParam(searchParams.from)
  const toDate = parseToParam(searchParams.to)
  const refresh = parseRefreshParam(searchParams.refresh)

  const metrics = await getDashboardMetrics({ fromDate, toDate, refresh })
  const t = await getExtracted()

  return (
    <div className="min-h-screen bg-background w-full">
      <div className="w-full p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title={t("Service Observability")}
          description={t("Real-time monitoring and metrics")}
        />
        <FilterSection />
        {metrics && (
          <div className="grid gap-4 sm:gap-6">
            <ServiceHealthSection metrics={metrics.serviceHealth} />
            <TrafficSection metrics={metrics.traffic} />
            <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
              <TimeToFirstTokenSection metrics={metrics.timeToFirstToken} />
              <TimeToLastTokenSection metrics={metrics.timeToLastToken} />
            </div>
            <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
              <RateLimitingSection metrics={metrics.rateLimiting} />
              <ModelUsageSection metrics={metrics.modelUsage} />
            </div>
            <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
              <QuestionLengthSection metrics={metrics.questionLength} />
              <AnswerLengthSection metrics={metrics.answerLength} />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
