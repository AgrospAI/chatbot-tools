"use client"

import { Monitor, Moon, Sun } from "lucide-react"
import { useExtracted } from "next-intl"
import { useTheme } from "next-themes"

interface Props {
  initialTheme: string
}

export default function ClientThemePicker({ initialTheme }: Props) {
  const { theme, setTheme } = useTheme()
  const currentTheme = theme ?? initialTheme

  const t = useExtracted()

  const themes = [
    {
      value: "light",
      label: t("Light"),
      icon: Sun,
      description: t("Clean and bright interface"),
    },
    {
      value: "dark",
      label: t("Dark"),
      icon: Moon,
      description: t("Easy on the eyes"),
    },
    {
      value: "system",
      label: t("System"),
      icon: Monitor,
      description: t("Matches your device"),
    },
  ]

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {themes.map(themeOption => {
        const Icon = themeOption.icon
        const isSelected = currentTheme === themeOption.value

        return (
          <button
            key={themeOption.value}
            onClick={() =>
              setTheme(themeOption.value as "light" | "dark" | "system")
            }
            className={`group relative flex flex-col items-center gap-3 rounded-lg border-2 p-4 transition-all hover:border-primary/50 ${
              isSelected
                ? "border-primary bg-primary/5"
                : "border-border bg-card"
            }`}
          >
            <Icon
              className={`h-6 w-6 transition-colors ${
                isSelected ? "text-primary" : "text-muted-foreground"
              }`}
            />
            <div className="text-center">
              <p
                className={`text-sm font-medium ${isSelected ? "text-primary" : "text-foreground"}`}
              >
                {themeOption.label}
              </p>
              <p className="mt-0.5 text-xs text-muted-foreground">
                {themeOption.description}
              </p>
            </div>
            {isSelected && (
              <div className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary" />
            )}
          </button>
        )
      })}
    </div>
  )
}
