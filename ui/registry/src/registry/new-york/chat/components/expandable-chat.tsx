"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useLockBodyScroll } from "@/registry/new-york/chat/hooks/useLockBodyScroll"
import useMediaQuery from "@/registry/new-york/chat/hooks/useMediaQuery"
import { BotMessageSquare, Expand, Minimize, X } from "lucide-react"
import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react"
import { createPortal } from "react-dom"

interface ExpandableChatProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode
}

const ChatContext = createContext<
  | {
      isOpen: boolean
      toggleChat: () => void
      isFullscreen: boolean
      toggleFullscreen: () => void
    }
  | undefined
>(undefined)

export const useChat = () => {
  const context = useContext(ChatContext)
  if (!context) throw new Error("useChat must be used within ExpandableChat")
  return context
}

const ExpandableChat: React.FC<ExpandableChatProps> = ({
  className,
  icon,
  children,
  ...props
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const chatRef = useRef<HTMLDivElement>(null)
  const [portalTarget, setPortalTarget] = useState<HTMLElement | null>(null)

  const toggleChat = () => setIsOpen(!isOpen)

  const [userIsFullscreen, setUserIsFullscreen] = useState(false)
  const toggleFullscreen = () => setUserIsFullscreen(!userIsFullscreen)

  const isSmallScreen = useMediaQuery("(max-width: 640px)")
  const isFullscreen = isOpen && (userIsFullscreen || isSmallScreen)

  useLockBodyScroll(isOpen)

  useEffect(() => {
    // Defer portal target resolution to the client to avoid SSR document access
    setPortalTarget(document.body)
  }, [])

  if (!portalTarget) return null

  return createPortal(
    <ChatContext.Provider
      value={{ isOpen, toggleChat, isFullscreen, toggleFullscreen }}
    >
      <div
        className={cn(
          `fixed inset-0 isolate z-[999]`,
          isOpen ? "bg-black/20" : "pointer-events-none",
          className,
        )}
        onClick={e => {
          e.stopPropagation()
          if (e.target === e.currentTarget && isOpen) {
            toggleChat()
          }
        }}
        {...props}
      >
        <div
          ref={chatRef}
          className={cn(
            "pointer-events-auto fixed right-4 bottom-24 flex h-[80vh] w-full max-w-xl origin-bottom-right flex-col overflow-hidden rounded-2xl border bg-background shadow-md transition-all duration-300 ease-in-out",
            isOpen
              ? "scale-100 opacity-100"
              : "pointer-events-none scale-0 opacity-0",
            isFullscreen
              ? "right-0 bottom-0 h-full w-full max-w-3xl rounded-none rounded-l-md shadow-lg"
              : "",
            className,
          )}
        >
          {children}
        </div>
        {!isFullscreen && (
          <ExpandableChatToggle
            icon={icon}
            isOpen={isOpen}
            toggleChat={toggleChat}
            className="pointer-events-auto absolute right-4 bottom-4 z-[800]"
          />
        )}
      </div>
    </ChatContext.Provider>,
    portalTarget,
  )
}

ExpandableChat.displayName = "ExpandableChat"

const ExpandableChatHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => {
  const { toggleChat, isFullscreen, toggleFullscreen } = useChat()

  const isSmallScreen = useMediaQuery("(max-width: 640px)")

  return (
    <div
      className={cn(
        "flex items-center gap-2 border-b py-2 pr-13 pl-2",
        className,
      )}
      {...props}
    >
      <Button
        variant="ghost"
        size="icon"
        onClick={isSmallScreen ? toggleChat : toggleFullscreen}
      >
        {isSmallScreen ? (
          <X className="size-4" />
        ) : isFullscreen ? (
          <Minimize className="size-4" />
        ) : (
          <Expand className="size-4" />
        )}
      </Button>
      {props.children}
    </div>
  )
}

ExpandableChatHeader.displayName = "ExpandableChatHeader"

const ExpandableChatBody: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => <div className={cn("flex-grow overflow-y-auto", className)} {...props} />

ExpandableChatBody.displayName = "ExpandableChatBody"

const ExpandableChatFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn(
      "relative mx-auto w-full max-w-3xl p-2",
      "before:absolute before:-top-6 before:right-0 before:left-0 before:h-6",
      "before:bg-gradient-to-t before:from-background before:to-transparent",
      "before:pointer-events-none before:z-10",
      className,
    )}
    {...props}
  />
)

ExpandableChatFooter.displayName = "ExpandableChatFooter"

interface ExpandableChatToggleProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon?: React.ReactNode
  isOpen: boolean
  toggleChat: () => void
}

const ExpandableChatToggle: React.FC<ExpandableChatToggleProps> = ({
  className,
  icon,
  isOpen,
  toggleChat,
  ...props
}) => (
  <Button
    variant="default"
    onClick={toggleChat}
    className={cn(
      "mr-2 mb-2 ml-auto flex h-14 w-14 cursor-pointer items-center justify-center rounded-full bg-primary shadow-md transition-all duration-300 hover:shadow-lg hover:shadow-black/30",
      className,
    )}
    {...props}
  >
    {isOpen ? (
      <X className="size-5" />
    ) : (
      icon || <BotMessageSquare className="size-6" />
    )}
  </Button>
)

ExpandableChatToggle.displayName = "ExpandableChatToggle"

export {
  ExpandableChat,
  ExpandableChatBody,
  ExpandableChatFooter,
  ExpandableChatHeader,
}
