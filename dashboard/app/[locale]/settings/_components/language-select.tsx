"use client"

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../../../components/ui/select"
import { localeLabels, locales } from "@/config"
import { usePathname, useRouter } from "@/i18n/navigation"
import { Globe } from "lucide-react"
import { useParams } from "next/navigation"
import { useTransition } from "react"

export default function LanguageSelect() {
  const router = useRouter()
  const [_, startTransition] = useTransition()
  const pathname = usePathname()
  const params = useParams()

  const handleChange = (value: string | null) => {
    if (value === null) return
    startTransition(() => {
      router.replace(
        // @ts-expect-error -- TypeScript will validate that only known `params`
        // are used in combination with a given `pathname`. Since the two will
        // always match for the current route, we can skip runtime checks.
        { pathname, params },
        { locale: value },
      )
    })
  }

  return (
    <Select value={params.locale as string} onValueChange={handleChange}>
      <SelectTrigger
        id="language"
        className="w-full border-input bg-background text-foreground sm:max-w-sm"
      >
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-muted-foreground" />
          <SelectValue>
            {localeLabels[params.locale as keyof typeof localeLabels]}
          </SelectValue>
        </div>
      </SelectTrigger>
      <SelectContent>
        {locales.map(locale => (
          <SelectItem key={locale} value={locale}>
            {localeLabels[locale]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
