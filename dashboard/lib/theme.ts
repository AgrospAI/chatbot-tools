import { themeCookieName } from "@/config"
import { cookies } from "next/headers"

export async function getTheme() {
  return (await cookies()).get(themeCookieName)?.value ?? "light"
}
