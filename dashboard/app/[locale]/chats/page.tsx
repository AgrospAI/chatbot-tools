"use client"

import Chats from "./_components/chats"
import { PageHeader } from "@/components/page-header"
import { useExtracted } from "next-intl"
import { useEffect, useState } from "react"

export type Chat = {
  chat_id: string
  created_at: string
}

export type ChatsResponse = {
  items: Chat[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export default function ChatsPage({ params }: { params: { locale: string } }) {
  const t = useExtracted()
  const [chatsData, setChatsData] = useState<ChatsResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [sortBy, setSortBy] = useState("created_at")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")

  useEffect(() => {
    async function fetchChats() {
      setLoading(true)
      setError(null)
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          page_size: pageSize.toString(),
          sort_by: sortBy,
          sort_order: sortOrder,
        })
        const res = await fetch(`http://localhost:8000/chats?${params}`, {
          cache: "no-store",
        })
        if (!res.ok) throw new Error("Failed to fetch chats")
        const data = await res.json()
        setChatsData(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred")
      } finally {
        setLoading(false)
      }
    }
    fetchChats()
  }, [page, pageSize, sortBy, sortOrder])

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6 space-y-6">
        <PageHeader
          title={t("Chats")}
          description={t("View and manage your conversations")}
        />
        {loading && <div>Loading...</div>}
        {error && <div className="text-red-500">Error: {error}</div>}
        {chatsData && (
          <Chats
            chatsData={chatsData}
            page={page}
            setPage={setPage}
            pageSize={pageSize}
            setPageSize={setPageSize}
            sortBy={sortBy}
            setSortBy={setSortBy}
            sortOrder={sortOrder}
            setSortOrder={setSortOrder}
          />
        )}
      </div>
    </div>
  )
}
