import { Button } from "@/components/ui/button"
import {
  ChatBubble,
  ChatBubbleMessage,
} from "@/registry/new-york/chat/components/chat-bubble"
import { ChatInput } from "@/registry/new-york/chat/components/chat-input"
import { ChatMessageList } from "@/registry/new-york/chat/components/chat-message-list"
import {
  ExpandableChat,
  ExpandableChatBody,
  ExpandableChatFooter,
  ExpandableChatHeader,
} from "@/registry/new-york/chat/components/expandable-chat"
import Markdown from "@/registry/new-york/chatbot/components/markdown/markdown"
import PromptSuggestions from "@/registry/new-york/chatbot/components/prompt-suggestions"
import { Send, Trash } from "lucide-react"
import { useState } from "react"

export type Message = UserMessage | BotMessage

export interface UserMessage {
  role: "user"
  message: string
}
export interface BotMessage {
  role: "bot"
  message: string
  pending: boolean
  sources: string[]
}

export type ChatStrings = {
  title: string
  promptSuggestions: string[]
  placeholder: string
  interruptedStreamingError: string
  genericErrorAnswer: string
}

export interface ChatbotProps {
  endpoint?: string
  strings?: Partial<ChatStrings>
  messages: Message[]
  icon?: React.ReactNode
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>
  newChat?: () => Promise<void>
}

export default function Chatbot({
  endpoint = "http://localhost:8000/ask",
  strings,
  messages,
  icon,
  setMessages,
  newChat,
}: ChatbotProps) {
  const title = strings?.title ?? "Chatbot Assistant"
  const promptSuggestions = strings?.promptSuggestions ?? []
  const placeholder = strings?.placeholder ?? "Ask me anything..."
  const interruptedStreamingError =
    strings?.interruptedStreamingError ?? "(Response was interrupted)"
  const genericErrorAnswer =
    strings?.genericErrorAnswer ??
    "Sorry, at this moment I am not able to help you. Try again later."

  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)

  const handleSendMessage = async (input: string) => {
    setInput("")

    const userMessage = {
      role: "user",
      message: input,
    } as UserMessage

    const botMessage = {
      role: "bot",
      message: "",
      pending: true,
    } as BotMessage

    setMessages(messages => [...messages, userMessage, botMessage])

    setIsLoading(true)
    setIsStreaming(true)

    try {
      const response = await fetch(endpoint, {
        method: "post",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: input }),
      })

      if (!response.ok || !response.body) {
        throw response.statusText
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let buffer = ""
      let content = ""
      let sources: string[] = []

      while (true) {
        const { value, done } = await reader.read()
        if (done) {
          break
        }
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split("\n")
        buffer = lines.pop() || ""

        for (const line of lines) {
          const message = line.replace(/^data: /, "").trim()
          if (!message) continue

          try {
            const parsed = JSON.parse(message)

            switch (parsed.type) {
              case "sources":
                sources = parsed.data
                break
              case "token":
                content += parsed.data
                break
            }
          } catch (e) {
            console.error("Error parsing JSON chunk", e)
          }
        }

        if (content) {
          setMessages(prev =>
            prev.map((msg, i) => {
              const isLastMessage = i === prev.length - 1
              if (!isLastMessage || msg.role !== "bot") return msg

              return {
                ...msg,
                message: content,
                sources: [...(msg.sources || []), ...sources],
              }
            }),
          )
          setIsLoading(false)
        }
      }
    } catch (error) {
      console.error("Error during fetch:", error)
      botMessage.message = genericErrorAnswer
    } finally {
      setMessages(prev =>
        prev.map((msg, i) =>
          i === prev.length - 1 ? { ...msg, pending: false } : msg,
        ),
      )
      setIsLoading(false)
      setIsStreaming(false)
    }
  }

  return (
    <ExpandableChat icon={icon}>
      <ExpandableChatHeader>
        <h2 className="m-0! w-full text-center text-xl font-semibold">
          {title}
        </h2>
      </ExpandableChatHeader>
      <ExpandableChatBody
        style={{
          scrollbarGutter: "stable",
        }}
      >
        {messages.length === 0 && (
          <PromptSuggestions
            suggestions={promptSuggestions}
            onClickSuggestion={handleSendMessage}
          />
        )}
        <ChatMessageList className="w-full max-w-3xl">
          {messages.map((message, index) => {
            if (message.role === "bot") {
              const showLoading = isLoading && index === messages.length - 1
              const isLastMessage = index === messages.length - 1
              const interruptedStreaming =
                message.pending && (!isLastMessage || !isStreaming)

              return (
                <ChatBubble key={index} variant="received">
                  <ChatBubbleMessage isLoading={showLoading}>
                    <Markdown references={message.sources}>
                      {message.message}
                    </Markdown>
                    {interruptedStreaming && (
                      <p className="mt-2 text-sm text-muted-foreground">
                        {interruptedStreamingError}
                      </p>
                    )}
                  </ChatBubbleMessage>
                </ChatBubble>
              )
            }

            return (
              <ChatBubble key={index} variant="sent">
                <ChatBubbleMessage>{message.message}</ChatBubbleMessage>
              </ChatBubble>
            )
          })}
        </ChatMessageList>
      </ExpandableChatBody>
      <ExpandableChatFooter>
        <div className="flex flex-col gap-2 rounded-2xl border p-2">
          <ChatInput
            value={input}
            onChange={e => setInput(e.currentTarget.value)}
            placeholder={placeholder}
            onKeyDown={e => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage(input)
              } else if (e.key === "Enter" && e.shiftKey) {
                e.preventDefault()
                setInput(input => input + "\n")
              }
            }}
          />
          <div className="flex gap-2">
            <Button
              variant="destructive"
              size="icon-sm"
              className="cursor-pointer"
              onClick={newChat}
              disabled={messages.length === 0}
            >
              <Trash className="size-4" />
            </Button>
            <div className="flex-grow" />
            <Button
              type="submit"
              size="icon-lg"
              className="cursor-pointer"
              onClick={() => handleSendMessage(input)}
              disabled={!input || isLoading}
            >
              <Send className="size-4" />
            </Button>
          </div>
        </div>
      </ExpandableChatFooter>
    </ExpandableChat>
  )
}
