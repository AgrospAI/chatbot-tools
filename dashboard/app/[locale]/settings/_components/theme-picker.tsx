import ClientThemePicker from "./client-theme-picker"
import { getTheme } from "@/lib/theme"

export default async function ThemePicker() {
  const theme = await getTheme()

  return <ClientThemePicker initialTheme={theme} />
}
