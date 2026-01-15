"use client"

import { Button } from "@/components/ui/button"
import { ColumnDef } from "@tanstack/react-table"
import { ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react"

export type Chat = {
  chat_id: string
  created_at: string
  ip?: string
  country?: string
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
      accessorKey: "ip",
      header: "IP Address",
      cell: ({ row }) => {
        const ip = row.getValue("ip") as string | undefined
        return <div>{ip || "N/A"}</div>
      },
    },
    {
      accessorKey: "country",
      header: "Country",
      cell: ({ row }) => {
        const country = row.getValue("country") as string | undefined
        return <div>{country || "N/A"}</div>
      },
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
