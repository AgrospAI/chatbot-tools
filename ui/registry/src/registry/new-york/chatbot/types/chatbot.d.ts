type Message = UserMessage | BotMessage

interface UserMessage {
  role: "user"
  message: string
}
interface BotMessage {
  role: "bot"
  message: string
  pending: boolean
  sources: string[]
}

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
