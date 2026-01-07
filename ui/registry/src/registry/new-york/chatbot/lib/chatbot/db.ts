import type { Message } from "@/registry/new-york/chatbot/components/chatbot/chatbot"
import { Dexie, type EntityTable } from "dexie"

interface Chat {
  id: string
  messages: Message[]
}

interface Setting {
  key: string
  value: string | null
}

interface ChatSettings {
  currentChatId: string | null
}

export const db = new Dexie("ChatsDatabase") as Dexie & {
  chats: EntityTable<Chat, "id">
  settings: EntityTable<Setting, "key">
}

db.version(1).stores({
  chats: "&id",
  settings: "&key",
})

export const settings = {
  async get<K extends keyof ChatSettings>(
    key: K,
  ): Promise<ChatSettings[K] | null> {
    const row = await db.settings.get(key)
    return row?.value ?? null
  },

  async set<K extends keyof ChatSettings>(
    key: K,
    value: ChatSettings[K],
  ): Promise<void> {
    await db.settings.put({ key, value })
  },
}
