import { createEnv } from "@t3-oss/env-nextjs"
import { z } from "zod"

export const env = createEnv({
  server: {
    METRICS_USE_MOCK: z
      .string()
      .transform(s => s !== "false" && s !== "0")
      .default(false),
    PROMETHEUS_BASE_URL: z.string().min(1).optional(),
    PROMETHEUS_BEARER_TOKEN: z.string().min(1).optional(),
  },
  client: {
    NEXT_PUBLIC_PUBLISHABLE_KEY: z.string().min(1).optional(),
  },
  runtimeEnv: {
    METRICS_USE_MOCK: process.env.METRICS_USE_MOCK,
    PROMETHEUS_BASE_URL: process.env.PROMETHEUS_BASE_URL,
    PROMETHEUS_BEARER_TOKEN: process.env.PROMETHEUS_BEARER_TOKEN,
    NEXT_PUBLIC_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_PUBLISHABLE_KEY,
  },
})
