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
import { MetricState, TokenLengthMetrics } from "@/lib/metrics/types"
import { useExtracted } from "next-intl"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts"

type QuestionLengthSectionProps = {
  metrics: MetricState<TokenLengthMetrics>
}

export function QuestionLengthSection({ metrics }: QuestionLengthSectionProps) {
  const t = useExtracted()
  const summary = metrics.data?.summary
  const series = metrics.data?.series ?? []
  const errorMessage = metrics.error
  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">
          {t("Question Length")}
        </CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("Average question size in characters")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground">{t("Average")}</p>
            <p className="text-xl font-semibold text-foreground">
              {summary ? `${summary.average.toFixed(0)} chars` : "--"}
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
              value: {
                label: "Length",
                color: "var(--chart-1)",
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
                  dataKey="value"
                  stroke="var(--chart-1)"
                  fill="var(--chart-1)"
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
