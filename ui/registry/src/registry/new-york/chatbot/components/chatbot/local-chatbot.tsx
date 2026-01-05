import { useEffect, useState } from "react"

import type {
  ChatbotProps,
  Message,
} from "@/registry/new-york/chatbot/components/chatbot/chatbot"
import Chatbot from "@/registry/new-york/chatbot/components/chatbot/chatbot"
import { db, settings } from "@/registry/new-york/chatbot/lib/chatbot/db"
import { useLiveQuery } from "dexie-react-hooks"

type Props = Omit<ChatbotProps, "messages" | "setMessages" | "newChat">

export default function LocalChatbot({
  endpoint = "http://localhost:8000/ask",
  strings,
  icon,
}: Props) {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      let storedChatId = await settings.get("currentChatId")

      if (!storedChatId) {
        storedChatId = crypto.randomUUID()
        await db.chats.add({ id: storedChatId, messages: [] })
        await settings.set("currentChatId", storedChatId)
      }

      setCurrentChatId(storedChatId)
      console.log("Current Chat ID:", storedChatId)
    })()
  }, [])

  const messages =
    useLiveQuery(async () => {
      if (!currentChatId) return []
      const chat = await db.chats.get(currentChatId)
      return chat?.messages ?? []
    }, [currentChatId]) ?? []

  const setMessages: React.Dispatch<
    React.SetStateAction<Message[]>
  > = value => {
    if (!currentChatId) return
    ;(async () => {
      const chat = await db.chats.get(currentChatId)
      const prev = chat?.messages ?? []

      const next = typeof value === "function" ? value(prev) : value

      await db.chats.update(currentChatId, { messages: next })
    })()
  }

  const newChat = async () => {
    await db.chats.clear()

    const newChatId = crypto.randomUUID()
    await db.chats.add({ id: newChatId, messages: [] })
    await settings.set("currentChatId", newChatId)
    setCurrentChatId(newChatId)
  }
  return (
    <Chatbot
      endpoint={endpoint}
      strings={strings}
      icon={icon}
      messages={messages}
      setMessages={setMessages}
      newChat={newChat}
    />
  )
}
