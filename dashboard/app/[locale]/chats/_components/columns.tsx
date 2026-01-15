"use client"

import { Button } from "@/components/ui/button"
import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react"

export type Chat = {
  chat_id: string
  created_at: string
}

interface SortingProps {
  sortBy: string
  sortOrder: "asc" | "desc"
  onSortChange: (sortBy: string, sortOrder: "asc" | "desc") => void
}

export function getColumns(sorting: SortingProps): ColumnDef<Chat>[] {
  return [
    {
      accessorKey: "chat_id",
      header: "Chat ID",
      cell: ({ row }) => (
        <div className="truncate">{row.getValue("chat_id")}</div>
      ),
    },
    {
      accessorKey: "created_at",
      header: () => {
        const isSorted = sorting.sortBy === "created_at"
        const currentOrder = isSorted ? sorting.sortOrder : null

        return (
          <Button
            variant="ghost"
            onClick={() => {
              const newOrder = currentOrder === "asc" ? "desc" : "asc"
              sorting.onSortChange("created_at", newOrder)
            }}
          >
            Created At
            {isSorted ? (
              currentOrder === "asc" ? (
                <ArrowUp className="ml-2 h-4 w-4" />
              ) : (
                <ArrowDown className="ml-2 h-4 w-4" />
              )
            ) : (
              <ArrowUpDown className="ml-2 h-4 w-4" />
            )}
          </Button>
        )
      },
      cell: ({ row }) => {
        const date = new Date(row.getValue("created_at"))
        return <div>{date.toLocaleString()}</div>
      },
    },
  ]
}
