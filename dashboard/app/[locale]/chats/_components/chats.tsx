"use client"

import { getColumns, type Chat } from "./columns"
import { DataTable } from "./data-table"
import { useRouter } from "@/i18n/navigation"

export type ChatsResponse = {
  items: Chat[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface Props {
  chatsData: ChatsResponse
  page: number
  setPage: (page: number) => void
  pageSize: number
  setPageSize: (pageSize: number) => void
  sortBy: string
  setSortBy: (sortBy: string) => void
  sortOrder: "asc" | "desc"
  setSortOrder: (sortOrder: "asc" | "desc") => void
}

export default function Chats({
  chatsData,
  page,
  setPage,
  pageSize,
  setPageSize,
  sortBy,
  setSortBy,
  sortOrder,
  setSortOrder,
}: Props) {
  const router = useRouter()

  const columns = getColumns({
    sortBy,
    sortOrder,
    onSortChange: (newSortBy: string, newSortOrder: "asc" | "desc") => {
      setSortBy(newSortBy)
      setSortOrder(newSortOrder)
    },
  })

  return (
    <DataTable
      columns={columns}
      data={chatsData.items}
      pagination={{
        page,
        pageSize,
        total: chatsData.total,
        totalPages: chatsData.total_pages,
        onPageChange: setPage,
        onPageSizeChange: setPageSize,
      }}
      sorting={{
        sortBy,
        sortOrder,
        onSortChange: (newSortBy: string, newSortOrder: "asc" | "desc") => {
          setSortBy(newSortBy)
          setSortOrder(newSortOrder)
        },
      }}
      onRowClick={(chat: Chat) => {
        router.push(`/chats/${chat.chat_id}`)
      }}
    />
  )
}
