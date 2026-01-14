"use client"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { MetricState, ServiceHealthMetrics } from "@/lib/metrics/types"
import { AlertCircle, CheckCircle2 } from "lucide-react"
import { useExtracted } from "next-intl"

type ServiceHealthSectionProps = {
  metrics: MetricState<ServiceHealthMetrics>
}

export function ServiceHealthSection({ metrics }: ServiceHealthSectionProps) {
  const t = useExtracted()
  const healthMetrics = metrics.data?.metrics ?? []
  const errorMessage = metrics.error

  const statusIcon = {
    healthy: CheckCircle2,
    warning: AlertCircle,
    critical: AlertCircle,
  }

  const statusColor = {
    healthy: "text-primary",
    warning: "text-amber-500",
    critical: "text-destructive",
  }

  return (
    <Card className="border-border">
      <CardHeader>
        <CardTitle className="text-foreground">{t("Service Health")}</CardTitle>
        <CardDescription className="text-muted-foreground">
          {t("System health and availability metrics")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {errorMessage ? (
          <div className="flex items-center justify-center rounded-lg border border-destructive/50 bg-destructive/5 p-4 text-sm text-destructive">
            {errorMessage}
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            {healthMetrics.map(metric => {
              const Icon = statusIcon[metric.status]
              const color = statusColor[metric.status]
              return (
                <div
                  key={metric.label}
                  className="flex items-center justify-between rounded-lg border border-border bg-card/50 p-4"
                >
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">
                      {metric.label}
                    </p>
                    <p className="text-2xl font-semibold text-foreground">
                      {metric.value}
                    </p>
                  </div>
                  <div className="rounded-full bg-primary/10 p-2">
                    <Icon className={`h-5 w-5 ${color}`} />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
