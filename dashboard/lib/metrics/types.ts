export type MetricState<T> = {
  data: T | null
  error?: string
}

export type TrafficPoint = {
  time: string
  requests: number
  concurrent: number
  pending: number
}

export type TrafficMetrics = {
  summary: {
    requestsPerSec: number
    concurrent: number
    pending: number
  }
  series: TrafficPoint[]
}

export type LatencyPoint = {
  time: string
  p50: number
  p90: number
  p99: number
}

export type LatencyMetrics = {
  summary: {
    p50: number
    p90: number
    p99: number
  }
  series: LatencyPoint[]
}

export type ModelUsagePoint = {
  time: string
  input: number
  output: number
}

export type ModelUsageMetrics = {
  summary: {
    inputTokens: number
    outputTokens: number
  }
  series: ModelUsagePoint[]
}

export type RateLimitingPoint = {
  time: string
  allowed: number
  rejected: number
}

export type RateLimitingMetrics = {
  summary: {
    requestsPerIpAvg: number
    rejected: number
  }
  series: RateLimitingPoint[]
}

export type ServiceHealthMetric = {
  label: string
  value: string
  status: "healthy" | "warning" | "critical"
}

export type ServiceHealthMetrics = {
  metrics: ServiceHealthMetric[]
}

export type TimeToTokenPoint = {
  time: string
  p50: number
  p90: number
  p99: number
}

export type TimeToTokenMetrics = {
  summary: {
    p50: number
    p90: number
    p99: number
  }
  series: TimeToTokenPoint[]
}

export type TokenLengthPoint = {
  time: string
  value: number
}

export type TokenLengthMetrics = {
  summary: {
    average: number
  }
  series: TokenLengthPoint[]
}

export type RejectedRequestsMetrics = {
  summary: {
    totalRejected: number
  }
  series: Array<{
    time: string
    rejected: number
  }>
}

export type DashboardMetrics = {
  traffic: MetricState<TrafficMetrics>
  latency: MetricState<LatencyMetrics>
  modelUsage: MetricState<ModelUsageMetrics>
  rateLimiting: MetricState<RateLimitingMetrics>
  serviceHealth: MetricState<ServiceHealthMetrics>
  timeToFirstToken: MetricState<TimeToTokenMetrics>
  timeToLastToken: MetricState<TimeToTokenMetrics>
  questionLength: MetricState<TokenLengthMetrics>
  answerLength: MetricState<TokenLengthMetrics>
  rejectedRequests: MetricState<RejectedRequestsMetrics>
}
