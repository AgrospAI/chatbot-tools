import Chat from "./_components/chat"
import { PageHeader } from "@/components/page-header"
import { Link } from "@/i18n/navigation"
import { notFound } from "next/navigation"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  created_at: string
  sources: Array<string>
}

export interface ChatDetail {
  chat_id: string
  created_at: string
  messages: Message[]
}

async function fetchChat(chatId: string): Promise<ChatDetail | null> {
  try {
    const res = await fetch(`http://localhost:8000/chats/${chatId}`, {
      cache: "no-store",
    })
    if (!res.ok) return null
    return res.json()
  } catch (err) {
    return null
  }
}

export default async function ChatDetailPage(
  searchParams: PageProps<"/[locale]/chats/[chatId]">,
) {
  const { chatId } = await searchParams.params
  const chat = await fetchChat(chatId)

  if (!chat) {
    notFound()
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 space-y-6">
        <PageHeader
          title={chat.chat_id}
          description={`Created at: ${new Date(chat.created_at).toLocaleString()}`}
        />
        <div className="mb-8">
          <Link href="/chats" className="text-sm text-primary hover:underline">
            &larr; Back to Chats
          </Link>
        </div>
        <Chat chat={chat} />
      </div>
    </div>
  )
}
