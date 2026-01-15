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
import { MetricState, TrafficMetrics } from "@/lib/metrics/types"
import { useExtracted } from "next-intl"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

type TrafficSectionProps = {
  metrics: MetricState<TrafficMetrics>
}

export function TrafficSection({ metrics }: TrafficSectionProps) {
  const t = useExtracted()
  const summary = metrics.data?.summary
  const series = metrics.data?.series ?? []
  const errorMessage = metrics.error
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">{t("Traffic")}</CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("Request volume and concurrency")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{t("Requests/sec")}</p>
            <p className="text-xl font-semibold text-foreground">
              {summary?.requestsPerSec?.toLocaleString() ?? "--"}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{t("Concurrent")}</p>
            <p className="text-xl font-semibold text-foreground">
              {summary?.concurrent?.toLocaleString() ?? "--"}
            </p>
          </div>
        </div>
        {errorMessage ? (
          <div className="flex h-[200px] items-center justify-center rounded-lg border border-destructive/50 bg-destructive/5 text-sm text-destructive">
            {errorMessage}
          </div>
        ) : (
          <ChartContainer
            config={{
              requests: {
                label: "Requests",
                color: "var(--chart-1)",
              },
            }}
            className="h-[200px] w-full aspect-auto"
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={series}>
                <defs>
                  <linearGradient
                    id="colorRequests"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="5%"
                      stopColor="var(--chart-1)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--chart-1)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>
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
                <Area
                  type="monotone"
                  dataKey="requests"
                  stroke="var(--chart-1)"
                  fill="url(#colorRequests)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
