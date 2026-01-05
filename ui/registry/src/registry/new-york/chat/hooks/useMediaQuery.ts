import { useMemo, useState, useEffect } from "react"

export function useMediaQuery(query: string) {
  const normalizedQuery = query.startsWith("@media")
    ? query.substring("@media".length, query.length)
    : query

  const mediaQueryList = useMemo(() => {
    if (
      typeof window === "undefined" ||
      typeof window.matchMedia !== "function"
    ) {
      return null
    }
    return window.matchMedia(normalizedQuery)
  }, [normalizedQuery])

  const [matches, setMatches] = useState(mediaQueryList?.matches ?? false)

  useEffect(() => {
    if (!mediaQueryList) return

    const handleChange = (e: MediaQueryListEvent) => {
      setMatches(e.matches)
    }

    setMatches(mediaQueryList.matches)
    mediaQueryList.addEventListener("change", handleChange)

    return () => {
      mediaQueryList.removeEventListener("change", handleChange)
    }
  }, [mediaQueryList])

  return matches
}

export default useMediaQuery
