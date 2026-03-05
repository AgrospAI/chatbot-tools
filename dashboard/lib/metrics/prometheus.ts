import { env } from "@/env"
import { buildMockDashboardMetrics } from "@/lib/metrics/mock"
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

type QueryRangeResponse = {
  status: "success" | "error"
  data?: {
    resultType: string
    result: Array<{
      metric: Record<string, string>
      values: Array<[number, string]>
    }>
  }
  error?: string
}

type QueryInstantResponse = {
  status: "success" | "error"
  data?: {
    resultType: string
    result: Array<{
      metric: Record<string, string>
      value: [number, string]
    }>
  }
  error?: string
}

type GetDashboardMetricsOptions = {
  useMock?: boolean
  fromDate?: Date
  toDate?: Date
  refresh?: number
}

const PROM_QUERIES = {
  requestsPerSecond: "sum(rate(http_requests_total[5m]))",
  concurrentRequests: "sum(http_requests_in_flight)",
  pendingRequests: "sum(http_requests_in_flight)",
  rejectedRequests: "sum(rate(rejected_requests_total[5m]))",
  requestsPerIp: "avg(rate(requests_per_ip_total[5m]))",
  timeToFirstTokenP50:
    "histogram_quantile(0.5, sum(rate(llm_time_to_first_token_seconds_bucket[5m])) by (le))",
  timeToFirstTokenP90:
    "histogram_quantile(0.9, sum(rate(llm_time_to_first_token_seconds_bucket[5m])) by (le))",
  timeToFirstTokenP99:
    "histogram_quantile(0.99, sum(rate(llm_time_to_first_token_seconds_bucket[5m])) by (le))",
  timeToLastTokenP50:
    "histogram_quantile(0.5, sum(rate(llm_time_to_last_token_seconds_bucket[5m])) by (le))",
  timeToLastTokenP90:
    "histogram_quantile(0.9, sum(rate(llm_time_to_last_token_seconds_bucket[5m])) by (le))",
  timeToLastTokenP99:
    "histogram_quantile(0.99, sum(rate(llm_time_to_last_token_seconds_bucket[5m])) by (le))",
  questionLengthAvg:
    "avg_over_time(llm_question_length_chars_sum[1h]) / avg_over_time(llm_question_length_chars_count[1h])",
  answerLengthAvg:
    "avg_over_time(llm_answer_length_chars_sum[1h]) / avg_over_time(llm_answer_length_chars_count[1h])",
  uptime: "avg_over_time(up[1h])",
  errorRate:
    "sum(rate(http_request_errors_total[5m])) / sum(rate(http_requests_total[5m]))",
  liveness: "up",
  totalRequests: "sum(http_requests_total)",
}

async function queryRange(
  query: string,
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<Array<{ timestamp: number; value: number }>> {
  const searchParams = new URLSearchParams({
    query,
    start: Math.floor(start.getTime() / 1000).toString(),
    end: Math.floor(end.getTime() / 1000).toString(),
    step: stepSeconds.toString(),
  })

  const response = await fetch(
    `${baseUrl}/api/v1/query_range?${searchParams.toString()}`,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: "no-store",
    },
  )

  if (!response.ok) {
    throw new Error(`Prometheus range query failed (${response.status})`)
  }

  const payload = (await response.json()) as QueryRangeResponse
  if (payload.status !== "success" || !payload.data) {
    throw new Error(payload.error ?? "Prometheus range query did not succeed")
  }

  const values = payload.data.result[0]?.values ?? []
  return values.map(([timestamp, raw]) => ({
    timestamp,
    value: Number(raw),
  }))
}

async function queryInstant(
  query: string,
  baseUrl: string,
  token: string | undefined,
): Promise<number> {
  const searchParams = new URLSearchParams({ query })
  const response = await fetch(
    `${baseUrl}/api/v1/query?${searchParams.toString()}`,
    {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      cache: "no-store",
    },
  )

  if (!response.ok) {
    throw new Error(`Prometheus instant query failed (${response.status})`)
  }

  const payload = (await response.json()) as QueryInstantResponse
  if (payload.status !== "success" || !payload.data) {
    throw new Error(payload.error ?? "Prometheus instant query did not succeed")
  }

  const value = payload.data.result[0]?.value?.[1]
  return Number(value ?? 0)
}

function formatTimestampToHour(tsSeconds: number): string {
  const date = new Date(tsSeconds * 1000)
  const hours = date.getUTCHours().toString().padStart(2, "0")
  return `${hours}:00`
}

function average(values: number[]): number {
  if (!values.length) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

async function fetchTrafficMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<TrafficMetrics> {
  const [requestsSeries, concurrentSeries] = await Promise.all([
    queryRange(
      PROM_QUERIES.requestsPerSecond,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.concurrentRequests,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
  ])

  const concurrent = await queryInstant(
    PROM_QUERIES.concurrentRequests,
    baseUrl,
    token,
  )

  const pending = await queryInstant(
    PROM_QUERIES.pendingRequests,
    baseUrl,
    token,
  )

  return {
    summary: {
      requestsPerSec: Number(
        average(requestsSeries.map(point => point.value)).toFixed(0),
      ),
      concurrent,
      pending,
    },
    series: requestsSeries.map((point, index) => ({
      time: formatTimestampToHour(point.timestamp),
      requests: Math.round(point.value),
      concurrent: Math.round(concurrentSeries[index]?.value ?? concurrent),
      pending: Math.round(pending),
    })),
  }
}

async function fetchModelUsageMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<ModelUsageMetrics> {
  const [questionSeries, answerSeries] = await Promise.all([
    queryRange(
      PROM_QUERIES.questionLengthAvg,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.answerLengthAvg,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
  ])

  const series = questionSeries.map((point, index) => ({
    time: formatTimestampToHour(point.timestamp),
    input: Math.round(point.value),
    output: Math.round(answerSeries[index]?.value ?? 0),
  }))

  return {
    summary: {
      inputTokens: Math.round(questionSeries.at(-1)?.value ?? 0),
      outputTokens: Math.round(answerSeries.at(-1)?.value ?? 0),
    },
    series,
  }
}

async function fetchRateLimitingMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<RateLimitingMetrics> {
  const [requestsPerIpSeries, rejectedSeries] = await Promise.all([
    queryRange(
      PROM_QUERIES.requestsPerIp,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.rejectedRequests,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
  ])

  const rejectedCount = await queryInstant(
    PROM_QUERIES.rejectedRequests,
    baseUrl,
    token,
  )

  const series = requestsPerIpSeries.map((point, index) => ({
    time: formatTimestampToHour(point.timestamp),
    allowed: Math.round(point.value),
    rejected: Math.round(rejectedSeries[index]?.value ?? 0),
  }))

  return {
    summary: {
      requestsPerIpAvg: Number(
        average(requestsPerIpSeries.map(p => p.value)).toFixed(0),
      ),
      rejected: Math.round(rejectedCount),
    },
    series,
  }
}

async function fetchServiceHealthMetrics(
  baseUrl: string,
  token: string | undefined,
): Promise<ServiceHealthMetrics> {
  const [uptime, errorRate, liveness] = await Promise.all([
    queryInstant(PROM_QUERIES.uptime, baseUrl, token),
    queryInstant(PROM_QUERIES.errorRate, baseUrl, token),
    queryInstant(PROM_QUERIES.liveness, baseUrl, token),
  ])

  const healthStatus = errorRate > 0.05 ? "warning" : "healthy"
  return {
    metrics: [
      {
        label: "Uptime",
        value: `${(uptime * 100).toFixed(2)}%`,
        status: "healthy",
      },
      {
        label: "Liveness",
        value: liveness > 0 ? "Active" : "Down",
        status: liveness > 0 ? "healthy" : "critical",
      },
      {
        label: "Error Rate",
        value: `${(errorRate * 100).toFixed(2)}%`,
        status: healthStatus,
      },
    ],
  }
}

async function fetchTimeToFirstTokenMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<TimeToTokenMetrics> {
  const [p50Series, p90Series, p99Series] = await Promise.all([
    queryRange(
      PROM_QUERIES.timeToFirstTokenP50,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.timeToFirstTokenP90,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.timeToFirstTokenP99,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
  ])

  const series = p50Series.map((p50Point, index) => ({
    time: formatTimestampToHour(p50Point.timestamp),
    p50: p50Point.value,
    p90: p90Series[index]?.value ?? p50Point.value,
    p99: p99Series[index]?.value ?? p50Point.value,
  }))

  return {
    summary: {
      p50: Number((p50Series.at(-1)?.value ?? 0).toFixed(2)),
      p90: Number((p90Series.at(-1)?.value ?? 0).toFixed(2)),
      p99: Number((p99Series.at(-1)?.value ?? 0).toFixed(2)),
    },
    series,
  }
}

async function fetchTimeToLastTokenMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<TimeToTokenMetrics> {
  const [p50Series, p90Series, p99Series] = await Promise.all([
    queryRange(
      PROM_QUERIES.timeToLastTokenP50,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.timeToLastTokenP90,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
    queryRange(
      PROM_QUERIES.timeToLastTokenP99,
      baseUrl,
      token,
      start,
      end,
      stepSeconds,
    ),
  ])

  const series = p50Series.map((p50Point, index) => ({
    time: formatTimestampToHour(p50Point.timestamp),
    p50: p50Point.value,
    p90: p90Series[index]?.value ?? p50Point.value,
    p99: p99Series[index]?.value ?? p50Point.value,
  }))

  return {
    summary: {
      p50: Number((p50Series.at(-1)?.value ?? 0).toFixed(2)),
      p90: Number((p90Series.at(-1)?.value ?? 0).toFixed(2)),
      p99: Number((p99Series.at(-1)?.value ?? 0).toFixed(2)),
    },
    series,
  }
}

async function fetchQuestionLengthMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<TokenLengthMetrics> {
  const series = await queryRange(
    PROM_QUERIES.questionLengthAvg,
    baseUrl,
    token,
    start,
    end,
    stepSeconds,
  )

  return {
    summary: {
      average: Number(average(series.map(p => p.value)).toFixed(0)),
    },
    series: series.map(point => ({
      time: formatTimestampToHour(point.timestamp),
      value: point.value,
    })),
  }
}

async function fetchAnswerLengthMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<TokenLengthMetrics> {
  const series = await queryRange(
    PROM_QUERIES.answerLengthAvg,
    baseUrl,
    token,
    start,
    end,
    stepSeconds,
  )

  return {
    summary: {
      average: Number(average(series.map(p => p.value)).toFixed(0)),
    },
    series: series.map(point => ({
      time: formatTimestampToHour(point.timestamp),
      value: point.value,
    })),
  }
}

async function fetchRejectedRequestsMetrics(
  baseUrl: string,
  token: string | undefined,
  start: Date,
  end: Date,
  stepSeconds: number,
): Promise<RejectedRequestsMetrics> {
  const series = await queryRange(
    PROM_QUERIES.rejectedRequests,
    baseUrl,
    token,
    start,
    end,
    stepSeconds,
  )

  return {
    summary: {
      totalRejected: Number((series.at(-1)?.value ?? 0).toFixed(0)),
    },
    series: series.map(point => ({
      time: formatTimestampToHour(point.timestamp),
      rejected: point.value,
    })),
  }
}

function fromSettled<T>(
  result: PromiseSettledResult<T>,
  fallback: MetricState<T>,
): MetricState<T> {
  if (result.status === "fulfilled") {
    return { data: result.value }
  }
  const message =
    result.reason instanceof Error
      ? result.reason.message
      : typeof result.reason === "string"
        ? result.reason
        : "Unable to load data"

  return {
    data: fallback.data,
    error: message,
  }
}

export async function getDashboardMetrics(
  options: GetDashboardMetricsOptions = {},
): Promise<DashboardMetrics> {
  const {
    useMock = env.METRICS_USE_MOCK,
    fromDate = new Date(Date.now() - 24 * 60 * 60 * 1000),
    toDate = new Date(),
    refresh = 0,
  } = options
  const mock = buildMockDashboardMetrics()

  const baseUrl = env.PROMETHEUS_BASE_URL
  const token = env.PROMETHEUS_BEARER_TOKEN

  console.log("Use mock metrics:", useMock)

  if (useMock) {
    return mock
  }

  if (!baseUrl) {
    const missingConfigError =
      "Prometheus URL not configured. Serving mock data."

    return {
      traffic: {
        ...mock.traffic,
        error: missingConfigError,
      },
      modelUsage: {
        ...mock.modelUsage,
        error: missingConfigError,
      },
      rateLimiting: {
        ...mock.rateLimiting,
        error: missingConfigError,
      },
      serviceHealth: {
        ...mock.serviceHealth,
        error: missingConfigError,
      },
      timeToFirstToken: {
        ...mock.timeToFirstToken,
        error: missingConfigError,
      },
      timeToLastToken: {
        ...mock.timeToLastToken,
        error: missingConfigError,
      },
      questionLength: {
        ...mock.questionLength,
        error: missingConfigError,
      },
      answerLength: {
        ...mock.answerLength,
        error: missingConfigError,
      },
      rejectedRequests: {
        ...mock.rejectedRequests,
        error: missingConfigError,
      },
    }
  }

  if (!baseUrl) {
    return mock
  }

  const [
    trafficResult,
    modelUsageResult,
    rateLimitingResult,
    serviceHealthResult,
    timeToFirstTokenResult,
    timeToLastTokenResult,
    questionLengthResult,
    answerLengthResult,
    rejectedRequestsResult,
  ] = await Promise.allSettled([
    fetchTrafficMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchModelUsageMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchRateLimitingMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchServiceHealthMetrics(baseUrl, token),
    fetchTimeToFirstTokenMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchTimeToLastTokenMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchQuestionLengthMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchAnswerLengthMetrics(baseUrl, token, fromDate, toDate, refresh),
    fetchRejectedRequestsMetrics(baseUrl, token, fromDate, toDate, refresh),
  ])

  return {
    traffic: fromSettled(trafficResult, mock.traffic),
    modelUsage: fromSettled(modelUsageResult, mock.modelUsage),
    rateLimiting: fromSettled(rateLimitingResult, mock.rateLimiting),
    serviceHealth: fromSettled(serviceHealthResult, mock.serviceHealth),
    timeToFirstToken: fromSettled(
      timeToFirstTokenResult,
      mock.timeToFirstToken,
    ),
    timeToLastToken: fromSettled(timeToLastTokenResult, mock.timeToLastToken),
    questionLength: fromSettled(questionLengthResult, mock.questionLength),
    answerLength: fromSettled(answerLengthResult, mock.answerLength),
    rejectedRequests: fromSettled(
      rejectedRequestsResult,
      mock.rejectedRequests,
    ),
  }
}
