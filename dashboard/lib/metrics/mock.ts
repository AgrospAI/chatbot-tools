import {
  DashboardMetrics,
  LatencyMetrics,
  MetricState,
  ModelUsageMetrics,
  RateLimitingMetrics,
  ServiceHealthMetrics,
  TrafficMetrics,
  TimeToTokenMetrics,
  TokenLengthMetrics,
  RejectedRequestsMetrics,
} from "@/lib/metrics/types"

const mockTraffic: MetricState<TrafficMetrics> = {
  data: {
    summary: {
      requestsPerSec: 3247,
      concurrent: 124,
      pending: 8,
    },
    series: [
      { time: "00:00", requests: 1200, concurrent: 45, pending: 3 },
      { time: "04:00", requests: 980, concurrent: 38, pending: 2 },
      { time: "08:00", requests: 2400, concurrent: 89, pending: 5 },
      { time: "12:00", requests: 3200, concurrent: 124, pending: 8 },
      { time: "16:00", requests: 2800, concurrent: 102, pending: 6 },
      { time: "20:00", requests: 1800, concurrent: 67, pending: 4 },
    ],
  },
}

const mockLatency: MetricState<LatencyMetrics> = {
  data: {
    summary: {
      p50: 58,
      p90: 112,
      p99: 198,
    },
    series: [
      { time: "00:00", p50: 45, p90: 89, p99: 156 },
      { time: "04:00", p50: 38, p90: 76, p99: 142 },
      { time: "08:00", p50: 52, p90: 98, p99: 178 },
      { time: "12:00", p50: 58, p90: 112, p99: 198 },
      { time: "16:00", p50: 48, p90: 94, p99: 168 },
      { time: "20:00", p50: 42, p90: 84, p99: 152 },
    ],
  },
}

const mockModelUsage: MetricState<ModelUsageMetrics> = {
  data: {
    summary: {
      inputTokens: 298000,
      outputTokens: 198000,
    },
    series: [
      { time: "00:00", input: 145000, output: 98000 },
      { time: "04:00", input: 112000, output: 76000 },
      { time: "08:00", input: 234000, output: 156000 },
      { time: "12:00", input: 298000, output: 198000 },
      { time: "16:00", input: 267000, output: 178000 },
      { time: "20:00", input: 189000, output: 126000 },
    ],
  },
}

const mockRateLimiting: MetricState<RateLimitingMetrics> = {
  data: {
    summary: {
      requestsPerIpAvg: 127,
      rejected: 42,
    },
    series: [
      { time: "00:00", allowed: 2800, rejected: 12 },
      { time: "04:00", allowed: 2300, rejected: 8 },
      { time: "08:00", allowed: 4200, rejected: 28 },
      { time: "12:00", allowed: 5100, rejected: 42 },
      { time: "16:00", allowed: 4500, rejected: 35 },
      { time: "20:00", allowed: 3200, rejected: 18 },
    ],
  },
}

const mockServiceHealth: MetricState<ServiceHealthMetrics> = {
  data: {
    metrics: [
      { label: "Uptime", value: "99.98%", status: "healthy" },
      { label: "Liveness", value: "Active", status: "healthy" },
      { label: "Error Rate", value: "0.02%", status: "healthy" },
    ],
  },
}

const mockTimeToFirstToken: MetricState<TimeToTokenMetrics> = {
  data: {
    summary: {
      p50: 0.34,
      p90: 0.72,
      p99: 1.25,
    },
    series: [
      { time: "00:00", p50: 0.28, p90: 0.58, p99: 0.98 },
      { time: "04:00", p50: 0.32, p90: 0.64, p99: 1.05 },
      { time: "08:00", p50: 0.38, p90: 0.76, p99: 1.28 },
      { time: "12:00", p50: 0.34, p90: 0.72, p99: 1.25 },
      { time: "16:00", p50: 0.3, p90: 0.68, p99: 1.18 },
      { time: "20:00", p50: 0.29, p90: 0.61, p99: 1.02 },
    ],
  },
}

const mockTimeToLastToken: MetricState<TimeToTokenMetrics> = {
  data: {
    summary: {
      p50: 2.15,
      p90: 4.32,
      p99: 8.45,
    },
    series: [
      { time: "00:00", p50: 1.98, p90: 3.98, p99: 7.82 },
      { time: "04:00", p50: 2.08, p90: 4.12, p99: 8.05 },
      { time: "08:00", p50: 2.22, p90: 4.45, p99: 8.68 },
      { time: "12:00", p50: 2.15, p90: 4.32, p99: 8.45 },
      { time: "16:00", p50: 2.05, p90: 4.15, p99: 8.25 },
      { time: "20:00", p50: 2.02, p90: 4.08, p99: 8.12 },
    ],
  },
}

const mockQuestionLength: MetricState<TokenLengthMetrics> = {
  data: {
    summary: {
      average: 187,
    },
    series: [
      { time: "00:00", value: 156 },
      { time: "04:00", value: 168 },
      { time: "08:00", value: 192 },
      { time: "12:00", value: 187 },
      { time: "16:00", value: 178 },
      { time: "20:00", value: 165 },
    ],
  },
}

const mockAnswerLength: MetricState<TokenLengthMetrics> = {
  data: {
    summary: {
      average: 523,
    },
    series: [
      { time: "00:00", value: 478 },
      { time: "04:00", value: 492 },
      { time: "08:00", value: 548 },
      { time: "12:00", value: 523 },
      { time: "16:00", value: 512 },
      { time: "20:00", value: 485 },
    ],
  },
}

const mockRejectedRequests: MetricState<RejectedRequestsMetrics> = {
  data: {
    summary: {
      totalRejected: 24,
    },
    series: [
      { time: "00:00", rejected: 4 },
      { time: "04:00", rejected: 3 },
      { time: "08:00", rejected: 8 },
      { time: "12:00", rejected: 24 },
      { time: "16:00", rejected: 18 },
      { time: "20:00", rejected: 12 },
    ],
  },
}

export function buildMockDashboardMetrics(): DashboardMetrics {
  return {
    traffic: mockTraffic,
    latency: mockLatency,
    modelUsage: mockModelUsage,
    rateLimiting: mockRateLimiting,
    serviceHealth: mockServiceHealth,
    timeToFirstToken: mockTimeToFirstToken,
    timeToLastToken: mockTimeToLastToken,
    questionLength: mockQuestionLength,
    answerLength: mockAnswerLength,
    rejectedRequests: mockRejectedRequests,
  }
}
