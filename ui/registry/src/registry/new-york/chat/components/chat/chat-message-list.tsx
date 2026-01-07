import { Button } from "@/components/ui/button"
import { useAutoScroll } from "@/registry/new-york/chat/hooks/useAutoScroll"
import { ArrowDown } from "lucide-react"
import * as React from "react"

interface ChatMessageListProps extends React.HTMLAttributes<HTMLDivElement> {
  smooth?: boolean
}

const ChatMessageList = React.forwardRef<HTMLDivElement, ChatMessageListProps>(
  ({ className, children, smooth = false, ...props }, ref) => {
    const { scrollRef, isAtBottom, scrollToBottom, disableAutoScroll } =
      useAutoScroll({
        smooth,
        content: children,
      })

    // Merge the forwarded ref with scrollRef
    const mergedRef = React.useCallback(
      (node: HTMLDivElement | null) => {
        scrollRef.current = node
        if (typeof ref === "function") {
          ref(node)
        } else if (ref) {
          ref.current = node
        }
      },
      [ref, scrollRef],
    )

    return (
      <div className="relative">
        <div
          className={`mx-auto flex h-full w-full flex-col overflow-y-auto p-4 ${className}`}
          ref={mergedRef}
          onWheel={disableAutoScroll}
          onTouchMove={disableAutoScroll}
          style={{
            scrollBehavior: smooth ? "smooth" : "auto",
          }}
          {...props}
        >
          <div className="flex flex-col gap-6">{children}</div>
        </div>

        {!isAtBottom && (
          <Button
            onClick={() => {
              scrollToBottom()
            }}
            size="icon"
            variant="outline"
            className="absolute bottom-2 left-1/2 inline-flex -translate-x-1/2 transform rounded-full shadow-md"
            aria-label="Scroll to bottom"
          >
            <ArrowDown className="h-4 w-4" />
          </Button>
        )}
      </div>
    )
  },
)

ChatMessageList.displayName = "ChatMessageList"

export { ChatMessageList }
