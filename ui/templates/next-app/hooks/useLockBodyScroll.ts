import { useEffect } from "react"

export function useLockBodyScroll(lock: boolean = true): void {
  useEffect(() => {
    document.body.style.overflow = lock ? "hidden" : "visible"
    return () => {
      document.body.style.overflow = "visible"
    }
  }, [lock])
}
