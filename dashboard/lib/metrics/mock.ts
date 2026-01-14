import {
  DashboardMetrics,
  LatencyMetrics,
  MetricState,
  ModelUsageMetrics,
  RateLimitingMetrics,
  ServiceHealthMetrics,
  TrafficMetrics,
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

export function buildMockDashboardMetrics(): DashboardMetrics {
  return {
    traffic: mockTraffic,
    latency: mockLatency,
    modelUsage: mockModelUsage,
    rateLimiting: mockRateLimiting,
    serviceHealth: mockServiceHealth,
  }
}
