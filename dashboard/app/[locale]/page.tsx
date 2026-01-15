import { LatencySection } from "@/app/[locale]/_components/latency-section"
import { ModelUsageSection } from "@/app/[locale]/_components/model-usage-section"
import { RateLimitingSection } from "@/app/[locale]/_components/rate-limiting-section"
import { ServiceHealthSection } from "@/app/[locale]/_components/service-health-section"
import { TrafficSection } from "@/app/[locale]/_components/traffic-section"
import { PageHeader } from "@/components/page-header"
import { getDashboardMetrics } from "@/lib/metrics/prometheus"
import { getExtracted } from "next-intl/server"

export default async function Home() {
  const t = await getExtracted()
  const metrics = await getDashboardMetrics()
  return (
    <div className="min-h-screen bg-background w-full">
      <div className="w-full p-4 sm:p-6 space-y-6 max-w-[1600px] mx-auto">
        <PageHeader
          title={t("Service Observability")}
          description={t("Real-time monitoring and metrics")}
        />

        {/* Dashboard Grid */}
        <div className="grid gap-4 sm:gap-6">
          <ServiceHealthSection metrics={metrics.serviceHealth} />
          <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
            <TrafficSection metrics={metrics.traffic} />
            <LatencySection metrics={metrics.latency} />
          </div>
          <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
            <RateLimitingSection metrics={metrics.rateLimiting} />
            <ModelUsageSection metrics={metrics.modelUsage} />
          </div>
        </div>
      </div>
    </div>
  )
}
