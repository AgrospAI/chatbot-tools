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
import { MetricState, ModelUsageMetrics } from "@/lib/metrics/types"
import { ArrowDownToLine, ArrowUpFromLine } from "lucide-react"
import { useExtracted } from "next-intl"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

type ModelUsageSectionProps = {
  metrics: MetricState<ModelUsageMetrics>
}

export function ModelUsageSection({ metrics }: ModelUsageSectionProps) {
  const t = useExtracted()
  const summary = metrics.data?.summary
  const series = metrics.data?.series ?? []
  const errorMessage = metrics.error
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">{t("Model Usage")}</CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("Token consumption")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6 grid grid-cols-2 gap-4">
          <div className="flex items-center gap-3 rounded-lg border border-border bg-card/50 p-4">
            <div className="rounded-full bg-chart-3/20 p-2">
              <ArrowDownToLine className="h-5 w-5 text-chart-3" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{t("Tokens In")}</p>
              <p className="text-xl font-semibold text-foreground">
                {summary?.inputTokens?.toLocaleString() ?? "--"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 rounded-lg border border-border bg-card/50 p-4">
            <div className="rounded-full bg-chart-2/20 p-2">
              <ArrowUpFromLine className="h-5 w-5 text-chart-2" />
            </div>
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground">{t("Tokens Out")}</p>
              <p className="text-xl font-semibold text-foreground">
                {summary?.outputTokens?.toLocaleString() ?? "--"}
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
              input: {
                label: "Input Tokens",
                color: "var(--chart-3)",
              },
              output: {
                label: "Output Tokens",
                color: "var(--chart-2)",
              },
            }}
            className="h-[200px] w-full aspect-auto"
          >
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={series}>
                <defs>
                  <linearGradient id="colorInput" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor="var(--chart-3)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--chart-3)"
                      stopOpacity={0}
                    />
                  </linearGradient>
                  <linearGradient id="colorOutput" x1="0" y1="0" x2="0" y2="1">
                    <stop
                      offset="5%"
                      stopColor="var(--chart-2)"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="var(--chart-2)"
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
                  dataKey="input"
                  stroke="var(--chart-3)"
                  fill="url(#colorInput)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="output"
                  stroke="var(--chart-2)"
                  fill="url(#colorOutput)"
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
