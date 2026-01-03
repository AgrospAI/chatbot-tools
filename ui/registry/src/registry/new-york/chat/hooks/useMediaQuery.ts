import { useMemo, useState, useEffect } from "react"

export function useMediaQuery(query: string) {
  const normalizedQuery = query.startsWith("@media")
    ? query.substring("@media".length, query.length)
    : query
  const mediaQueryList = useMemo(
    () => matchMedia(normalizedQuery),
    [normalizedQuery],
  )
  const [matches, setMatches] = useState(mediaQueryList.matches)

  useEffect(() => {
    const handleChange = (e: MediaQueryListEvent) => {
      setMatches(e.matches)
    }

    mediaQueryList.addEventListener("change", handleChange)

    return () => {
      mediaQueryList.removeEventListener("change", handleChange)
    }
  }, [mediaQueryList])

  return matches
}

export default useMediaQuery
