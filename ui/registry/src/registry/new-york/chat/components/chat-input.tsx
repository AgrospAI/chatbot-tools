import { cn } from "@/lib/utils"
import {
  AutosizeTextarea,
  type AutosizeTextAreaRef,
} from "@/registry/new-york/chat/components/autosize-textarea"
import * as React from "react"

type ChatInputProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>

const ChatInput = React.forwardRef<AutosizeTextAreaRef, ChatInputProps>(
  ({ className, ...props }, ref) => (
    <AutosizeTextarea
      ref={ref}
      name="message"
      autoComplete="off"
      className={cn(
        "flex w-full resize-none rounded-none border-0 px-4 py-3 text-sm shadow-none",
        "placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
        "outline-none focus:outline-none focus-visible:outline-none",
        "ring-0 focus:ring-0 focus-visible:ring-0",
        "ring-offset-0 focus:ring-offset-0 focus-visible:ring-offset-0",
        className,
      )}
      maxHeight={192}
      {...props}
    />
  ),
)
ChatInput.displayName = "ChatInput"

export { ChatInput }
