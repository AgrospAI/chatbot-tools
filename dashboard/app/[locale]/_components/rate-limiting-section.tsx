"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { MetricState, RateLimitingMetrics } from "@/lib/metrics/types"
import { ShieldAlert, ShieldCheck } from "lucide-react"
import { useExtracted } from "next-intl"
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

type RateLimitingSectionProps = {
  metrics: MetricState<RateLimitingMetrics>
}

export function RateLimitingSection({ metrics }: RateLimitingSectionProps) {
  const t = useExtracted()
  const summary = metrics.data?.summary
  const series = metrics.data?.series ?? []
  const errorMessage = metrics.error
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">{t("Rate Limiting")}</CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("Request rate control metrics")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3 rounded-lg border border-border bg-card/50 p-4">
            <div className="rounded-full bg-primary/10 p-2">
              <ShieldCheck className="h-5 w-5 text-primary" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">
                {t("Req/IP (avg)")}
              </p>
              <p className="text-xl font-semibold text-foreground">
                {summary?.requestsPerIpAvg?.toLocaleString() ?? "--"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-lg border border-border bg-card/50 p-4">
            <div className="rounded-full bg-destructive/10 p-2">
              <ShieldAlert className="h-5 w-5 text-destructive" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{t("Rejected")}</p>
              <p className="text-xl font-semibold text-foreground">
                {summary?.rejected?.toLocaleString() ?? "--"}
              </p>
            </div>
          </div>
        </div>
        {errorMessage ? (
          <div className="flex h-[200px] items-center justify-center rounded-lg border border-destructive/50 bg-destructive/5 text-sm text-destructive">
            {errorMessage}
          </div>
        ) : (
          <ChartContainer
            config={{
              allowed: {
                label: "Allowed",
                color: "var(--chart-1)",
              },
              rejected: {
                label: "Rejected",
                color: "var(--destructive)",
              },
            }}
            className="h-[200px] aspect-auto w-full "
          >
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={series}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--border)"
                  vertical={false}
                />
                <XAxis
                  dataKey="time"
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                />
                <YAxis stroke="var(--muted-foreground)" fontSize={12} />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar
                  dataKey="allowed"
                  fill="var(--chart-1)"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="rejected"
                  fill="var(--destructive)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
