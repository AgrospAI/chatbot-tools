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
import { MetricState, TimeToTokenMetrics } from "@/lib/metrics/types"
import { useExtracted } from "next-intl"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

type TimeToFirstTokenSectionProps = {
  metrics: MetricState<TimeToTokenMetrics>
}

export function TimeToFirstTokenSection({
  metrics,
}: TimeToFirstTokenSectionProps) {
  const t = useExtracted()
  const summary = metrics.data?.summary
  const series = metrics.data?.series ?? []
  const errorMessage = metrics.error
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">
          {t("Time to First Token")}
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("LLM response latency percentiles (seconds)")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 grid grid-cols-3 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">P50</p>
            <p className="text-xl font-semibold text-foreground">
              {summary ? `${summary.p50.toFixed(2)}s` : "--"}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">P90</p>
            <p className="text-xl font-semibold text-foreground">
              {summary ? `${summary.p90.toFixed(2)}s` : "--"}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">P99</p>
            <p className="text-xl font-semibold text-foreground">
              {summary ? `${summary.p99.toFixed(2)}s` : "--"}
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
              p50: {
                label: "P50",
                color: "var(--chart-3)",
              },
              p90: {
                label: "P90",
                color: "var(--chart-2)",
              },
              p99: {
                label: "P99",
                color: "var(--chart-4)",
              },
            }}
            className="h-[200px] w-full aspect-auto"
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={series}>
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
                  dataKey="p50"
                  stroke="var(--chart-3)"
                  fill="var(--chart-3)"
                  fillOpacity={0.2}
                  isAnimationActive={false}
                />
                <Area
                  type="monotone"
                  dataKey="p90"
                  stroke="var(--chart-2)"
                  fill="var(--chart-2)"
                  fillOpacity={0.2}
                  isAnimationActive={false}
                />
                <Area
                  type="monotone"
                  dataKey="p99"
                  stroke="var(--chart-4)"
                  fill="var(--chart-4)"
                  fillOpacity={0.2}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  )
}
