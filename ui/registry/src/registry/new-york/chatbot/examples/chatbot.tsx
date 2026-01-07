import Chatbot, {
  type Message,
} from "@/registry/new-york/chatbot/components/chatbot/chatbot"
import { MessageCircleQuestionMark } from "lucide-react"
import { useState } from "react"

const title = "Chatbot Assistant"
const promptSuggestions = [
  "What's the weather like today?",
  "Tell me a joke.",
  "How do I bake a chocolate cake?",
  "Explain quantum computing in simple terms.",
]

const icon = <MessageCircleQuestionMark className="size-6" />

export default function Default() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      message: "Hello! I'm your Chatbot Assistant. How can I help you today?",
      pending: false,
      sources: [],
    },
  ])

  const clearMessages = async () => {
    setMessages([])
  }

  return (
    <Chatbot
      strings={{ title, promptSuggestions }}
      messages={messages}
      setMessages={setMessages}
      icon={icon}
      newChat={clearMessages}
    />
  )
}
