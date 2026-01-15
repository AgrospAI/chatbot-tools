"use client"

import type { ChatDetail } from "../page"
import { ChatBubble, ChatBubbleMessage } from "@/components/chat/chat-bubble"
import { ChatMessageList } from "@/components/chat/chat-message-list"
import Markdown from "@/components/chat/markdown/markdown"
import { useRouter } from "@/i18n/navigation"

interface ChatProps {
  chat: ChatDetail
}

export default function Chat({ chat }: ChatProps) {
  const router = useRouter()
  const messages = chat.messages

  return (
    <ChatMessageList className="w-full max-w-3xl">
      {messages.map((message, index) => {
        if (message.role === "assistant") {
          return (
            <ChatBubble key={index} variant="received">
              <ChatBubbleMessage>
                <Markdown references={message.sources}>
                  {message.content}
                </Markdown>
              </ChatBubbleMessage>
            </ChatBubble>
          )
        }

        return (
          <ChatBubble key={index} variant="sent">
            <ChatBubbleMessage>{message.content}</ChatBubbleMessage>
          </ChatBubble>
        )
      })}
    </ChatMessageList>
  )
}
