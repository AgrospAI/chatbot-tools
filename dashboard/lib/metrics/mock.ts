import {
  DashboardMetrics,
  MetricState,
  ModelUsageMetrics,
  RateLimitingMetrics,
  RejectedRequestsMetrics,
  ServiceHealthMetrics,
  TimeToTokenMetrics,
  TokenLengthMetrics,
  TrafficMetrics,
} from "@/lib/metrics/types"

const mockTraffic: MetricState<TrafficMetrics> = {
  data: {
    summary: {
      requestsPerSec: 24.5,
      concurrent: 12,
      pending: 3,
    },
    series: [
      { time: "00:00", requests: 15, concurrent: 8, pending: 1 },
      { time: "04:00", requests: 18, concurrent: 9, pending: 2 },
      { time: "08:00", requests: 35, concurrent: 15, pending: 4 },
      { time: "12:00", requests: 42, concurrent: 18, pending: 5 },
      { time: "16:00", requests: 38, concurrent: 16, pending: 3 },
      { time: "20:00", requests: 22, concurrent: 10, pending: 2 },
    ],
  },
}

const mockModelUsage: MetricState<ModelUsageMetrics> = {
  data: {
    summary: {
      inputTokens: 245,
      outputTokens: 342,
    },
    series: [
      { time: "00:00", input: 180, output: 320 },
      { time: "04:00", input: 192, output: 328 },
      { time: "08:00", input: 268, output: 389 },
      { time: "12:00", input: 289, output: 405 },
      { time: "16:00", input: 276, output: 398 },
      { time: "20:00", input: 210, output: 350 },
    ],
  },
}

const mockRateLimiting: MetricState<RateLimitingMetrics> = {
  data: {
    summary: {
      requestsPerIpAvg: 2.8,
      rejected: 12,
    },
    series: [
      { time: "00:00", allowed: 15, rejected: 1 },
      { time: "04:00", allowed: 18, rejected: 1 },
      { time: "08:00", allowed: 35, rejected: 2 },
      { time: "12:00", allowed: 42, rejected: 4 },
      { time: "16:00", allowed: 38, rejected: 3 },
      { time: "20:00", allowed: 22, rejected: 1 },
    ],
  },
}

const mockServiceHealth: MetricState<ServiceHealthMetrics> = {
  data: {
    metrics: [
      { label: "Uptime", value: "99.95%", status: "healthy" },
      { label: "Liveness", value: "Active", status: "healthy" },
      { label: "Error Rate", value: "0.05%", status: "healthy" },
    ],
  },
}

const mockTimeToFirstToken: MetricState<TimeToTokenMetrics> = {
  data: {
    summary: {
      p50: 0.45,
      p90: 0.82,
      p99: 1.35,
    },
    series: [
      { time: "00:00", p50: 0.38, p90: 0.68, p99: 1.12 },
      { time: "04:00", p50: 0.42, p90: 0.74, p99: 1.18 },
      { time: "08:00", p50: 0.48, p90: 0.86, p99: 1.42 },
      { time: "12:00", p50: 0.45, p90: 0.82, p99: 1.35 },
      { time: "16:00", p50: 0.43, p90: 0.78, p99: 1.28 },
      { time: "20:00", p50: 0.4, p90: 0.72, p99: 1.15 },
    ],
  },
}

const mockTimeToLastToken: MetricState<TimeToTokenMetrics> = {
  data: {
    summary: {
      p50: 2.65,
      p90: 4.82,
      p99: 8.95,
    },
    series: [
      { time: "00:00", p50: 2.48, p90: 4.48, p99: 8.32 },
      { time: "04:00", p50: 2.58, p90: 4.62, p99: 8.55 },
      { time: "08:00", p50: 2.72, p90: 4.95, p99: 9.18 },
      { time: "12:00", p50: 2.65, p90: 4.82, p99: 8.95 },
      { time: "16:00", p50: 2.55, p90: 4.65, p99: 8.75 },
      { time: "20:00", p50: 2.52, p90: 4.58, p99: 8.62 },
    ],
  },
}

const mockQuestionLength: MetricState<TokenLengthMetrics> = {
  data: {
    summary: {
      average: 145,
    },
    series: [
      { time: "00:00", value: 128 },
      { time: "04:00", value: 136 },
      { time: "08:00", value: 154 },
      { time: "12:00", value: 150 },
      { time: "16:00", value: 142 },
      { time: "20:00", value: 132 },
    ],
  },
}

const mockAnswerLength: MetricState<TokenLengthMetrics> = {
  data: {
    summary: {
      average: 342,
    },
    series: [
      { time: "00:00", value: 312 },
      { time: "04:00", value: 326 },
      { time: "08:00", value: 365 },
      { time: "12:00", value: 358 },
      { time: "16:00", value: 348 },
      { time: "20:00", value: 320 },
    ],
  },
}

const mockRejectedRequests: MetricState<RejectedRequestsMetrics> = {
  data: {
    summary: {
      totalRejected: 12,
    },
    series: [
      { time: "00:00", rejected: 1 },
      { time: "04:00", rejected: 1 },
      { time: "08:00", rejected: 2 },
      { time: "12:00", rejected: 4 },
      { time: "16:00", rejected: 3 },
      { time: "20:00", rejected: 1 },
    ],
  },
}

export function buildMockDashboardMetrics(): DashboardMetrics {
  return {
    traffic: mockTraffic,
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
