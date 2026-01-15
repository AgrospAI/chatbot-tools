import { useMemo, useSyncExternalStore } from "react"

function getMediaQueryList(query: string) {
  if (
    typeof window === "undefined" ||
    typeof window.matchMedia !== "function"
  ) {
    return null
  }
  return window.matchMedia(query)
}

export function useMediaQuery(query: string) {
  const normalizedQuery = useMemo(
    () =>
      query.startsWith("@media")
        ? query.substring("@media".length, query.length)
        : query,
    [query],
  )

  const subscribe = (onStoreChange: () => void) => {
    const mediaQueryList = getMediaQueryList(normalizedQuery)
    if (!mediaQueryList) return () => {}

    // Keep state in sync with native media query changes.
    const handler = () => onStoreChange()
    mediaQueryList.addEventListener("change", handler)
    return () => mediaQueryList.removeEventListener("change", handler)
  }

  const getSnapshot = () => getMediaQueryList(normalizedQuery)?.matches ?? false
  const getServerSnapshot = () => false

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}

export default useMediaQuery
